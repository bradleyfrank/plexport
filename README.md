# plexport

Export album and track metadata from Plex.

## Config

Create a config file `plexport.cfg` with the following:

```ini
[plexport]
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
usage: plexport [-h] [-a ALBUM] [-l LIBRARY] [-d] [-o OUTPUT]
                [-m {album,tracks}] [-f {csv,json,human}]

options:
  -h, --help            show this help message and exit
  -a ALBUM, --album ALBUM
                        album(s) to match
  -l LIBRARY, --library LIBRARY
                        plex library
  -d, --debug           enable debug output
  -o OUTPUT, --output OUTPUT
                        output destination
  -m {album,tracks}, --metadata {album,tracks}
                        type of metadata to fetch
  -f {csv,json,human}, --format {csv,json,human}
                        how to format metadata
```
