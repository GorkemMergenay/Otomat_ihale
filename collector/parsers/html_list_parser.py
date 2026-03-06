from __future__ import annotations

from bs4 import BeautifulSoup


def parse_list_items(html: str, selector: str):
    soup = BeautifulSoup(html, "html.parser")
    return soup.select(selector)
