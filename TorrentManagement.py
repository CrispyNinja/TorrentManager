
import os
import sys
import paramiko
import glob
import guessit
import time
import ctypes
from paramiko import sftp
from datetime import datetime
import shutil
import math

# REQUIRED MODULES:
# - Paramiko
# - Guessit
# Install with PIP

####################################################################
# SETTINGS BEGIN

delete_on_process = True # If we should delete file after processing

# SSH credentials to your server
ip_address = 'x.x.x.x'
port = 22
username = 'username'
password = 'password'

# Local Paths
tv_path = r'\Local\Path\To\TV' # Local root directory of your 'TV' folder
movie_path = r'\Local\Path\To\Movies' # Local root directory of your 'Movies' folder

# Remote Paths
remote_tv_path = '/Remote/Path/To/TV Shows/' # Where we should upload all TV files
remote_movie_path = '/Remote/Path/To/Movies/' # Where we should upload all Movie files

time_sleep = 5.0 * 60 # How long we should sleep before checking again (in seconds)

# Supported video file extensions
types = ('.mkv', '.avi', '.mp4', '.mov', '.flv')

# SETTINGS END
####################################################################

# Temporary array of videos we have processed
regfiles = [None]


####################################################################

####################################################################
def frame(name, style_character='*'):
    """Frame the name with the style_character."""

    frame_line = style_character * (len(name) + 4)
    print(frame_line)
    print('{0} {1} {0}'.format(style_character, name))
    print(frame_line)

frame('TorrentManager 1.0')

# Set up SSH
try:
    transport = paramiko.Transport((ip_address, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
except paramiko.ssh_exception.SSHException as error:
    print('> Error: ' + str(error))
    sys.exit('> Exiting... Reason: could not connect')

def containsVideos(dirname):
    if os.path.isdir(dirname):
        for root, dirs, files in os.walk(dirname):
            for vids in files:
                if vids.endswith(types):
                    return True
                
            return False

    return False




####################################################################
# LOGGING
####################################################################

# Func to convert from bytes to a human readable format
def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

# A simple progressbar
def progressBar(value, endvalue, bar_length=20):
        percent = float(value) / endvalue
        arrow = '-' * int(round(percent * bar_length)-1) + '>'
        spaces = ' ' * (bar_length - len(arrow))

        sys.stdout.write("\rTransferred: [{0}] {1}/{2} ({3}%)".format(arrow + spaces, convert_size(value), convert_size(endvalue), float(round(percent * 100, 2))))
        sys.stdout.flush()

# Callback for upload progress
def reportProgress(currentBytes, totalBytes):
    progressBar(currentBytes, totalBytes)
    # print("Transferred: {0}/{1} ({2}%)".format(convert_size(currentBytes), convert_size(totalBytes), round(1 - ((totalBytes - currentBytes) / totalBytes), 4) * 100), flush=True, end='\r')

####################################################################
# END LOGGING
####################################################################




def deleteFile(path, isTV):
    # Check if file is in another dir than our main one
    dirname = os.path.dirname(os.path.realpath(path))

    if isTV:
        if dirname != tv_path:
            print('[*] Local path not same as current (sub folder?)')
            print('[*] Deleting: ' + dirname)

            os.remove(path)

            if not containsVideos(dirname):
                shutil.rmtree(dirname)
        else:
            # If not, just delete it
            os.remove(path)
            print('[*] Deleted')
    else:
        if dirname != movie_path:
            print('[*] Local path not same as root (sub folder?)')
            print('[*] Deleting: ' + dirname)

            os.remove(path)
            shutil.rmtree(dirname)
        else:
            # If not, just delete it
            os.remove(path)
            print('[*] Deleted')

def capitalize_name(name):
    words = name.split()
    cap_words = []

    for word in words:
        if word != 'of':
            cap_word = word.capitalize()
            cap_words.append(cap_word)
        else:
            cap_words.append(word)

    new_name = ' '.join(cap_words)
    return new_name

def uploadMovie(movie):
    filename = os.path.basename(movie)

    out_dir = remote_movie_path + filename
    print('> Sending to: ' + out_dir)
    sftp.put(movie, out_dir, callback=reportProgress)

    # Do check on delete
    if delete_on_process:
        print('> Deleting processed file: ' + filename)
        deleteFile(movie, False)


def uploadTV(file):
    print('> Processing new files...')

    filename = os.path.basename(file)
    # print('> Filename: ' + os.path.dirname(file))
    gi = guessit.guessit(filename)
    title = gi['title']
    capitalized_title = capitalize_name(title)

    out_dir = remote_tv_path + capitalized_title + '/' + filename

    # Test folder
    remote_path = remote_tv_path + title
    try:
        sftp.chdir(remote_path)  # Test if remote_path exists
    except IOError:
        print('> Found new show ({0})! Creating folder...'.format(title))
        sftp.mkdir(remote_path)  # Create remote_path
        sftp.chdir(remote_path)

    print('> Sending to: ' + out_dir)
    sftp.put(file, out_dir, callback=reportProgress)

    # Do check on delete
    # This will also delete entire folder even if there's more videos...
    if delete_on_process:
        print('> Deleting locally processed file: ' + filename)
        deleteFile(file, True)

    print('\n')

def checkLocalFolders():
    print('> Verifying local content...')
    if not os.path.exists(tv_path):
        os.makedirs(tv_path)

    if not os.path.exists(movie_path):
        os.makedirs(movie_path)

def prepareFiles(isTV, files):
    current_processed = 0 # Simple check to see if we have any new files

    if isTV:
        print('> Checking for TV files...')
    else:
        print('> Checking for Movie files...')

    if len(files) > 0:
        for file in files:
            if file not in regfiles:
                if not os.path.isdir(file) and os.path.isfile(file) and file.endswith(types):
                    regfiles.append(file)
                    current_processed += 1

                    print('[*] Registering new file: ' + file)
                    if isTV:
                        uploadTV(file)
                    else:
                        uploadMovie(file)

                else:
                    print('> Checking sub directories... ' + file)

                    for root, dirs, files in os.walk(file):
                        for vids in files:
                            if vids.endswith(types):
                                vid_loc = file + '\\' + vids
                                regfiles.append(vid_loc)
                                current_processed += 1

                                print('[*] Registering new file (in sub dir): ' + vid_loc)
                                if isTV:
                                    uploadTV(vid_loc)
                                else:
                                    uploadMovie(vid_loc)
    if current_processed == 0:
        print('> No new %s files found!\n' % ('TV' if isTV else 'Movie'))

try:
    while True:
        # Set the files to new ones to update
        files_tv = glob.glob(tv_path + '\*', recursive=True)
        files_movie = glob.glob(movie_path + '\*', recursive=True)

        print('\n')

        ctime = datetime.now().strftime('%H:%M:%S')
        print('######## Performing check... ({}) ########'.format(str(ctime)))
        # Register every current file to a list so we can compare
        print('> Performing file check...')

        prepareFiles(True, files_tv)
        prepareFiles(False, files_movie)

        checkLocalFolders() # Quality control

        time_left = str(float(time_sleep / 60.0)) # Calculate to minutes
        print('> Sleeping for ' + time_left + ' minute(s)...')
        time.sleep(time_sleep)

except KeyboardInterrupt:
    print('Quitting program...')

    sftp.close()
    transport.close()

except:
    print("Unexpected error: " + str(sys.exc_info()[0]))
    raise
