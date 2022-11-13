# plexex

Export track ratings and mood tags from a music album.

## Config

Create a config file `plexex.cfg` with the following:

```ini
[plexex]
baseurl =
token =
library =
```

Your `baseurl` is the address of your Plex server.

The value of `library` is the name of your Music library in Plex.

To find your Plex `token`, navigate to `/Library/Application Support/Plex Media Server/` and run:

```sh
tr ' ' '\n' < Preferences.xml | grep PlexOnlineToken
```

## Installation

```sh
pip install -r requirements.txt
```

## Usage

```sh
usage: plexex [-h] [-a ALBUM] [-l LIBRARY] [-f FILE] [-c] [-d]

options:
  -h, --help            show this help message and exit
  -a ALBUM, --album ALBUM
                        album title
  -l LIBRARY, --library LIBRARY
                        plex library
  -f FILE, --file FILE  save output to file
  -c, --csv             output in csv format
  -d, --debug           enable debug output
```

