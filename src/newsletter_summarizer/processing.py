import asyncio
import email
from email import policy
from typing import Awaitable
from collections.abc import Callable

from bs4 import BeautifulSoup, Tag


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
    i: int, article_wrapper: Tag, fetch_summary: Callable[[int, str], Awaitable[str]]
) -> None:
    # Fetch Summary based on contained link
    content_wrapper = article_wrapper.find_all("td")[2]
    link = content_wrapper.find("a").get("href")
    summary = await fetch_summary(i, link)

    # Append the summary
    content_wrapper.append(BeautifulSoup(f"<p>{summary}</p>", "html.parser"))


def _is_article_wrapper(el: Tag) -> bool:
    if el.name != "tr":
        return False
    tds = el.find_all("td")
    if len(tds) != 3:
        return False
    img_td, spacer_td, title_td = tds
    return (
        img_td.find("img") is not None
        and spacer_td.attrs.get("width") is not None
        and title_td.find("a") is not None
    )


async def process_html(
    html: str, fetch_summary: Callable[[int, str], Awaitable[str]]
) -> str:
    soup = BeautifulSoup(html, "html.parser")
    wrappers = soup.find_all(_is_article_wrapper)
    update_tasks = [
        process_wrapper(i, el, fetch_summary) for i, el in enumerate(wrappers)
    ]
    await asyncio.gather(*update_tasks)
    return str(soup)
