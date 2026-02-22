import logging
import os
from urllib.parse import parse_qs

import httpx
from httpx import URL

USER_AGENT = os.environ["NEWSLETTER_SUMMARIZER_USER_AGENT"]
INITIAL_LOGIN_URL = os.environ["NEWSLETTER_SUMMARIZER_INITIAL_LOGIN_URL"]
CLIENT_ID = os.environ["NEWSLETTER_SUMMARIZER_CLIENT_ID"]
REDIRECT_URI = os.environ["NEWSLETTER_SUMMARIZER_REDIRECT_URI"]
USERNAME = os.environ["NEWSLETTER_SUMMARIZER_USERNAME"]
PASSWORD = os.environ["NEWSLETTER_SUMMARIZER_PASSWORD"]

logger = logging.getLogger(__name__)
client = httpx.AsyncClient(headers={"User-Agent": USER_AGENT})


async def login() -> None:
    logger.info("Obtaining login URL...")
    url_res = await client.get(
        INITIAL_LOGIN_URL,
        params={
            "response_type": "code",
            "scope": "openid+profile+email+offline_access",
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
        },
        follow_redirects=True,
    )

    assert url_res.is_success, f"Expected login url request to be successful, got status code { url_res.status_code }: { url_res.text }"

    if _contains_redirect_uri(url_res):
        logger.info("Already logged in.")
        return

    login_url = url_res.url
    parsed_query = parse_qs(login_url.query.decode("utf8"))
    assert "state" in parsed_query, "Expected login url to contain a state"
    login_state = parsed_query["state"][0]

    logger.info("Logging in...")
    res = await client.post(
        login_url,
        data={
            "action": "default",
            "state": login_state,
            "username": USERNAME,
            "password": PASSWORD,
        },
        follow_redirects=True,
    )

    assert res.is_success, f"Expected login request to be successful. Got status code { res.status_code }: { res.text }"
    assert _contains_redirect_uri(res)
    logger.info("Login successful.")


def _contains_redirect_uri(response: httpx.Response) -> bool:
    for el in response.history:
        if el.url.copy_with(params={}) == URL(REDIRECT_URI):
            return True
    return False


async def fetch_html(url: str) -> str:
    res = await client.get(url, follow_redirects=True)
    assert res.is_success, f"Expected fetch to be successful, got status code { res.status_code }: { res.text }"
    return res.text
