#!/usr/bin/env python3

"""
Script to display track rating and mood tags for a music album.
"""

import argparse
import sys
from configparser import ConfigParser

import inquirer
from plexapi.server import PlexServer

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("-a", "--album", help="album title", type=str)
arg_parser.add_argument("-l", "--library", help="plex library", type=str)
args = arg_parser.parse_args()

cfg_parser = ConfigParser()
cfg_parser.read("plexex.cfg")

baseurl = cfg_parser.get("plexex", "baseurl")
token = cfg_parser.get("plexex", "token")
library = args.library or cfg_parser.get("plexex", "library")

if not library:
    print("You must specify a library.")
    sys.exit(1)

if not args.album:
    print("You must specify an album.")
    sys.exit(1)

plex = PlexServer(baseurl, token)
music = plex.library.section(library)
results = music.searchAlbums(title=args.album)

if not results:
    print("No results found.")
    sys.exit(1)

if len(results) > 1:
    choices = [album.title for album in results]
    questions = [inquirer.List("album", "Display which album?", choices)]
    answers = inquirer.prompt(questions)
    album_id = next(album for album in results if album.title == answers["album"])
else:
    album_id = results[0]

for track in album_id.tracks():
    print(f"Track: {track.trackNumber:03} - {track.title}")
    print(f"Rating: {int((track.userRating or 0) / 2)}")
    print(f"Moods: {', '.join([mood.tag for mood in track.moods])}")
    print("")
