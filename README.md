# Last.fm 1K User Dataset Extended

## What is this
The Last.fm 1K User Dataset is a collection of 1000 users' music listening habits
on [Last.fm](), originally collected and released by Òscar Celma in
2010. The official release and README of the project can be found at
http://ocelma.net/MusicRecommendationDataset/lastfm-1K.html.

This repository hosts the
[Last.fm Dataset - 1K users](http://ocelma.net/MusicRecommendationDataset/lastfm-1K.html)
under the same license and terms as in the offical README, copied for convenience below.

This is a fork of [eifuentes'](https://github.com/eifuentes/) repository and builds on their additions to the original dataset.

## Changes to the Dataset

My changes are based on eifuentes' parquet files of the dataset. Please see
[their README](https://github.com/eifuentes/lastfm-dataset-1K#preprocessing)
about the changes they made.

My use case required album infomation for the listened tracks. For every listened
track with a musicbrainz ID, I queried musicbrainz for the corresponding album
information. Note that a track may appear on more than one album. I always
chose the first album returned. **This may not be identical to the album the
user actually listened to.**

## Examples

The following example rows show the new table schema and possible values for
each column.

| user_id | timestamp | artist_id | artist_name | track_id | track_name | album_id | album_name | album_artist_name | length | tracknumber |
| - | - | - | - | - | - | - | - | - | - | - |
| user_000001 | 2006-08-13 13:59:20+00:00 | 09a114d9-7723-4e14-b524-379697f6d2b5 | Plaid & Bob Jaroc | c4633ab1-e715-477f-8685-afa5f2058e42 | The Launching Of Big Face | b5d8192f-6924-4e2c-952b-b10b69eb2cfa | Greedy Baby | Plaid & Bob Jaroc | 254173 | 3 |
| user_000001 | 2006-08-21 15:14:58+00:00 | 7b42e4cf-650b-4fe0-bc7d-c95e31247729 | Peven Everett | f548d49d-4239-4066-b867-f88419c14e3c | I Can Give It | 9fd11527-90ac-4c2d-ae37-40e1570d5011 | GP03 | Various Artists | 235360 | 4 |
| user_000001 | 2006-08-21 15:18:49+00:00 | e757253a-85cc-4892-a2e4-c88c3948b670 | Shaun Escoffery | 413ee492-9d5e-488f-94c4-993d6a54b55e | Let It Go | 9fd11527-90ac-4c2d-ae37-40e1570d5011 | GP03 | Various Artists | 265240 | 5 |
| user_000587 | 2009-01-28 12:20:14+00:00 | | Nujabes + Fat Jon | | 5. Mystline | | | | | |
| user_000647 | 2007-06-20 20:06:50+00:00 | 03ad1736-b7c9-412a-b442-82536d63a5c4 | Elliott Smith | 8a8b9728-b745-4054-81e4-5b1fcdcd13cd | L.A. | | | | 0 | 0 |

* Row 1: musicbrainz id for the track was available and an album was found
* Row 2 and 3: MBID was available and a compilation album was found for both tracks
* Row 4: No MBID was available so no query for album information was made
* Row 5: [MBID](https://musicbrainz.org/recording/8a8b9728-b745-4054-81e4-5b1fcdcd13cd)
  was available but no official release contains this track so no album
  information was saved

## Caveats

1) As mentioned above, the album information is not entirely accurate. Since
   a track may appear on several albums and it's not possible to reconstruct
   with the available data which album the user was listening to, I just chose
   *any* album this track appears on. This is sufficent for my use case.
   It may not be for yours.
2) I only queried album information for tracks that had a musicbrainz ID. It's
   certainly possible to query musicbrainz for all other tracks as well and a
   good number of them are probably in their database. I decided against it
   because incomplete data is to be expected for user-submitted information.
3) So far I have only processed the smaller, educational subset of 50 users.
   The provided source code may be sufficient to process the larger dataset
   of 1000 users, though two issues kept popping up:
   - I ran into serious **memory issues** while trying my code with the larger
     dataset. Since I only needed the smaller dataset, I have not investigated
     the memory issues further. Any help with this would be much appreciated!
   - The **runtime** is atrocious. Processing the small subset took about
     44 hours. Thanks to caching of musicbrainz queries, the runtime should be
     less than linear as long as tracks are repeated throughout the dataset.
     Parallelization and async calls would probably help a lot.

## How to use

If you only need the data, just grab one of the files from the release.

If you want to extend a dataset yourself, you can run the extender.

The extender reads in a parquet file of the original data without album
information, queries musicbrainz for information and outputs a new parquet file
with the additional information.

Install the requirements:

```shell
$ pip install -r requirements.txt
```

Then run the main module (from the root of the repository):

```shell
$ python -m lastfm-dataset-1K-extended.main --help
Usage: python -m lastfm-dataset-1K-extended.main [OPTIONS]

Options:
  -i, --infile TEXT   Input dataset.  [required]
  -o, --outfile TEXT  Output file.
  -s, --skip INTEGER  Number of rows to skip.
  --help              Show this message and exit.
```

`-i`/`--infile` is required and should point to the parquet file
you want to extend.

`-o`/`--outfile` is optional and will be the filename of the extended dataset.

`-s`/`--skip` is useful to continue the extension run after an interruption
(the new parquet file is auto-saved after every 100 entries, so you might want
to round down to the last multiple of 100).

## Converting file types

### parquet to csv
Install `parquet-tools`:

```shell
$ pip install parquet-tools
```

And run:

```shell
$ parquet-tools csv <parquet file>
```

### csv to sqlite
Install `sqlite-utils`:

```shell
$ pip install sqlite-utils
```

And run:

```shell
$ sqlite-utils insert <output database file> <table name> <input csv file> --csv
```

---

## Original README

> ## README
> *Version 1.0, May 2010*
>
> ### What is this?
>
> This dataset contains *user*, *timestamp*, *artist*, *song* tuples
> collected from [Last.fm API](http://www.last.fm/api),
> using the
> [user.getRecentTracks()](https://www.last.fm/api/show/user.getRecentTracks)
> method.
>
> This dataset represents the whole listening habits (till May, 5th 2009)
> for nearly 1,000 users.
>
> ### Files
>
>| Filename                                         | MD5                              |
>| ------------------------------------------------ | -------------------------------- |
>| userid-timestamp-artid-artname-traid-traname.tsv | 64747b21563e3d2aa95751e0ddc46b68 |
>| userid-profile.tsv                               | c53608b6b445db201098c1489ea497df |
>
> ### Data Statistics
>
> #### userid-timestamp-artid-artname-traid-traname.tsv
>
>| Element               | Statistic  |
>| --------------------- | ---------- |
>| Total Lines           | 19,150,868 |
>| Unique Users          | 992        |
>| Artists with MBID     | 107,528    |
>| Artists without MBDID | 69,420     |
>
> ### Data Format
>
> The data is formatted one entry per line as follows (tab separated, `\t`)
>
> #### userid-timestamp-artid-artname-traid-traname.tsv
>
> ```
> userid \t timestamp \t musicbrainz-artist-id \t artist-name \t musicbrainz-track-id \t track-name
> ```
>
> #### userid-profile.tsv
>
> ```
> userid \t gender ('m'|'f'|empty) \t age (int|empty) \t country (str|empty) \t signup (date|empty)
> ```
>
> ### Example:
>
> #### userid-timestamp-artid-artname-traid-traname.tsv
>
> ```
> user_000639 \t 2009-04-08T01:57:47Z \t MBID \t The Dogs D'Amour \t MBID \t Fall in Love Again?
> user_000639 \t 2009-04-08T01:53:56Z \t MBID \t The Dogs D'Amour \t MBID \t Wait Until I'm Dead
> ...
> ```
>
> #### userid-profile.tsv
>
> ```
> user_000639 \t m \t Mexico \t Apr 27, 2005
> ...
> ```
>
> ### License
>
> The data contained in `lastfm-dataset-1K.tar.gz` is distributed with
> permission of [Last.fm](http://last.fm).
>
>The data is made available for non-commercial use.
>
> Those interested in using the data or web services in a commercial
> context should contact:
>
> *partners [at] last [dot] fm*.
>
> For more information see Last.fm [terms of service](http://www.last.fm/api/tos).
>
> ### Acknowledgements
>
> Thanks to [Last.fm](http://last.fm) for providing the access to this data
> via their web services.
>
> Special thanks to [Norman Casagrande](http://www.last.fm/user/nova77LF).
>
> ### References
>
> When using this dataset you must reference the [Last.fm](http://last.fm) webpage.
>
> Optionally (not mandatory at all!), you can cite *Chapter 3* of
> [this book](http://ocelma.net/MusicRecommendationBook/index.html)
>
> ```
> @book{Celma:Springer2010,
>   author = {Celma, O.},
>   title = {{Music Recommendation and Discovery in the Long Tail}},
>   publisher = {Springer},
>   year = {2010}
> }
> ```
>
> ### Contact
>
> This data was collected by [Òscar Celma](http://www.dtic.upf.edu/~ocelma/)
> @ [MTG](http://mtg.upf.edu)/[UPF](http://upf.edu)
>
