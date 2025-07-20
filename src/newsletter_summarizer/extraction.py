import json
from typing import TypedDict

from bs4 import BeautifulSoup


class ExtractedArticle(TypedDict):
    id: str
    title: str
    text: str


def extract_article(html: str) -> ExtractedArticle:
    soup = BeautifulSoup(html)

    next_data = soup.find("script", id="__NEXT_DATA__").text
    next_data_dict = json.loads(next_data)
    next_data_context = next_data_dict["props"]["pageProps"]["data"]["context"]

    id = next_data_context["id"]
    title = next_data_context["title"]

    text = []
    for element in next_data_context["elements"]:
        for field in element["fields"]:
            if field["name"] in ["headline", "intro", "paragraph", "subhead"]:
                text.append(field["value"])
    text = "\n".join(text)

    return ExtractedArticle(id=id, title=title, text=text)
