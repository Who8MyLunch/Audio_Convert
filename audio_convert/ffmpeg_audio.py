
from __future__ import division, print_function, unicode_literals

import time
import argparse
import glob
import os
import shutil

import subprocess

import mutagen

def run_cmd(cmd, path_work=None):
    """
    Run an external program via command line arguments.
    Capture stdout and stderr.
    No stdin.
    """

    # Configure.
    si = subprocess.STARTUPINFO()
    si.dwFlags = subprocess.STARTF_USESHOWWINDOW

    # http://msdn.microsoft.com/en-us/library/ms633548(v=vs.85).aspx
    si.wShowWindow = 0    # Hide
    # si.wShowWindow = 5  # Show
    # si.wShowWindow = 6  # Minimize

    cf = subprocess.CREATE_NEW_CONSOLE

    # Do it.
    proc = subprocess.Popen(cmd, startupinfo=si, creationflags=cf,
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=path_work)

    std_out, std_err = proc.communicate()

    # Done.
    return std_out, std_err



def convert(fname_src, verbose=False):
    """
    Convert a single audio file.
    """
    if not os.path.isfile(fname_src):
        raise IOError('File not found: %s' % fname_src)

    # File names.
    b, e = os.path.splitext(fname_src)
    fname_dst = b + '.m4a'

    # Build command.
    cmd = 'ffmpeg -y -i "%s" "%s"' % (fname_src, fname_dst)

    t0 = time.time()
    std_out, std_err = run_cmd(cmd)
    dt = time.time() - t0

    if dt < 0.01:
        raise Exception('Problem processing file: %s %s %s %s' % (fname_src, std_out, std_err, cmd))

    if std_out.lower().find('error') >= 0:
        raise Exception('Problem processing file: %s %s %s %s' % (fname_src, std_out, std_err, cmd))

    # Done.
    return fname_dst



def move_processed_file(fname):
    p_src = os.path.dirname(fname)
    f_src = os.path.basename(fname)

    p_dst = os.path.join(p_src, '.audio_convert')
    if not os.path.isdir(p_dst):
        os.mkdir(p_dst)

    f = os.path.join(p_dst, os.path.basename(fname))
    if os.path.isfile(f):
        os.remove(f)

    shutil.move(fname, p_dst)


def view_metadata_wma(fname_wma):

    meta = mutagen.File(fname_wma, easy=True)

    tags_map = {'Title': 'Title',
                'Author': 'Author',
                'Description': 'Description',
                'WM/Composer': 'Composer',
                'WM/Publisher': 'Publisher',
                'WM/Year': 'Year',
                'WM/AlbumTitle': 'AlbumTitle',
                'WM/AlbumArtist': 'AlbumArtist',
                'MusicBrainz/Album Type': 'MusicBrainz/Album Type',
                'MusicBrainz/Track Id': 'MusicBrainz/Track Id',
                'MusicBrainz/Artist Id': 'MusicBrainz/Artist Id',
                'MusicBrainz/Album Artist Id': 'MusicBrainz/Album Artist Id',
                'MusicBrainz/Album Id': 'MusicBrainz/Album Id',
                'MusicBrainz/Original Album Id': 'MusicBrainz/Original Album Id',
                'Acoustid/Id': 'Acoustid/Id'}

    tags_matched = {}
    tags_available = {}
    tags_other = {}

    for k, v in meta.items():
        v = v[0]
        if type(v) == mutagen.asf.ASFUnicodeAttribute or type(v) == unicode or type(v) == str:
            if k in tags_map:
                tags_matched[k] = v
            else:
                tags_available[k] = v
        else:
            tags_other[k] = v

    # Print.
    print('\nMatched')
    for k, v in tags_matched.items():
        print('%s: %s' % (k, v))

    print('\nAvailable')
    for k, v in tags_available.items():
        print('%s: %s' % (k, v))

    print('\nOther')
    for k, v in tags_other.items():
        print(k, v, type(v))








def main_convert():
    """
    This is the main application.

    Convert wma files to mp3 files.
    """

    verbose = True

    # Build parser.
    parser = argparse.ArgumentParser()

    parser.add_argument('fname_pattern', action='store', help='File name pattern')
    parser.add_argument('-R', '--recursive', action='store_true', default=True,
                        help='Search several subdirectories')

    # Run parser, extract arguments.
    args = parser.parse_args()

    # List of files.
    pattern = os.path.normpath(unicode(args.fname_pattern))

    if os.path.isdir(pattern):
        pattern = os.path.join(pattern, '*')
        fname_list = glob.glob(pattern)

        pattern = os.path.join(pattern, '*')
        fname_list.extend(glob.glob(pattern))

        pattern = os.path.join(pattern, '*')
        fname_list.extend(glob.glob(pattern))

        pattern = os.path.join(pattern, '*')
        fname_list.extend(glob.glob(pattern))

    else:
        fname_list = glob.glob(pattern)

    to_be_removed = []
    for f in fname_list:
        if os.path.isdir(f):
            to_be_removed.append(f)

    for f in to_be_removed:
        fname_list.remove(f)

    # Do the work.
    num_files = len(fname_list)
    for k, f_src in enumerate(fname_list):
        f_src = os.path.abspath(f_src)

        b_src, e = os.path.splitext(f_src)

        folder = os.path.basename(os.path.dirname(f_src))
        if (e == '.mp3' or e == '.wma' or e == '.wav' or e == '.aiff') and b_src != 'tmp' and folder != '.audio_convert':

            if verbose:
                try:
                    print('%3d/%d: [%s -> .m4a] %s' % (k, num_files, e, os.path.basename(b_src)))
                except Exception as e:
                    val = repr(f_src)
                    raise Exception('Problem processing file: %s' % val)

            # Temporary working copy.
            path_work = os.path.dirname(f_src)
            f_tmp_src = os.path.join(path_work, 'tmp' + e)
            shutil.copy(f_src, f_tmp_src)

            # Transcode file format.
            f_tmp_dst = convert(f_tmp_src, verbose=verbose)

            # Finish.
            b_tmp_dst, e_dst = os.path.splitext(f_tmp_dst)

            f_dst = b_src + e_dst
            if os.path.isfile(f_dst):
                os.remove(f_dst)
            os.rename(f_tmp_dst, f_dst)

            if os.path.isfile(f_tmp_src):
                os.remove(f_tmp_src)

            if os.path.isfile(f_dst):
                move_processed_file(f_src)

    # Done.


if __name__ == '__main__':
    main_covert()
