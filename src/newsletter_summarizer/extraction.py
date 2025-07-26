import json
from typing import TypedDict, List, Optional

from bs4 import BeautifulSoup


class ExtractedArticleTag(TypedDict):
    name: str
    uri: str
    identifier: str


class ExtractedArticle(TypedDict):
    id: str
    href: str
    published: str
    updated: str
    last_modified: str
    title: str
    description: str
    authors: List[str]
    tags: List[ExtractedArticleTag]
    text: Optional[str]


def extract_article(html: str) -> ExtractedArticle:
    soup = BeautifulSoup(html, "html.parser")

    page_head = soup.find("head")
    meta_title = page_head.find("meta", attrs={"property": "og:title"})
    head_title = (meta_title or {}).get("content")
    meta_description = page_head.find("meta", attrs={"name": "description"})
    head_description = (meta_description or {}).get("content")

    next_data = soup.find("script", id="__NEXT_DATA__").text
    next_data_dict = json.loads(next_data)
    next_data_context = next_data_dict["props"]["pageProps"]["data"]["context"]

    id = next_data_context["id"]
    href = next_data_context["href"]
    published = next_data_context["published"]
    updated = next_data_context["updated"]
    last_modified = next_data_context["lastModified"]
    title = next_data_context.get("title") or head_title
    authors = [a["name"] for a in next_data_context["authors"]]
    tags = [
        ExtractedArticleTag(name=t["name"], uri=t["uri"], identifier=t["identifier"])
        for t in next_data_context["tags"]
    ]

    text = None
    if "elements" in next_data_context:
        text = []
        for element in next_data_context["elements"]:
            for field in element["fields"]:
                if field["name"] in ["headline", "intro", "paragraph", "subhead"]:
                    text.append(field["value"])
        text = "\n".join(text)

    return ExtractedArticle(
        id=id,
        href=href,
        published=published,
        updated=updated,
        last_modified=last_modified,
        title=title,
        description=head_description,
        authors=authors,
        tags=tags,
        text=text,
    )
