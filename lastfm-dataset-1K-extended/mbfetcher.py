from typing import Any

import musicbrainzngs

from . import DATADIR
from .entities import Recording, Release
from .mbcache import MBCache


class MBFetcher:
    CACHEFILE = DATADIR / "musicbrainz.cache"

    def __init__(self):
        self.cache = MBCache(self.CACHEFILE)
        musicbrainzngs.set_useragent(
            "Example music app", "0.1", "http://example.com/music"
        )

    def get_track_info_by_mbid(self, mbid: str) -> Recording:
        try:
            return self.cache.recordings[mbid]
        except KeyError:
            result: dict[str, Any] = musicbrainzngs.get_recording_by_id(
                mbid, includes=["releases", "media"], release_status=["official"]
            )["recording"]

            album_id = None
            length = result.get("length", 0)
            tracknumber = 0

            releases = result.get("release-list", [])
            if len(releases) >= 1:
                # just pick the first one
                release = releases[0]
                album_id = release["id"]

                try:
                    tracknumber = release["medium-list"][0]["track-list"][0]["position"]
                except (KeyError, IndexError):
                    pass

            recording = Recording(
                album_id=album_id, length=int(length), tracknumber=int(tracknumber)
            )

            self.cache.recordings[mbid] = recording
            return recording

    def get_release_info_by_mbid(self, mbid: str) -> Release:
        try:
            return self.cache.releases[mbid]
        except KeyError:
            result: dict[str, Any] = musicbrainzngs.get_release_by_id(mbid, includes=["artists"])[
                "release"
            ]

            release = Release(
                title=result["title"], artist=result["artist-credit-phrase"]
            )

            self.cache.releases[mbid] = release
            return release

    def write_cache(self):
        self.cache.write()
