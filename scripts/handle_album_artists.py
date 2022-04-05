#!/bin/env python

import sqlite3
from typing import Optional

import python_progress_bar as progress_bar


def get_or_create_artist(cur, artist_name: str) -> Optional[int]:
    artist_id = get_artist_id(cur, artist_name)
    if artist_id is None:
        artist_id = insert_artist(cur, artist_name)
    return artist_id

def get_artist_id(cur, artist_name: str) -> Optional[int]:
    query = "SELECT id FROM artists WHERE name = ?;"
    result = cur.execute(query, [artist_name]).fetchone()
    if result:
        return result[0]
    return None

def insert_artist(cur, artist_name: str) -> Optional[int]:
    query = "INSERT INTO artists (name) VALUES (?);"
    cur.execute(query, [artist_name])
    return get_artist_id(cur, artist_name)


if __name__ == "__main__":
    import sys
    db = sys.argv[1]

    con = sqlite3.connect(db)
    cur = con.cursor()

    album_artist_names = []
    query = "SELECT DISTINCT album_artist_name FROM listens;"
    for row in cur.execute(query):
        name = row[0]
        if name:
            album_artist_names.append(name)

    progress_bar.enable_trapping()
    progress_bar.setup_scroll_area()
    for idx, name in enumerate(album_artist_names):
        if idx % 1000 == 0:
            print(f"{idx + 1} of {len(album_artist_names)}")
        percent = (idx + 1) * 100 // len(album_artist_names)
        progress_bar.draw_progress_bar(percent)
        artist_id = get_or_create_artist(cur, name)
        query = "UPDATE listens SET album_artist_id = ? WHERE album_artist_name = ?;"
        cur.execute(query, [artist_id, name])

    con.commit()
    con.close()
