'''
Authors:
Kumar Shridhar <shridhar.stark@gmail.com>
Venkatesh Iyer <iyervenkatesh92@gmail.com>
Ritu Yadav <er.ritu92@gmail.com>

Code modified from : https://github.com/egbertbouman/youtube-comment-downloader

'''

from __future__ import print_function

import io
import json
import os
import sys
import uuid
import shutil

import requests

from apollo.Scraper.config import YOUTUBE_ID, LIMIT, YOUTUBE_VIDEO_URL, USER_AGENT
from apollo.Scraper.download_comments import download_comments
from apollo.Scraper.helper import read_json, write_csv


def scrapper():

    try:
        youtube_id = YOUTUBE_ID
        output = str(youtube_id)+"_"+str(uuid.uuid1())
#         output = args.output
        limit = LIMIT

        if not youtube_id or not output:
            raise ValueError('you need to specify a Youtube ID and an output filename')

        print('Downloading Youtube comments for video:', youtube_id)
        count = 0

        # Get Youtube page with initial comments
        session = requests.Session()
        session.headers['User-Agent'] = USER_AGENT
        # Get Youtube page with initial comments
        response = session.get(YOUTUBE_VIDEO_URL.format(youtube_id=youtube_id))
        # print(response)
        html = response.text
        if "og:title" in html:

            with io.open(output, 'w', encoding='utf8') as fp:
                sys.stdout.write('Downloaded %d comment(s)\r' % count)
                sys.stdout.flush()

                for comment in download_comments(youtube_id):
                    comment_json = json.dumps(comment, ensure_ascii=False)
                    print(comment_json.decode('utf-8') if isinstance(comment_json, bytes) else comment_json, file=fp)
                    count += 1
                    sys.stdout.write('Downloaded %d comment(s)\r' % count)
                    sys.stdout.flush()
                    if limit and count >= limit:
                        break
            print('\nDone!')

            output_filename= output+'.csv'
            write_csv(read_json(output), output_filename)
            os.remove(output)
            # Take path parameter from config file
            os.remove(output_filename)

        else:
            print (f'The provided YouTube ID : {youtube_id} is invalid! ')

    except Exception as e:
        print('Error:', str(e))
        sys.exit(1)


if __name__ == "__main__":
    scrapper()
