"""Refresh source-owned Corporate Education sections in Pages/community.html."""

from __future__ import annotations

import argparse
import html
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup, Tag
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


SOURCE_URL = (
    "https://www.southflorida.edu/current-students/degrees-programs/"
    "special-programs/corporate-education-training"
)
DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "Pages" / "community.html"
HEADERS = {
    "User-Agent": (
        "SFSC-Corporate-Education-Sync/1.0 "
        "(+https://github.com/South-Florida-State-College/experience-ellucian)"
    )
}
CATEGORY_LABELS = {
    "business": "Business and Computers",
    "education": "Education",
    "health": "Health and Public Safety",
    "personal": "Personal Interest",
    "real-estate": "Real Estate",
    "technical": "Technical and Industrial",
    "workforce": "Workforce Solutions",
    "other": "Other",
}


@dataclass(frozen=True)
class Catalog:
    href: str
    image: str
    alt: str
    category: str


@dataclass(frozen=True)
class SourceContent:
    navigation: tuple[tuple[str, str], ...]
    banner_lead: str
    banner_link_href: str
    banner_link_text: str
    banner_tail: str
    banner_notice: str
    catalogs: tuple[Catalog, ...]
    introductions: tuple[str, ...]
    sections: tuple[tuple[str, tuple[str, ...]], ...]
    contact_lines: tuple[str, ...]
    contact_email: str


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


def absolute_url(value: str) -> str:
    url = urljoin(SOURCE_URL, value.strip())
    parts = urlsplit(url)
    if parts.hostname == "www.southflorida.edu" and parts.scheme == "http":
        parts = parts._replace(scheme="https")
    return urlunsplit(parts)


def classify_catalog(text: str) -> str:
    value = text.casefold().replace("corporate education", "")
    rules = (
        (
            "technical",
            (
                "cdl",
                "transport",
                "construction",
                "utility",
                "industrial",
                "manufacturing",
                "miner",
                "msha",
                "trade",
                "welding",
            ),
        ),
        ("health", ("health", "public safety", "medical", "nursing")),
        ("real-estate", ("real estate",)),
        ("workforce", ("workforce", "fast-track", "fast track")),
        ("personal", ("personal interest", "enrichment")),
        ("education", ("educator", "education", "teacher")),
        ("business", ("business", "computer", "professional development")),
    )
    for category, keywords in rules:
        if any(keyword in value for keyword in keywords):
            return category
    return "other"


def direct_text(node: Tag) -> str:
    return " ".join(node.get_text(" ", strip=True).split())


def parse_source(source_html: str) -> SourceContent:
    soup = BeautifulSoup(source_html, "html.parser")
    content = soup.select_one(".subpageContent .col-md-9.col-sm-8")
    if content is None:
        raise RuntimeError("The Corporate Education content container was not found")

    nav_nodes = soup.select(".subpageContent .sideNav > li.pagenav > ul > li")
    navigation: list[tuple[str, str]] = []
    for item in nav_nodes:
        link = item.find("a", href=True, recursive=False)
        if link:
            navigation.append((direct_text(link), absolute_url(link["href"])))
    if not 10 <= len(navigation) <= 30:
        raise RuntimeError(
            f"Found {len(navigation)} navigation links; expected between 10 and 30"
        )

    tables = content.find_all("table")
    if len(tables) < 2:
        raise RuntimeError("The expected banner and catalog tables were not found")

    banner_table = tables[0]
    banner_rows = banner_table.find_all("tr")
    if len(banner_rows) < 2:
        raise RuntimeError("The Corporate Education banner is missing a row")
    banner_cell = banner_rows[0].find(["td", "th"])
    banner_link = banner_rows[0].find("a", href=True)
    if banner_cell is None or banner_link is None:
        raise RuntimeError("The Corporate Education banner link was not found")
    banner_text = direct_text(banner_cell)
    banner_link_text = direct_text(banner_link)
    link_index = banner_text.find(banner_link_text)
    if link_index < 0:
        raise RuntimeError("The banner link text could not be located in the banner")
    banner_lead = banner_text[:link_index]
    banner_tail = banner_text[link_index + len(banner_link_text) :]
    banner_tail = re.sub(r"\s+([.,;:!?])", r"\1", banner_tail)
    activation_match = re.search(r"\s+(Use Activation Code:.*)$", banner_tail)
    if activation_match:
        banner_tail = (
            banner_tail[: activation_match.start()].rstrip()
            + "<br><span>"
            + html.escape(activation_match.group(1))
            + "</span>"
        )
    else:
        banner_tail = html.escape(banner_tail)

    banner_notice = direct_text(banner_rows[1])
    if not banner_notice:
        raise RuntimeError("The Corporate Education banner notice is empty")

    # WordPress currently lays the covers out in one table, but editors may add
    # another row or table. Read every table containing a PDF-linked image so a
    # newly added catalog is picked up without a code change.
    catalog_tables = [
        table
        for table in tables[1:]
        if any(
            urlsplit(absolute_url(link.get("href", ""))).path.casefold().endswith(
                ".pdf"
            )
            for link in table.select("a[href]")
            if link.find("img") is not None
        )
    ]
    if not catalog_tables:
        raise RuntimeError("The Corporate Education catalog table was not found")

    catalogs: list[Catalog] = []
    seen_catalogs: set[tuple[str, str]] = set()
    for catalog_table in catalog_tables:
        for image in catalog_table.select("a[href] img"):
            link = image.find_parent("a", href=True)
            if link is None:
                continue
            href = absolute_url(link.get("href", ""))
            raw_image_url = (
                image.get("data-lazy-src")
                or image.get("data-src")
                or image.get("src")
                or ""
            )
            image_url = absolute_url(raw_image_url) if raw_image_url else ""
            if not urlsplit(href).path.casefold().endswith(".pdf") or not image_url:
                continue
            key = (href, image_url)
            if key in seen_catalogs:
                continue
            seen_catalogs.add(key)
            alt = (
                " ".join(image.get("alt", "").split())
                or "Corporate Education catalog"
            )
            catalog_identity = " ".join(
                (
                    alt,
                    urlsplit(href).path.rsplit("/", 1)[-1],
                    urlsplit(image_url).path.rsplit("/", 1)[-1],
                )
            )
            catalogs.append(
                Catalog(
                    href=href,
                    image=image_url,
                    alt=alt,
                    category=classify_catalog(catalog_identity),
                )
            )
    if not 3 <= len(catalogs) <= 50:
        raise RuntimeError(
            f"Found {len(catalogs)} catalogs; expected between 3 and 50"
        )

    first_heading = content.find("h2", string=lambda value: value and value.strip())
    if first_heading is None:
        raise RuntimeError("No Corporate Education section headings were found")

    introductions: list[str] = []
    for node in catalog_tables[-1].next_siblings:
        if node is first_heading:
            break
        if isinstance(node, Tag) and node.name == "p":
            text = direct_text(node)
            if text:
                introductions.append(text)
    if len(introductions) < 2:
        raise RuntimeError("Too few Corporate Education introduction paragraphs were found")

    expected_sections = ("Continuing Education", "Customized Training", "Contract Training")
    sections: list[tuple[str, tuple[str, ...]]] = []
    for title in expected_sections:
        heading = content.find("h2", string=lambda value: value and value.strip() == title)
        item_list = heading.find_next_sibling("ul") if heading else None
        items = tuple(direct_text(item) for item in item_list.find_all("li", recursive=False)) if item_list else ()
        if not items:
            raise RuntimeError(f"The {title!r} list was not found or is empty")
        sections.append((title, items))

    contact_heading = content.find(
        ["h2", "h3"], string=lambda value: value and "Contact us" in value
    )
    contact = contact_heading.find_next_sibling("p") if contact_heading else None
    email_link = contact.find("a", href=re.compile(r"^mailto:", re.I)) if contact else None
    if contact is None or email_link is None:
        raise RuntimeError("The Corporate Education contact information was not found")
    contact_lines = tuple(" ".join(value.split()) for value in contact.stripped_strings)
    contact_email = email_link["href"].split(":", 1)[1].strip()
    contact_lines = tuple(
        value
        for value in contact_lines
        if value.casefold() not in {"email:", contact_email.casefold()}
    )
    if len(contact_lines) < 5 or "@" not in contact_email:
        raise RuntimeError("The Corporate Education contact information is incomplete")

    return SourceContent(
        navigation=tuple(navigation),
        banner_lead=banner_lead,
        banner_link_href=absolute_url(banner_link["href"]),
        banner_link_text=banner_link_text,
        banner_tail=banner_tail,
        banner_notice=banner_notice,
        catalogs=tuple(catalogs),
        introductions=tuple(introductions),
        sections=tuple(sections),
        contact_lines=contact_lines,
        contact_email=contact_email,
    )


def render_navigation(source: SourceContent) -> str:
    return "\n".join(
        f'<li><a href="{html.escape(href, quote=True)}">{html.escape(label)}</a></li>'
        for label, href in source.navigation
    )


def render_banner(source: SourceContent) -> str:
    return (
        '<div class="banner">\n'
        '    <p style="font-size: 16pt;">'
        f'{html.escape(source.banner_lead)}'
        f'<a href="{html.escape(source.banner_link_href, quote=True)}">'
        f'{html.escape(source.banner_link_text)}</a>'
        f'{source.banner_tail}</p>\n'
        f'    <p>{html.escape(source.banner_notice)}</p>\n'
        '</div>'
    )


def render_catalogs(source: SourceContent) -> str:
    categories = {catalog.category for catalog in source.catalogs}
    options = ['<option value="all">All Catalogs</option>']
    for category, label in CATEGORY_LABELS.items():
        if category in categories:
            options.append(
                f'<option value="{category}">{html.escape(label)}</option>'
            )
    option_html = "\n".join(f"        {option}" for option in options)

    items = []
    for catalog in source.catalogs:
        items.append(
            f'<div class="catalog-item" data-category="{catalog.category}">\n'
            f'    <a href="{html.escape(catalog.href, quote=True)}" '
            'target="_blank" rel="noopener noreferrer">\n'
            f'        <img src="{html.escape(catalog.image, quote=True)}" '
            f'alt="{html.escape(catalog.alt, quote=True)}">\n'
            '    </a>\n'
            '</div>'
        )
    item_html = "\n".join("    " + item.replace("\n", "\n    ") for item in items)
    return (
        '<div class="filter-container">\n'
        '    <label for="catalogFilter" class="visually-hidden">Filter catalogs</label>\n'
        '    <select id="catalogFilter" onchange="filterCatalogs()">\n'
        f'{option_html}\n'
        '    </select>\n'
        '</div>\n\n'
        '<div class="catalog-grid" id="catalogGrid">\n'
        f'{item_html}\n'
        '</div>'
    )


def render_corporate_copy(source: SourceContent) -> str:
    blocks = ["<h2>Corporate Education</h2>"]
    blocks.extend(
        f"<p>{html.escape(paragraph)}</p>" for paragraph in source.introductions
    )
    for title, items in source.sections:
        blocks.append(f"<h3>{html.escape(title)}</h3>")
        list_items = "\n".join(f"    <li>{html.escape(item)}</li>" for item in items)
        blocks.append(f"<ul>\n{list_items}\n</ul>")
    return "\n\n".join(blocks)


def render_contact(source: SourceContent) -> str:
    lines = [html.escape(line) for line in source.contact_lines]
    lines.append(
        'Email (Corporate Education): '
        f'<a href="mailto:{html.escape(source.contact_email, quote=True)}">'
        f'{html.escape(source.contact_email)}</a>'
    )
    lines.append(
        'Email (Community Education): '
        '<a href="mailto:communityeducation@southflorida.edu">'
        'communityeducation@southflorida.edu</a>'
    )
    return '<div class="contact-info">\n    <p>' + "<br>\n    ".join(lines) + "</p>\n</div>"


def replace_section(document: str, name: str, replacement: str) -> str:
    pattern = re.compile(
        rf"^(?P<indent>[ \t]*)<!-- BEGIN AUTO-SYNC: {re.escape(name)} -->.*?"
        rf"^[ \t]*<!-- END AUTO-SYNC: {re.escape(name)} -->",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(document)
    if match is None:
        raise RuntimeError(f"The {name!r} auto-sync markers were not found")
    indent = match.group("indent")
    indented = "\n".join(
        indent + line if line else "" for line in replacement.splitlines()
    )
    block = (
        f"{indent}<!-- BEGIN AUTO-SYNC: {name} -->\n"
        f"{indented}\n"
        f"{indent}<!-- END AUTO-SYNC: {name} -->"
    )
    return document[: match.start()] + block + document[match.end() :]


def update_document(document: str, source: SourceContent) -> str:
    sections = (
        ("corporate-navigation", render_navigation(source)),
        ("corporate-banner", render_banner(source)),
        ("corporate-catalogs", render_catalogs(source)),
        ("corporate-copy", render_corporate_copy(source)),
        ("corporate-contact", render_contact(source)),
    )
    for name, replacement in sections:
        document = replace_section(document, name, replacement)
    return document


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--source-file", type=Path)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report whether an update is needed without writing the output file",
    )
    args = parser.parse_args()

    if args.source_file:
        source_html = args.source_file.read_text(encoding="utf-8")
    else:
        with create_session() as session:
            response = session.get(SOURCE_URL, timeout=30)
            response.raise_for_status()
            source_html = response.text

    source = parse_source(source_html)
    output = args.output.resolve()
    current = output.read_text(encoding="utf-8")
    updated = update_document(current, source)
    if updated == current:
        print(f"{output} is already current")
        return 0
    if args.check:
        print(f"{output} needs to be refreshed", file=sys.stderr)
        return 1
    output.write_text(updated, encoding="utf-8", newline="\n")
    print(
        f"Updated {output} with {len(source.navigation)} links and "
        f"{len(source.catalogs)} catalogs"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
