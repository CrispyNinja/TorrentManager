# TorrentManager
A script to automatically manage your downloaded files to a PLEX server. It handles automatic uploades, deletion, creation of new folders, etc.


## Settings
Remember to change the IP adress, username and password.

**Change the local and remote paths to fit your setup**

--------------------------------------------------------
## Required modules
Install [Paramiko](http://www.paramiko.org/) and [GuessIt](https://github.com/guessit-io/guessit) with PIP.


## qBitTorrent
If using qBitTorrent it is recommended to enable "Keep incomplete torrents in" so the script does not move files that are incomplete.
