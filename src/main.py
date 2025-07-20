import asyncio
import email
from email import policy
import json
from typing import Dict, Any

from bs4 import BeautifulSoup, Tag


async def fetch_email(message_id: str) -> bytes:
    # Todo: Replace with actual implementation to fetch from S3
    with open("../sample-data/emails/" + message_id, "rb") as f:
        return f.read()


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


async def fetch_summary(link: str) -> str:
    return "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet."


async def process_wrapper(wrapper: Tag) -> None:
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


async def process_email(message_id: str) -> None:
    # Extract HTML from email
    email_bytes = await fetch_email(message_id)
    html = extract_html_from_email(email_bytes)

    # Process the HTML
    soup = BeautifulSoup(html, "html.parser")
    wrappers = [el.parent.parent for el in soup.find_all("mj-text")]
    update_tasks = [process_wrapper(el) for el in wrappers]
    await asyncio.gather(*update_tasks)
    updated_html = str(soup)

    # Send a message containing the result
    # Todo...
    print(updated_html)


def lambda_handler(event: Dict[str, Any], context: Dict[str, Any]) -> None:
    message_id = event["Records"][0]["ses"]["mail"]["messageId"]
    asyncio.run(process_email(message_id))


if __name__ == "__main__":
    with open("../sample-data/events/sample.json", "r") as f:
        event = json.load(f)
        lambda_handler(event, {})
