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

## Usage

```sh
pip install -r requirements.txt
./plexex.py -a <album> [-l <library>]
```

