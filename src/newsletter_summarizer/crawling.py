import os
from typing import Tuple
from urllib.parse import parse_qs

import httpx
from httpx import URL

USER_AGENT = os.environ["NEWSLETTER_SUMMARIZER_USER_AGENT"]
INITIAL_LOGIN_URL = os.environ["NEWSLETTER_SUMMARIZER_INITIAL_LOGIN_URL"]
CLIENT_ID = os.environ["NEWSLETTER_SUMMARIZER_CLIENT_ID"]
REDIRECT_URI = os.environ["NEWSLETTER_SUMMARIZER_REDIRECT_URI"]
USERNAME = os.environ["NEWSLETTER_SUMMARIZER_USERNAME"]
PASSWORD = os.environ["NEWSLETTER_SUMMARIZER_PASSWORD"]

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

    login_url = res.url
    assert (
        login_url != INITIAL_LOGIN_URL
    ), "Expected initial url to redirect to a different one for login."

    parsed_query = parse_qs(res.url.query.decode("utf8"))
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
    assert res.is_success
    assert res.url != login_url, "Expected login to redirect."

    global logged_in
    logged_in = True


async def fetch_html(url: str) -> str:
    assert logged_in, "You need to call login() first."
    res = await client.get(url, follow_redirects=True)
    assert res.is_success
    return res.text
