#!/usr/bin/env python3

"""
Script to display track rating and mood tags for a music album.
"""

import argparse
import csv
import sys
from configparser import ConfigParser, NoOptionError
from itertools import chain
from pathlib import Path
from typing import Optional, TextIO, Type

import inquirer
from logzero import setup_logger
from plexapi import audio, server


def output_csv(songs: audio.Track, csvfile: Optional[TextIO]) -> None:
    """Output in csv format."""
    writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
    writer.writerow(["Album", "Track No.", "Track Title", "Rating", "Moods"])
    for song in songs:
        writer.writerow(
            [
                song["album"],
                song["number"],
                song["title"],
                song["rating"],
                ", ".join(song["moods"]),
            ]
        )


def output_plaintext(songs: audio.Track, outfile: Optional[TextIO]) -> None:
    """Output in plain text."""
    for song in songs:
        outfile.write(f"{song['number']}) {song['title']} ({song['album']})\n")
        outfile.write(f"Moods: {', '.join(song['moods'])}\n")
        outfile.write(f"Rating: {song['rating']}\n")
        outfile.write("\n")


def get_specific_albums(title: str) -> list:
    """Search for album by title."""
    results = MUSIC.searchAlbums(title=title)
    LOGGER.debug("Found albums: %s", results)
    if len(results) <= 1:
        return results
    choices = [album.title for album in results]
    questions = [inquirer.Checkbox("albums", "Export which albums?", choices)]
    answers = inquirer.prompt(questions)
    return [album for album in results if album.title in answers["albums"]]


def build_tracks(audio_track: Type[audio.Track]) -> dict:
    """Create track metadata dictionary."""
    LOGGER.debug("Building track: %s", audio_track.title)
    return {
        "album": audio_track.album().title or "",
        "number": audio_track.trackNumber or -1,
        "title": audio_track.title or "",
        "rating": audio_track.userRating or 0,
        "moods": [mood.tag for mood in audio_track.moods] or ["None"],
    }


arg_parser = argparse.ArgumentParser(prog="plexex")
arg_parser.add_argument("-a", "--album", help="album title", type=str)
arg_parser.add_argument("-l", "--library", help="plex library", type=str)
arg_parser.add_argument("-f", "--file", help="save output to file", type=Path)
arg_parser.add_argument("-c", "--csv", help="output in csv format", action="store_true")
arg_parser.add_argument("-d", "--debug", help="enable debug output", action="store_true")
args = arg_parser.parse_args()

LOGGER = setup_logger(level=10 if args.debug else 20)

cfg_parser = ConfigParser()
cfg_parser.read("plexex.cfg")

try:
    baseurl = cfg_parser.get("plexex", "baseurl")
    token = cfg_parser.get("plexex", "token")
except NoOptionError as err:
    LOGGER.error("Missing configuration parameter: %s", err)
    sys.exit(1)

try:
    library = args.library or cfg_parser.get("plexex", "library")
except (NameError, NoOptionError):
    LOGGER.error("You must specify a library.")
    sys.exit(1)
else:
    LOGGER.debug("Using '%s' library", library)

try:
    if args.file and args.file.is_dir():
        raise IsADirectoryError("Output file cannot be a directory.")
except IsADirectoryError as err:
    LOGGER.error(err)
    sys.exit(1)

plex = server.PlexServer(baseurl, token)
MUSIC = plex.library.section(library)

if args.album:
    albums = get_specific_albums(args.album)
else:
    albums = list(MUSIC.albums())

LOGGER.debug("Albums selected: %s", albums)
tracks = [build_tracks(t) for t in list(chain(*albums))]
outfunc = output_csv if args.csv else output_plaintext

if args.file:
    with open(args.file, "w", newline="", encoding="utf-8") as export:
        outfunc(tracks, export)
else:
    outfunc(tracks, sys.stdout)
