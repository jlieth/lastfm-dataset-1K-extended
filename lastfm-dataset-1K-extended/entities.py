from typing import Optional

from pydantic import BaseModel


class Recording(BaseModel):
    album_id: Optional[str] = None
    length: int = 0
    tracknumber: int = 0


class Release(BaseModel):
    title: str
    artist: str
