"""Synchronize the SFSC website employee directory to a CSV file."""

from __future__ import annotations

import argparse
import csv
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


DIRECTORY_URL = "https://www.southflorida.edu/faculty-staff/employee-directory"
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "docs" / "employee_directory.csv"
HEADERS = {
    "User-Agent": "SFSC-Employee-Directory-Sync/1.0 (+https://github.com/South-Florida-State-College/experience-ellucian)"
}
CSV_FIELDS = ["Name", "Title", "Department", "Email", "Phone"]


def create_session() -> requests.Session:
    session = requests.Session()
    retries = Retry(
        total=4,
        backoff_factor=1,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.headers.update(HEADERS)
    return session


def get_soup(session: requests.Session, url: str) -> BeautifulSoup:
    response = session.get(url, timeout=30)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def profile_details(session: requests.Session, url: str) -> tuple[str, str, str]:
    """Return the full website position, email, and phone for a profile."""
    soup = get_soup(session, url)
    position_node = soup.select_one(".tshowcase-single-position")
    email_node = soup.select_one(".tshowcase-single-email a[href^='mailto:']")
    phone_node = soup.select_one(".tshowcase-single-telephone")

    position = position_node.get_text(" ", strip=True) if position_node else ""
    email = ""
    if email_node:
        email = email_node.get("href", "").removeprefix("mailto:").strip()
        if not email:
            email = email_node.get_text(" ", strip=True)
    phone = phone_node.get_text(" ", strip=True) if phone_node else ""
    return position, email, phone


def split_position(position: str, previous: dict[str, str]) -> tuple[str, str]:
    """Split the website's combined position into the CSV title and department."""
    position = position.strip()
    previous_title = previous.get("Title", "").strip()
    previous_department = previous.get("Department", "").strip()

    # Existing hand-curated titles sometimes contain commas. Reuse that boundary
    # when the current website value still begins with the same title.
    if previous_title and position.casefold().startswith((previous_title + ",").casefold()):
        return position[: len(previous_title)], position[len(previous_title) + 1 :].strip()

    if "," in position:
        title, department = position.split(",", 1)
        return title.strip(), department.strip()

    return position, previous_department or "N/A"


def read_existing_csv(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        return {
            row.get("Name", "").strip().casefold(): row
            for row in csv.DictReader(csv_file)
            if row.get("Name", "").strip()
        }


def scrape_directory(
    session: requests.Session, existing: dict[str, dict[str, str]]
) -> list[dict[str, str]]:
    employees: list[dict[str, str]] = []
    seen_profiles: set[str] = set()
    page_url: str | None = DIRECTORY_URL
    page_number = 0

    while page_url:
        page_number += 1
        if page_number > 100:
            raise RuntimeError("Directory pagination exceeded the 100-page safety limit")

        print(f"Scraping directory page {page_number}: {page_url}")
        soup = get_soup(session, page_url)
        rows = soup.select("table.tshowcase-box-table tr.ts-align-left")
        if not rows:
            raise RuntimeError(f"No employee rows found on {page_url}")

        for row in rows:
            columns = row.find_all("td")
            if len(columns) < 3:
                continue

            name_link = columns[0].find("a", href=True)
            name = columns[0].get_text(" ", strip=True)
            profile_url = urljoin(DIRECTORY_URL, name_link["href"]) if name_link else ""
            if not name or (profile_url and profile_url in seen_profiles):
                continue

            previous = existing.get(name.casefold(), {})
            position = columns[1].get_text(" ", strip=True)
            title, department = split_position(position, previous)
            phone = columns[2].get_text(" ", strip=True)
            if profile_url:
                seen_profiles.add(profile_url)

            employees.append(
                {
                    "Name": name,
                    "Title": title,
                    "Department": department,
                    "Email": previous.get("Email", "").strip(),
                    "Phone": phone or previous.get("Phone", "").strip(),
                    "_profile_url": profile_url,
                }
            )

        next_link = soup.find("a", string=lambda value: value and "Next Page" in value)
        page_url = urljoin(page_url, next_link["href"]) if next_link and next_link.get("href") else None

    # Use a modest worker count so a full sync finishes promptly without placing
    # excessive concurrent load on the college website.
    print(f"Reading {len(employees)} employee profiles")
    profile_error_count = 0
    with ThreadPoolExecutor(max_workers=6) as executor:
        pending = {
            executor.submit(profile_details, session, employee["_profile_url"]): employee
            for employee in employees
            if employee["_profile_url"]
        }
        for future in as_completed(pending):
            employee = pending[future]
            try:
                profile_title, email, profile_phone = future.result()
                if profile_title:
                    employee["Title"], employee["Department"] = split_position(
                        profile_title, employee
                    )
                employee["Email"] = email or employee["Email"]
                employee["Phone"] = profile_phone or employee["Phone"]
            except requests.RequestException:
                # Keep the list-page data if one profile is temporarily unavailable.
                # Do not log the profile URL or exception because they can contain
                # private request data.
                profile_error_count += 1

    if profile_error_count:
        print(
            f"Warning: {profile_error_count} employee profiles could not be read",
            file=sys.stderr,
        )

    employees.sort(key=lambda employee: employee["Name"].casefold())
    return employees


def write_csv(employees: list[dict[str, str]], output: Path) -> None:
    # A small or empty result almost certainly means the website markup changed.
    # Fail safely instead of replacing the working directory with bad data.
    if len(employees) < 50:
        raise RuntimeError(f"Only {len(employees)} employees were found; refusing to replace {output}")

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary_output = output.with_suffix(output.suffix + ".tmp")
    with temporary_output.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(
            {field: employee.get(field, "") for field in CSV_FIELDS}
            for employee in employees
        )
    temporary_output.replace(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    output = args.output.resolve()
    existing = read_existing_csv(output)
    with create_session() as session:
        employees = scrape_directory(session, existing)
    write_csv(employees, output)
    print(f"Saved {len(employees)} employees to {args.output.resolve()}")


if __name__ == "__main__":
    main()
