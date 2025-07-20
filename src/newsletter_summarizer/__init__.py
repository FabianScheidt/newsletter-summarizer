import asyncio
from typing import Dict, Any

from aiobotocore.session import get_session

from newsletter_summarizer.s3 import (
    fetch_raw_email,
    store_html_input,
    store_html_output,
    store_article_text,
    store_article_html,
)
from newsletter_summarizer.processing import (
    extract_html_from_email,
    process_html,
    extract_subject_from_email,
)
from newsletter_summarizer.crawling import fetch_html, login
from newsletter_summarizer.extraction import extract_article
from newsletter_summarizer.submission import submit_result
from newsletter_summarizer.summary import summarize

session = get_session()


async def process_email(message_id: str) -> None:
    async with (
        session.create_client("s3") as s3,
        session.create_client("bedrock-runtime") as bedrock,
    ):
        # Extract HTML from email
        email_bytes = await fetch_raw_email(s3, message_id)
        subject = extract_subject_from_email(email_bytes)
        html = extract_html_from_email(email_bytes)
        await store_html_input(s3, message_id, html)

        # Define handling for processing articles
        async def fetch_summary(link: str) -> str:
            fetched_html = await fetch_html(link)
            extracted_article = extract_article(fetched_html)

            await store_article_html(s3, extracted_article["id"], fetched_html)
            await store_article_text(s3, extracted_article["id"], extracted_article)

            summary = await summarize(bedrock, extracted_article["text"])

            return summary

        # Initiate the crawler and process the HTML
        await login()
        updated_html = await process_html(html, fetch_summary)
        await store_html_output(s3, message_id, updated_html)

    async with session.create_client("ses") as ses:
        # Send a message containing the result
        await submit_result(ses, subject, updated_html)


def lambda_handler(event: Dict[str, Any], context: Dict[str, Any]) -> None:
    message_id = event["Records"][0]["ses"]["mail"]["messageId"]
    asyncio.run(process_email(message_id))
