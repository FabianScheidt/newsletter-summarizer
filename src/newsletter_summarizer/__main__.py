import asyncio
import json
import pathlib
from typing import Dict, Any

from aiobotocore.session import get_session

from newsletter_summarizer.s3 import (
    fetch_raw_email,
    store_html_input,
    store_html_output,
)
from newsletter_summarizer.processing import extract_html_from_email, process_html

session = get_session()


async def fetch_summary(link: str) -> str:
    return "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet."


async def process_email(message_id: str) -> None:
    async with session.create_client("s3") as s3:
        # Extract HTML from email
        email_bytes = await fetch_raw_email(s3, message_id)
        html = extract_html_from_email(email_bytes)
        await store_html_input(s3, message_id, html)

        # Process the HTML
        updated_html = await process_html(html, fetch_summary)
        await store_html_output(s3, message_id, updated_html)

        # Send a message containing the result
        # Todo...
        print(updated_html)


def lambda_handler(event: Dict[str, Any], context: Dict[str, Any]) -> None:
    message_id = event["Records"][0]["ses"]["mail"]["messageId"]
    asyncio.run(process_email(message_id))


if __name__ == "__main__":
    dir = pathlib.Path(__file__).parent.resolve()
    with open(dir / "../../sample-data/events/sample.json", "r") as f:
        event = json.load(f)
        lambda_handler(event, {})
