from itertools import islice
from typing import Optional

import musicbrainzngs
import python_progress_bar as progress_bar
from pyarrow import array, int32, parquet, string

from .entities import Recording, Release
from .mbfetcher import MBFetcher


class DatasetExtender:
    def __init__(self, dataset: str, outfile: str, skip: int = 0):
        self.fetcher = MBFetcher()
        self.dataset = parquet.read_table(dataset)
        self.outfile = outfile
        self.skip = skip

        self.additional_info = {}
        self.init_additional_info()

    def init_additional_info(self):
        columns = self.dataset.column_names
        length = self.dataset.num_rows
        keys = ["album_id", "album_name", "album_artist_name", "length", "tracknumber"]

        for key in keys:
            # try to initilize info from database columns
            if key in columns:
                idx = columns.index(key)
                self.additional_info[key] = self.dataset.column(idx).to_pylist()

            # otherwise create empty lists
            else:
                self.additional_info[key] = [None] * length

    def run(self):
        num_rows = self.dataset.num_rows

        # Make sure that the progress bar is cleaned up when user presses ctrl+c
        progress_bar.enable_trapping()
        # Create progress bar
        progress_bar.setup_scroll_area()

        idx = self.skip
        for row in islice(self.dataset.to_batches(max_chunksize=1), idx, None):
            # occasionally write results
            if idx > 0 and idx % 100 == 0:
                print("Writing parquet file to disk...")
                self.add_columns()
                self.write()

            percent = (idx + 1) * 100 // num_rows
            progress_bar.draw_progress_bar(percent)

            row = row.to_pydict()

            # get current info from row
            user_id = row["user_id"][0]
            timestamp = row["timestamp"][0]
            artist_id = row["artist_id"][0]
            artist_name = row["artist_name"][0]
            track_id = row["track_id"][0]
            track_name = row["track_name"][0]

            # try to get additional info if present
            album_id = row.get("album_id", [None])[0]
            album_name = row.get("album_name", [None])[0]
            album_artist_name = row.get("album_artist_name", [None])[0]
            length = row.get("length", [None])[0]
            tracknumber = row.get("tracknumber", [None])[0]

            # print info about this item to console
            number = f"[#{idx + 1}]"
            spacer = f"{' ' * len(number)}"
            print(f"{number} {artist_name} - {track_name} ({timestamp})")

            # if the item already has additional info, copy info to dict of
            # additional info and do nothing else
            if album_id:
                print(f"{spacer} already contains additional info")
                self.additional_info["album_id"][idx] = album_id
                self.additional_info["album_name"][idx] = album_name
                self.additional_info["album_artist_name"][idx] = album_artist_name
                self.additional_info["length"][idx] = length
                self.additional_info["tracknumber"][idx] = tracknumber
            # if not, fetch info from musicbrainz
            else:
                recording = release = None

                try:
                    recording, release = self.fetch_info(track_id, idx)
                except musicbrainzngs.ResponseError:
                    pass

                if recording:
                    self.additional_info["length"][idx] = recording.length
                    self.additional_info["tracknumber"][idx] = recording.tracknumber
                    self.additional_info["album_id"][idx] = recording.album_id
                if release:
                    self.additional_info["album_name"][idx] = release.title
                    self.additional_info["album_artist_name"][idx] = release.artist

            idx += 1

        progress_bar.destroy_scroll_area()

    def fetch_info(self, track_id: str, idx: int) -> tuple[Optional[Recording], Optional[Release]]:
        number = f"[#{idx + 1}]"
        spacer = f"{' ' * len(number)}"

        recording: Optional[Recording] = None
        release: Optional[Release] = None

        if track_id:
            print(f"{spacer} Fetching info for track {track_id}...")
            recording = self.fetcher.get_track_info_by_mbid(track_id)
            print(f"{spacer} Track info: {recording.dict()}")
            album_id = recording.album_id
            if album_id:
                release = self.fetcher.get_release_info_by_mbid(album_id)
                print(f"{spacer} Album info: {release.dict()}")

        return recording, release

    def write(self):
        parquet.write_table(self.dataset, self.outfile, compression="SNAPPY")

    def add_columns(self):
        # remove columns first so we don't add them twice
        self._remove_additional_info()

        self._append_additional_info("album_id", string)
        self._append_additional_info("album_name", string)
        self._append_additional_info("album_artist_name", string)
        self._append_additional_info("length", int32)
        self._append_additional_info("tracknumber", int32)

    def _append_additional_info(self, key: str, col_type):
        column = self.additional_info[key]
        self.dataset = self.dataset.append_column(key, array(column, col_type()))

    def _remove_additional_info(self):
        for colname in self.additional_info.keys():
            columns = self.dataset.column_names
            if colname in columns:
                idx = columns.index(colname)
                self.dataset = self.dataset.remove_column(idx)
