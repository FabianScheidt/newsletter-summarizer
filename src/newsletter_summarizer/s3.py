import json
import os

from aiobotocore.client import AioBaseClient

from newsletter_summarizer.extraction import ExtractedArticle
from newsletter_summarizer.summary import SummaryLog

bucket = os.environ["NEWSLETTER_SUMMARIZER_BUCKET"]


async def fetch_raw_email(s3: AioBaseClient, message_id: str) -> bytes:
    key = "emails/raw/" + message_id
    res = await s3.get_object(Bucket=bucket, Key=key)
    return await res["Body"].read()


async def store_html_input(s3: AioBaseClient, message_id: str, html: str) -> None:
    key = f"emails/html-input/{message_id}.html"
    await s3.put_object(Bucket=bucket, Key=key, Body=html.encode("utf-8"))


async def store_html_output(s3: AioBaseClient, message_id: str, html: str) -> None:
    key = f"emails/html-output/{message_id}.html"
    await s3.put_object(Bucket=bucket, Key=key, Body=html.encode("utf-8"))


async def store_article_html(s3: AioBaseClient, article_id: str, html: str) -> None:
    key = f"articles/html/{article_id}.html"
    await s3.put_object(Bucket=bucket, Key=key, Body=html.encode("utf-8"))


async def store_article_text(
    s3: AioBaseClient, article_id: str, extracted_article: ExtractedArticle
) -> None:
    key = f"articles/text/{article_id}.json"
    await s3.put_object(Bucket=bucket, Key=key, Body=_json_dump(extracted_article))


async def store_article_summary(
    s3: AioBaseClient, article_id: str, summary_log: SummaryLog
) -> None:
    key = f"articles/summary/{article_id}.json"
    await s3.put_object(Bucket=bucket, Key=key, Body=_json_dump(summary_log))


def _json_dump(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False).encode("utf8")
