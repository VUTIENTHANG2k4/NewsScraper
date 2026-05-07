from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class NewsItemCreate(BaseModel):
    source_id: str
    source_name: str
    source_url: HttpUrl
    title: str | None = Field(default=None, max_length=500)
    author: str | None = Field(default=None, max_length=250)
    content: str | None = Field(default=None, max_length=50000)
    image_url: HttpUrl | None = None
    published_at: datetime
    created_at: datetime
