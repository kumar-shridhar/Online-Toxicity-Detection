'''
Authors:
Kumar Shridhar <shridhar.stark@gmail.com>
Venkatesh Iyer <iyervenkatesh92@gmail.com>
Ritu Yadav <er.ritu92@gmail.com>

Code modified from : https://github.com/egbertbouman/youtube-comment-downloader

'''

from __future__ import print_function

import argparse
import io
import json
import sys
import uuid
import shutil

from apollo.Scraper.config import OUTPUT_PATH
from apollo.Scraper.download_comments import download_comments
from apollo.Scraper.helper import read_json, write_csv


def scrapper():
   
    try:
        youtube_id = YOUTUBE_ID
        output = str(youtube_id)+"_"+str(uuid.uuid1())
#         output = args.output
        limit = LIMIT

        if not youtube_id or not output:
            parser.print_usage()
            raise ValueError('you need to specify a Youtube ID and an output filename')

        print('Downloading Youtube comments for video:', youtube_id)
        count = 0
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
        shutil.copy(output_filename,OUTPUT_PATH)
        os.remove(output_filename)

    except Exception as e:
        print('Error:', str(e))
        sys.exit(1)


if __name__ == "__main__":
    scrapper()
