import asyncio
import logging
import os
from typing import Dict, Any

from aiobotocore.session import get_session

from newsletter_summarizer.s3 import (
    fetch_raw_email,
    store_html_input,
    store_html_output,
    store_article_text,
    store_article_html,
    store_article_summary,
)
from newsletter_summarizer.processing import (
    extract_sender_from_email,
    extract_html_from_email,
    process_html,
    extract_subject_from_email,
)
from newsletter_summarizer.crawling import fetch_html, login
from newsletter_summarizer.extraction import extract_article
from newsletter_summarizer.submission import submit_result
from newsletter_summarizer.summary import summarize

logger = logging.getLogger(__name__)
session = get_session()


async def process_email(message_id: str) -> None:
    logger.info(f"Processing email {message_id}...")

    async with (
        session.create_client("s3") as s3,
        session.create_client(
            "bedrock-runtime",
            region_name=os.environ.get("NEWSLETTER_SUMMARIZER_BEDROCK_REGION"),
        ) as bedrock,
    ):
        # Extract HTML from email
        logger.info(f"Extracting content {message_id}...")
        email_bytes = await fetch_raw_email(s3, message_id)
        sender = extract_sender_from_email(email_bytes)
        subject = extract_subject_from_email(email_bytes)
        html = extract_html_from_email(email_bytes)
        await store_html_input(s3, message_id, html)

        # Define handling for processing articles
        async def fetch_summary(i: int, link: str) -> str:
            logger.info(f"Processing article with index {i} at {link}...")
            fetched_html = await fetch_html(link)
            extracted_article = extract_article(fetched_html)

            await store_article_html(s3, extracted_article["id"], fetched_html)
            await store_article_text(s3, extracted_article["id"], extracted_article)

            text = extracted_article["text"] or extracted_article["description"]
            logger.info(
                f"Fetching summary for article with index {i}: {extracted_article["title"]}"
            )
            summary, summary_log = await summarize(bedrock, text)
            await store_article_summary(s3, extracted_article["id"], summary_log)

            return summary

        # Initiate the crawler and process the HTML
        logger.info(f"Logging in {message_id}...")
        await login()
        logger.info(f"Processing HTML {message_id}...")
        updated_html = await process_html(html, fetch_summary)
        await store_html_output(s3, message_id, updated_html)

    async with session.create_client("ses") as ses:
        # Send a message containing the result
        logger.info("Sending updated email...")
        await submit_result(ses, sender, subject, updated_html)

    logger.info("Done!")


def lambda_handler(event: Dict[str, Any], context: Dict[str, Any]) -> None:
    message_id = event["Records"][0]["ses"]["mail"]["messageId"]
    logger.info(f"Processing message {message_id}...")
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(process_email(message_id))
