"""Refresh Brightspace tutorial content and its Ellucian runtime snapshot."""

from __future__ import annotations

import argparse
import html
import json
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
    "https://www.southflorida.edu/current-students/distance-learning/"
    "brightspace-tutorials"
)
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPOSITORY_ROOT / "Pages" / "BrightSpace.html"
DEFAULT_DATA_OUTPUT = REPOSITORY_ROOT / "docs" / "brightspace_tutorials.json"
HEADERS = {
    "User-Agent": (
        "SFSC-Brightspace-Tutorial-Sync/1.0 "
        "(+https://github.com/South-Florida-State-College/experience-ellucian)"
    )
}


@dataclass(frozen=True)
class TutorialSection:
    title: str
    description: str
    links: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class BrightspaceContent:
    intro_before_email: str
    email_label: str
    intro_after_email: str
    email: str
    phone: str
    student: TutorialSection
    instructor: TutorialSection


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


def normalized_text(node: Tag) -> str:
    return " ".join(node.get_text(" ", strip=True).split())


def find_heading(content: Tag, title: str) -> Tag:
    for heading in content.find_all("h2"):
        heading_text = normalized_text(heading)
        if heading_text.casefold().startswith(title.casefold()):
            return heading
    raise RuntimeError(f"The {title!r} heading was not found")


def parse_tutorial_section(content: Tag, title: str) -> TutorialSection:
    heading = find_heading(content, title)
    description_node = heading.find_next("p")
    link_list = heading.find_next("ul")
    if description_node is None or link_list is None:
        raise RuntimeError(f"The {title!r} tutorial content is incomplete")

    links: list[tuple[str, str]] = []
    seen: set[str] = set()
    for item in link_list.find_all("li", recursive=False):
        link = item.find("a", href=True)
        if link is None:
            continue
        label = normalized_text(link)
        href = absolute_url(link["href"])
        if not label or href in seen:
            continue
        seen.add(href)
        links.append((label, href))

    if not 5 <= len(links) <= 50:
        raise RuntimeError(
            f"Found {len(links)} {title.lower()} links; expected between 5 and 50"
        )
    return TutorialSection(
        title=title,
        description=normalized_text(description_node),
        links=tuple(links),
    )


def parse_source(source_html: str) -> BrightspaceContent:
    soup = BeautifulSoup(source_html, "html.parser")
    content = soup.select_one(".subpageContent .col-md-9.col-sm-8")
    if content is None:
        raise RuntimeError("The Brightspace tutorial content container was not found")

    intro = content.select_one("#mainContent_fv_PageContent_p_t_Std")
    if intro is None:
        intro = next(
            (
                paragraph
                for paragraph in content.find_all("p")
                if paragraph.find("a", href=re.compile(r"^mailto:", re.I))
            ),
            None,
        )
    email_link = intro.find("a", href=re.compile(r"^mailto:", re.I)) if intro else None
    if intro is None or email_link is None:
        raise RuntimeError("The Brightspace introduction or support email was not found")

    intro_text = normalized_text(intro)
    email_label = normalized_text(email_link)
    label_index = intro_text.find(email_label)
    if label_index < 0:
        raise RuntimeError("The Brightspace support label was not found in the introduction")
    intro_before_email = intro_text[:label_index]
    intro_after_email = intro_text[label_index + len(email_label) :]
    intro_after_email = re.sub(r"\s+([.,;:!?])", r"\1", intro_after_email)
    email = email_link["href"].split(":", 1)[1].strip()
    phone_match = re.search(r"\b\d{3}-\d{3}-\d{4}\b", intro_text)
    if "@" not in email or phone_match is None:
        raise RuntimeError("The Brightspace support contact information is incomplete")

    student = parse_tutorial_section(content, "Student Tutorials")
    instructor = parse_tutorial_section(content, "Instructor Tutorials")
    return BrightspaceContent(
        intro_before_email=intro_before_email,
        email_label=email_label,
        intro_after_email=intro_after_email,
        email=email,
        phone=phone_match.group(0),
        student=student,
        instructor=instructor,
    )


def render_intro(source: BrightspaceContent) -> str:
    return (
        '<div class="intro-section">\n'
        f'    <p>{html.escape(source.intro_before_email)}'
        f'<a href="mailto:{html.escape(source.email, quote=True)}">'
        f'{html.escape(source.email_label)}</a>'
        f'{html.escape(source.intro_after_email)}</p>\n'
        f'    <a class="contact-btn" href="mailto:{html.escape(source.email, quote=True)}">'
        'Support</a>\n'
        '</div>'
    )


def render_tutorial_section(section: TutorialSection, section_id: str) -> str:
    items = "\n".join(
        f'        <li><a href="{html.escape(href, quote=True)}" target="_blank" '
        f'rel="noopener noreferrer">{html.escape(label)}</a></li>'
        for label, href in section.links
    )
    return (
        f'<section aria-labelledby="{section_id}">\n'
        f'    <h2 id="{section_id}">{html.escape(section.title)}</h2>\n'
        f'    <p>{html.escape(section.description)}</p>\n'
        f'    <ul>\n{items}\n    </ul>\n'
        '</section>'
    )


def render_contact(source: BrightspaceContent) -> str:
    return (
        '<div id="contact-section" role="contentinfo">\n'
        '    <h2>Contact Us</h2>\n'
        '    <p>Need help? Reach out to the Office of Educational Technology!</p>\n'
        f'    <p>Email: <a href="mailto:{html.escape(source.email, quote=True)}">'
        f'{html.escape(source.email)}</a></p>\n'
        f'    <p>Phone: <a href="tel:{html.escape(source.phone, quote=True)}">'
        f'{html.escape(source.phone)}</a></p>\n'
        '</div>'
    )


def render_sections(source: BrightspaceContent) -> dict[str, str]:
    return {
        "brightspace-intro": render_intro(source),
        "brightspace-student": render_tutorial_section(
            source.student, "student-tutorials"
        ),
        "brightspace-instructor": render_tutorial_section(
            source.instructor, "instructor-tutorials"
        ),
        "brightspace-contact": render_contact(source),
    }


def build_payload(source: BrightspaceContent) -> dict[str, object]:
    return {
        "schema_version": 1,
        "source_url": SOURCE_URL,
        "sections": render_sections(source),
    }


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


def update_document(document: str, source: BrightspaceContent) -> str:
    for name, replacement in render_sections(source).items():
        document = replace_section(document, name, replacement)
    return document


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--data-output", type=Path, default=DEFAULT_DATA_OUTPUT)
    parser.add_argument("--source-file", type=Path)
    parser.add_argument("--check", action="store_true")
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
    data_output = args.data_output.resolve()
    current = output.read_text(encoding="utf-8")
    updated = update_document(current, source)
    payload = json.dumps(
        build_payload(source), ensure_ascii=False, indent=2, sort_keys=True
    ) + "\n"
    current_payload = (
        data_output.read_text(encoding="utf-8") if data_output.exists() else None
    )

    html_changed = updated != current
    data_changed = payload != current_payload
    if not html_changed and not data_changed:
        print(f"{output} and {data_output} are already current")
        return 0
    if args.check:
        changed = []
        if html_changed:
            changed.append(str(output))
        if data_changed:
            changed.append(str(data_output))
        print(f"Needs refresh: {', '.join(changed)}", file=sys.stderr)
        return 1

    if html_changed:
        output.write_text(updated, encoding="utf-8", newline="\n")
    if data_changed:
        data_output.parent.mkdir(parents=True, exist_ok=True)
        data_output.write_text(payload, encoding="utf-8", newline="\n")
    print(
        f"Updated Brightspace HTML/JSON with {len(source.student.links)} student "
        f"and {len(source.instructor.links)} instructor tutorials"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
