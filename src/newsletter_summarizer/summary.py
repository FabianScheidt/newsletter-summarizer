import logging
import json
import os
from typing import Dict, Any, TypedDict

from aiobotocore.client import AioBaseClient
from aiobotocore.session import get_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

session = get_session()

MODEL_ID = os.environ["NEWSLETTER_SUMMARIZER_BEDROCK_MODEL_ID"]
SYSTEM_PROMPT = os.environ["NEWSLETTER_SUMMARIZER_SYSTEM_PROMPT"]


class SummaryLog(TypedDict):
    request: Dict[str, Any]
    response: Dict[str, Any]


async def summarize(bedrock: AioBaseClient, text: str) -> (str, SummaryLog):
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": text}],
        "max_tokens": 1000,
        "temperature": 0.7,
        "top_k": 250,
        "top_p": 1.0,
        "stop_sequences": [],
    }

    # Invoke the model with the request.
    response = await bedrock.invoke_model(
        modelId=MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(payload),
    )

    # Decode the response body.
    model_response = json.loads(await response["body"].read())

    # Extract and print the response text.
    response_text = model_response["content"][0]["text"]
    return response_text, SummaryLog(request=payload, response=model_response)
