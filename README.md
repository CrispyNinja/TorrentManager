# TorrentManager
A script to automatically manage your downloaded files to a PLEX server. It handles automatic uploades, deletion, creation of new folders, etc.

This will automatically create new folders on the server for each new show it finds, and upload to already existing folders.
Great for managing a remote PLEX server where you download a lot of files locally and don't want to manually transfer everything.

For movies it will simply transfer the files to the directory of your choosing.

### Features
* Automatic Uploads
* Create every folder for you
* Delete the local files it has successfully transferred
* Automatically find the name of the show
* Add your own file extensions

## Settings
Remember to change the IP adress, username and password.

**Change the local and remote paths to fit your setup**

--------------------------------------------------------
## Required modules
Install [Paramiko](http://www.paramiko.org/) and [GuessIt](https://github.com/guessit-io/guessit) with PIP.


## qBitTorrent
If using qBitTorrent it is recommended to enable "Keep incomplete torrents in" so the script does not move files that are incomplete.
