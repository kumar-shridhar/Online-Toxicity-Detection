'''
Authors:
Kumar Shridhar <shridhar.stark@gmail.com>
Venkatesh Iyer <iyervenkatesh92@gmail.com>
Ritu Yadav <er.ritu92@gmail.com>

Code modified from : https://github.com/egbertbouman/youtube-comment-downloader

'''

import time
import json, csv


def find_value(html, key, num_chars=2, separator='"'):
    pos_begin = html.find(key) + len(key) + num_chars
    pos_end = html.find(separator, pos_begin)
    return html[pos_begin: pos_end]


def ajax_request(session, url, params=None, data=None, headers=None, retries=5, sleep=20):
    for _ in range(retries):
        response = session.post(url, params=params, data=data, headers=headers)
        if response.status_code == 200:
            return response.json()
        if response.status_code == 400:
            return print(f'Error: {response.status_code}. Make sure the entered YouTube ID is correct.')
        if response.status_code in [403, 413]:
            return print(f'Error: {response.status_code}')
        else:
            time.sleep(sleep)



def search_dict(partial, key):
    if isinstance(partial, dict):
        for k, v in partial.items():
            if k == key:
                yield v
            else:
                for o in search_dict(v, key):
                    yield o
    elif isinstance(partial, list):
        for i in partial:
            for o in search_dict(i, key):
                yield o
                
def read_json(filename):
    return [json.loads(line) for line in open(filename, 'r')]

def write_csv(data,filename):
    with open(filename, 'w+') as outf:
        writer = csv.DictWriter(outf, data[0].keys())
        writer.writeheader()
        for row in data:
            writer.writerow(row)