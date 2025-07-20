import os

from aiobotocore.client import AioBaseClient

SENDER = os.environ["NEWSLETTER_SUMMARIZER_SENDER"]
RECIPIENT = os.environ["NEWSLETTER_SUMMARIZER_RECIPIENT"]


async def submit_result(ses: AioBaseClient, subject: str, html: str) -> None:
    await ses.send_email(
        Source=SENDER,
        Destination={"ToAddresses": [RECIPIENT]},
        Message={
            "Subject": {"Data": subject, "Charset": "utf-8"},
            "Body": {
                "Html": {"Data": html, "Charset": "utf-8"},
            },
        },
    )
