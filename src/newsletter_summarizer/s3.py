import os

from aiobotocore.client import AioBaseClient

bucket = os.environ["NEWSLETTER_SUMMARIZER_BUCKET"]


async def fetch_raw_email(s3: AioBaseClient, message_id: str) -> bytes:
    key = "emails/raw/" + message_id
    res = await s3.get_object(Bucket=bucket, Key=key)
    return await res["Body"].read()


async def store_html_input(s3: AioBaseClient, message_id: str, html: str) -> None:
    key = f"emails/html-input/{message_id}.html"
    await s3.put_object(Bucket=bucket, Key=key, Body=html)


async def store_html_output(s3: AioBaseClient, message_id: str, html: str) -> None:
    key = f"emails/html-output/{message_id}.html"
    await s3.put_object(Bucket=bucket, Key=key, Body=html)
