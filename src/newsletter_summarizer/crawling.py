import logging
import os
from typing import Tuple
from urllib.parse import parse_qs

import httpx
from httpx import URL, Response

USER_AGENT = os.environ["NEWSLETTER_SUMMARIZER_USER_AGENT"]
INITIAL_LOGIN_URL = os.environ["NEWSLETTER_SUMMARIZER_INITIAL_LOGIN_URL"]
CLIENT_ID = os.environ["NEWSLETTER_SUMMARIZER_CLIENT_ID"]
REDIRECT_URI = os.environ["NEWSLETTER_SUMMARIZER_REDIRECT_URI"]
USERNAME = os.environ["NEWSLETTER_SUMMARIZER_USERNAME"]
PASSWORD = os.environ["NEWSLETTER_SUMMARIZER_PASSWORD"]

logger = logging.getLogger(__name__)
client = httpx.AsyncClient(headers={"User-Agent": USER_AGENT})


async def obtain_login_url() -> Tuple[URL, str]:
    res = await client.get(
        INITIAL_LOGIN_URL,
        params={
            "response_type": "code",
            "scope": "openid+profile+email+offline_access",
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
        },
        follow_redirects=True,
    )

    # Todo: This seems to be failing sometimes
    if not res.is_success or res.url == INITIAL_LOGIN_URL:
        _log_response(res, "Login URL Response")
        raise AssertionError("Expected login to redirect.")

    login_url = res.url
    parsed_query = parse_qs(login_url.query.decode("utf8"))
    assert "state" in parsed_query, "Expected login url to contain a state"
    login_state = parsed_query["state"][0]

    return login_url, login_state


async def login() -> None:
    login_url, login_state = await obtain_login_url()

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

    # Todo: This seems to be failing sometimes
    if not res.is_success or res.url == login_url:
        _log_response(res, "Login Response")
        raise AssertionError("Expected login to redirect.")

    global logged_in
    logged_in = True


def _log_response(res: Response, response_name: str = "Response") -> None:
    logger.info("%s Status: %s", response_name, res.status_code)
    logger.info("%s URL: %s", response_name, res.url)
    logger.info("%s Headers: %s", response_name, res.headers)
    logger.info("%s Payload: %s", response_name, res.text)


async def fetch_html(url: str) -> str:
    assert logged_in, "You need to call login() first."
    res = await client.get(url, follow_redirects=True)
    assert res.is_success
    return res.text
