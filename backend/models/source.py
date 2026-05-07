from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class SourceSelectors(BaseModel):
    article_list: str = ""
    title: str = ""
    author: str = ""
    content: str = ""
    published_at: str = ""
    image: str = ""
    date_format: str = ""


class SourceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    base_url: HttpUrl
    crawl_type: Literal["http", "playwright"] = "http"
    selector_type: Literal["css", "xpath"] = "css"
    selectors: SourceSelectors


class SourceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    crawl_type: Literal["http", "playwright"] | None = None
    selector_type: Literal["css", "xpath"] | None = None
    selectors: SourceSelectors | None = None
    is_active: bool | None = None
    last_crawled: datetime | None = None
