import asyncio
import email
from email import policy
from typing import Awaitable
from collections.abc import Callable

from bs4 import Tag, BeautifulSoup


def extract_subject_from_email(email_bytes: bytes) -> str:
    msg = email.message_from_bytes(email_bytes, policy=policy.default)
    return msg.get("Subject")


def extract_html_from_email(email_bytes: bytes) -> str:
    msg = email.message_from_bytes(email_bytes, policy=policy.default)
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/html":
                return part.get_content()
    else:
        if msg.get_content_type() == "text/html":
            return msg.get_content()
    raise ValueError("Expected email to contain text/html")


async def process_wrapper(
    wrapper: Tag, fetch_summary: Callable[[str], Awaitable[str]]
) -> None:
    # Find content column
    content_before = [c for c in wrapper.children if str(c).strip() == "TITLE"]
    assert len(content_before) == 1, "Expected exactly one title comment"
    content_wrapper = content_before[0].find_next_sibling()
    assert content_wrapper.name == "div", "Expected content wrapper to be a div."

    # Fetch Summary based on contained link
    link = content_wrapper.find("a").get("href")
    summary = await fetch_summary(link)

    # Append the summary
    content_wrapper.append(BeautifulSoup(f"<p>{summary}</p>", "html.parser"))


async def process_html(
    html: str, fetch_summary: Callable[[str], Awaitable[str]]
) -> str:
    soup = BeautifulSoup(html, "html.parser")
    wrappers = [el.parent for el in soup.find_all("mj-text")]
    update_tasks = [process_wrapper(el, fetch_summary) for el in wrappers]
    await asyncio.gather(*update_tasks)
    return str(soup)
