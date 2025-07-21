import os
import re

from aiobotocore.client import AioBaseClient

SENDER = os.environ["NEWSLETTER_SUMMARIZER_SENDER"]
RECIPIENT = os.environ["NEWSLETTER_SUMMARIZER_RECIPIENT"]


async def submit_result(
    ses: AioBaseClient, original_sender: str, subject: str, html: str
) -> None:
    await ses.send_email(
        Source=_assemble_sender(original_sender),
        Destination={"ToAddresses": [RECIPIENT]},
        Message={
            "Subject": {"Data": subject, "Charset": "utf-8"},
            "Body": {
                "Html": {"Data": html, "Charset": "utf-8"},
            },
        },
    )


def _assemble_sender(original_sender: str) -> str:
    match = re.match(r"^(.+?)\s?<.+>$", original_sender)
    if match:
        return f"{ match.group(1) } <{ SENDER }>"
    return SENDER
