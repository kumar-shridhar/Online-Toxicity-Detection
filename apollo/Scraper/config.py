"""
Authors:
Kumar Shridhar <shridhar.stark@gmail.com>
Venkatesh Iyer <iyervenkatesh92@gmail.com>
Ritu Yadav <er.ritu92@gmail.com>

Code modified from : https://github.com/egbertbouman/youtube-comment-downloader

"""

import os

def update(id):
    global YOUTUBE_ID
    YOUTUBE_ID = id

def return_id():
    return YOUTUBE_ID


YOUTUBE_VIDEO_URL = "https://www.youtube.com/watch?v={youtube_id}"
YOUTUBE_COMMENTS_AJAX_URL_OLD = "https://www.youtube.com/comment_ajax"
YOUTUBE_COMMENTS_AJAX_URL_NEW = "https://www.youtube.com/comment_service_ajax"

# The OUTPUT_PATH will point to temporary place for script processing. 
# Change when deploying
OUTPUT_PATH = ""

# Development time update
if os.name == 'nt':
    OUTPUT_PATH = "C:\\AKRAM-Local\\github\\Apollo\\Frontend\\working"
else:
    OUTPUT_PATH = os.environ['HOME']

LIMIT = 50

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
