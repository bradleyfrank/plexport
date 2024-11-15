#!/usr/bin/env python3

"""
Script to display track rating and mood tags for a music album.
"""

import argparse
import csv
import json
import sys
from configparser import ConfigParser, NoOptionError
from itertools import chain
from pathlib import PosixPath
from typing import TextIO, Type

import inquirer
from logzero import setup_logger
from plexapi import audio, server


def output_csv(plex_data: list, titles: list, destination: TextIO) -> None:
    """Output in csv format."""
    writer = csv.writer(destination, quoting=csv.QUOTE_ALL)
    writer.writerow(titles)
    for item in plex_data:
        writer.writerow(convert_nested_lists(item))


def output_json(plex_data: list, titles: list, destination: TextIO) -> None:
    """Output in json format."""
    destination.write(json.dumps([dict(zip(titles, item)) for item in plex_data], indent=1))


def output_human(plex_data: list, titles: list, destination: TextIO) -> None:
    """Output in human readable text."""
    for item in plex_data:
        for index, value in enumerate(convert_nested_lists(item)):
            destination.write(f"{titles[index]}: {value}\n")
        destination.write("\n")


def select_albums(title: str) -> list:
    """Search for album by title."""
    results = MUSIC.searchAlbums(title=title)
    LZ.debug("Found albums: %s", results)
    if len(results) <= 1:
        return results
    choices = [album.title for album in results]
    questions = [inquirer.Checkbox("albums", "Export which albums?", choices)]
    answers = inquirer.prompt(questions)
    return [album for album in results if album.title in answers["albums"]]


def process_album(audio_album: Type[audio.Album]) -> list:
    """Create album metadata dictionary."""
    LZ.debug("Building album: %s", audio_album.title)
    return [
        audio_album.title or "",
        audio_album.titleSort or "",
        audio_album.userRating or 0,
        [genre.tag for genre in audio_album.genres] or ["None"],
        [style.tag for style in audio_album.styles] or ["None"],
        [collection.tag for collection in audio_album.collections] or ["None"],
    ]


def process_tracks(audio_track: Type[audio.Track]) -> list:
    """Create track metadata dictionary."""
    LZ.debug("Building track: %s", audio_track.title)
    return [
        audio_track.title or "",
        audio_track.album().title or "",
        audio_track.parentIndex or 0,
        audio_track.trackNumber or 0,
        audio_track.userRating or 0,
        [mood.tag for mood in audio_track.moods] or ["None"],
    ]


def convert_nested_lists(row) -> list:
    """Remove nested lists."""
    return [", ".join(sorted(i)) if isinstance(i, list) else i for i in row]


args = argparse.ArgumentParser(prog="plexport")
args.add_argument("-a", "--album", help="album(s) to match", type=str)
args.add_argument("-l", "--library", help="plex library", type=str)
args.add_argument("-d", "--debug", help="enable debug output", action="store_true")
args.add_argument("-o", "--output", help="output destination", type=PosixPath)
args.add_argument(
    "-m",
    "--metadata",
    help="type of metadata to fetch",
    choices=["album", "tracks"],
    default="album",
)
args.add_argument(
    "-f",
    "--format",
    help="how to format metadata",
    choices=["csv", "json", "human"],
    default="human",
)
flags = args.parse_args()

LZ = setup_logger(level=10 if flags.debug else 20)

cfg_parser = ConfigParser()
cfg_parser.read("plexport.cfg")

try:
    baseurl = cfg_parser.get("plexport", "baseurl")
    token = cfg_parser.get("plexport", "token")
except NoOptionError as err:
    LZ.error("Missing configuration parameter: %s", err)
    sys.exit(1)

try:
    library = flags.library or cfg_parser.get("plexport", "library")
except (NameError, NoOptionError):
    LZ.error("You must specify a library.")
    sys.exit(1)
else:
    LZ.debug("Using '%s' library", library)

plex = server.PlexServer(baseurl, token)
MUSIC = plex.library.section(library)

if flags.album:
    LZ.debug("Searching albums for '%s'", flags.album)
    albums = select_albums(flags.album)
else:
    LZ.debug("Selecting all albums")
    albums = list(MUSIC.albums())

LZ.debug("Albums selected: %s", albums)

match flags.metadata:
    case "album":
        headers = ["Album", "Sort Name", "Rating", "Genres", "Styles", "Collections"]
        metadata = [process_album(a) for a in albums]
    case "tracks":
        headers = ["Title", "Album", "Disc", "Track", "Rating", "Moods"]
        metadata = [process_tracks(t) for t in list(chain(*albums))]
    case _:
        LZ.error("Unknown metadata format.")
        sys.exit(1)

output_functions = {"csv": output_csv, "json": output_json, "human": output_human}
write_function = output_functions[flags.format]

if flags.output:
    dest = flags.output / "output" if flags.output.is_dir() else flags.output
    with open(dest, "w", newline="", encoding="utf-8") as fd:
        write_function(metadata, headers, fd)
else:
    write_function(metadata, headers, sys.stdout)
