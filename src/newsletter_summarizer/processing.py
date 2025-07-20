import asyncio
import email
from email import policy
from typing import Awaitable
from collections.abc import Callable

from bs4 import Tag, BeautifulSoup


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
    assert wrapper.name == "tr", "Expected wrapping element to be a table row."
    children = wrapper.find_all("td")
    assert len(children) == 3, "Expected wrapping element to contain three columns."
    content_col = children[2]
    content_wrapper = content_col.find("div")

    # Fetch Summary based on contained link
    link = content_wrapper.find("a").get("href")
    summary = await fetch_summary(link)

    # Append the summary
    content_wrapper.append(BeautifulSoup(f"<p>{summary}</p>", "html.parser"))


async def process_html(
    html: str, fetch_summary: Callable[[str], Awaitable[str]]
) -> str:
    soup = BeautifulSoup(html, "html.parser")
    wrappers = [el.parent.parent for el in soup.find_all("mj-text")]
    update_tasks = [process_wrapper(el, fetch_summary) for el in wrappers]
    await asyncio.gather(*update_tasks)
    return str(soup)
