import json
from pathlib import Path
from typing import Any, Callable, Generic, Optional, Type, TypeVar, Union

from . import DATADIR
from .entities import Recording, Release


T = TypeVar("T", Recording, Release)


class Container(Generic[T]):
    def __init__(self, item_class: Type[T], on_change: Optional[Callable] = None):
        self.items: dict[str, T] = {}
        self.item_class = item_class
        self.on_change: Optional[Callable] = on_change

    def __getitem__(self, key: str) -> T:
        return self.items[key]

    def __setitem__(self, key: str, value: T):
        self.items[key] = value
        if self.on_change:
            self.on_change()

    def from_dict(self, data: dict[str, dict[str, Any]]):
        for key, r in data.items():
            self.items[key] = self.item_class(**r)

    def to_dict(self) -> dict[str, dict[str, Any]]:
        return {mbid: r.dict() for mbid, r in self.items.items()}


class MBCache:
    BACKUP_AFTER = 50

    def __init__(self, cachefile: Union[str, Path]):
        self.cachefile = cachefile
        self.recordings = Container(Recording, on_change=self.backup)
        self.releases = Container(Release, on_change=self.backup)
        self.changes = 0

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

        self.changes = 0

    def _write(self):
        data = {
            "recordings": self.recordings.to_dict(),
            "releases": self.releases.to_dict(),
        }
        with open(self.cachefile, "w") as f:
            f.write(json.dumps(data))

    def backup(self):
        self.changes += 1
        if self.changes >= self.BACKUP_AFTER:
            print("Writing musicbrainz cache to disk...")
            self.status()
            self._write()
            self.changes = 0

    def status(self):
        print(
            "Musicbrainz cache:",
            f"{len(self.recordings.items)} recordings,",
            f"{len(self.releases.items)} releases",
        )


if __name__ == "__main__":
    cachefile = DATADIR / "musicbrainz.cache"
    cache = MBCache(cachefile)
    cache.backup()
