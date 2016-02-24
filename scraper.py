# Copyright (c) 2016, Alexander Lim
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Download all of the Planet Money MP3s.

Honestly this program is pretty fragile and requires you already have a
list of URLs to scrape from which you can get from the Planet Money
podcast archive, and the MP3s it downloads aren't tagged correctly. Just
needed something that worked.
"""

from __future__ import print_function

import os
import re
import sys

import requests


def get_url_list(filename):
    """
    Get the URLs to scrape from the given file.

    URLs should be line-separated. If no such URLs exist or there is an
    error opening the file, returns an empty list.
    """
    try:
        with open(filename) as f:
            # readlines() returns filenames with newline characters.
            newlines_removed = map(lambda x: x.decode('utf8').rstrip('\n'),
                                   f.readlines())
            # Just in case any blank lines were in the file.
            empty_lines_removed = filter(lambda x: x, newlines_removed)
            return list(empty_lines_removed)
    except EnvironmentError:
        return []


def scrape(urls, dest_folder):
    """Scrape the given list of URLs for podcast MP3s and download them."""
    for url in urls:
        r = requests.get(url)
        if r.status_code == requests.codes.ok:
            download_mp3s(r.text, dest_folder)
        else:
            print('failed: {}', url)


def download_mp3s(text, dest_folder):
    """
    Download all of the Planet Money MP3 files found on the page.

    Uses a regex to determine if a link is a download link; probably not
    future-proof, but this is a one-off script anyway.
    """
    regex = re.compile(r'http://pd\.npr\.org/anon\.npr-mp3/npr/[A-Za-z]+/\d{4}'
                       r'/\d{2}/\d{8}.+\.mp3', re.UNICODE)
    results = regex.findall(text, re.UNICODE)
    for url in results:
        download(url, dest_folder)


def download(url, dest_folder):
    """
    Download a file to the given destination folder.

    The resulting name for the file will be taken from the last
    component of the download URL, determined by taking the remaining
    substring after the last slash ('/'). Whether the download
    succeeded or failed will be printed to standard output.
    """
    r = requests.get(url, stream=True)
    mp3_name = url.rsplit('/')[-1]
    filename = os.path.join(dest_folder, mp3_name)
    try:
        # Code taken from requests documentation.
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(1024):
                if chunk:
                    f.write(chunk)
    except EnvironmentError:
        print('failed: {}'.format(url))
    else:
        print('downloaded: {}'.format(url))


def main():
    """Script entry point."""
    urls = get_url_list('urls.txt')
    dest_folder = '.' if len(sys.argv) < 2 else sys.argv[1]
    scrape(urls, dest_folder)


if __name__ == '__main__':
    main()
