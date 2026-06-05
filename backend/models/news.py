from datetime import datetime

from pydantic import BaseModel, Field


class NewsItemCreate(BaseModel):
    """
    Schema validate document news trước khi insert vào MongoDB.

    image_url để dạng str thay vì HttpUrl vì một số site trả URL tương đối
    hoặc thiếu scheme — không nên fail crawl chỉ vì vậy.
    """

    source_id: str
    source_name: str
    source_url: str
    title: str | None = Field(default=None, max_length=2000)
    author: str | None = Field(default=None, max_length=250)
    content: str | None = Field(default=None, max_length=100000)
    image_url: str | None = Field(default=None, max_length=2000)
    published_at: datetime
    created_at: datetime
