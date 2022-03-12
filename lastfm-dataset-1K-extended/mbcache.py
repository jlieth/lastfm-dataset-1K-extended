import json
from pathlib import Path
from typing import Any, Generic, Type, TypeVar, Union

from . import DATADIR
from .entities import Recording, Release


T = TypeVar("T", Recording, Release)


class Container(Generic[T]):
    def __init__(self, item_class: Type[T]):
        self.items: dict[str, T] = {}
        self.item_class = item_class

    def __getitem__(self, key: str) -> T:
        return self.items[key]

    def __setitem__(self, key: str, value: T):
        self.items[key] = value

    def from_dict(self, data: dict[str, dict[str, Any]]):
        for key, r in data.items():
            self[key] = self.item_class(**r)

    def to_dict(self) -> dict[str, dict[str, Any]]:
        return {mbid: r.dict() for mbid, r in self.items.items()}


class MBCache:
    def __init__(self, cachefile: Union[str, Path]):
        self.cachefile = cachefile
        self.recordings = Container(Recording)
        self.releases = Container(Release)

        self._read()

    def _read(self):
        try:
            data = json.loads(open(self.cachefile).read())
            self.recordings.from_dict(data["recordings"])
            self.releases.from_dict(data["releases"])
        except FileNotFoundError:
            pass
        except json.JSONDecodeError:
            pass

    def write(self):
        data = {
            "recordings": self.recordings.to_dict(),
            "releases": self.releases.to_dict(),
        }
        with open(self.cachefile, "w") as f:
            f.write(json.dumps(data))


if __name__ == "__main__":
    cachefile = DATADIR / "musicbrainz.cache"
    cache = MBCache(cachefile)
    cache.write()
