import asyncio
import email
from email import policy
from typing import Awaitable
from collections.abc import Callable

from bs4 import BeautifulSoup, PageElement, Comment, Tag


def extract_sender_from_email(email_bytes: bytes) -> str:
    msg = email.message_from_bytes(email_bytes, policy=policy.default)
    return msg.get("From")


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
    i: int, content_wrapper: Tag, fetch_summary: Callable[[int, str], Awaitable[str]]
) -> None:
    # Fetch Summary based on contained link
    link = content_wrapper.find("a").get("href")
    summary = await fetch_summary(i, link)

    # Append the summary
    content_wrapper.append(BeautifulSoup(f"<p>{summary}</p>", "html.parser"))


def _is_title_marker(el: str | PageElement) -> bool:
    return (
        isinstance(el, Comment)
        and el.strip() == "TITLE"
        and el.find_next_sibling().name == "div"
    )


async def process_html(
    html: str, fetch_summary: Callable[[int, str], Awaitable[str]]
) -> str:
    soup = BeautifulSoup(html, "html.parser")
    wrappers = [el.find_next_sibling() for el in soup.find_all(string=_is_title_marker)]
    update_tasks = [
        process_wrapper(i, el, fetch_summary) for i, el in enumerate(wrappers)
    ]
    await asyncio.gather(*update_tasks)
    return str(soup)
