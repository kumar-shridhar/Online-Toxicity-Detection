import matplotlib.pyplot as plt
import numpy
from flask import Flask, request, render_template, flash, redirect, url_for, Response
from flask import make_response, jsonify
import sys
import os

import requests
import json
import threading
import time
import pandas as pd
import tempfile
import datetime
from collections import defaultdict 



sys.path.append(os.path.abspath("./"))
from apollo.Scraper.config import (
    LIMIT,
    OUTPUT_PATH,
    USER_AGENT,
    YOUTUBE_VIDEO_URL, return_id,
)

from apollo.Scraper.config import OUTPUT_PATH, update
from apollo.Scraper.LinkParser import extract_id
from apollo.Scraper.youtubeScraper import scrapper
from apollo.inference.inference import inference, inference_v2, load_model
from apollo.Scraper.download_comments import download_comments

app = Flask(__name__)
app.secret_key = os.urandom(24)
LOAD_MODEL_THREAD = None
CHART_DATA = [0, 0]
COMPLETED = False
LIMIT = 50
LOG_RESULT_DATA = None
LOG_DATA = ''
DATA_STORE = defaultdict(list)


COMMENTS_STORE = []

@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers["X-UA-Compatible"] = "IE=Edge,chrome=1"
    response.headers["Cache-Control"] = "public, max-age=0"
    # response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    # response.headers["Expires"] = 0
    # response.headers["Pragma"] = "no-cache"
    # response.headers['Cache-Control'] = 'no-store'
    return response


def scrape_data(COMMENT_LINK):
    update(COMMENT_LINK)

    output_file_name = scrapper()
    return output_file_name


def load_csv(COMMENT_LINK):

    output_file_name = scrape_data(COMMENT_LINK)
    outfile_path = OUTPUT_PATH + "/" + output_file_name
    return outfile_path


def final_infer(COMMENT_LINK, SENSITIVITY):

    outfile_path = load_csv(COMMENT_LINK)
    VALUES = inference(outfile_path, SENSITIVITY)
    return VALUES

def scrapper_v2(youtube_id, sensitivity, limit):
    try:
        # if LOAD_MODEL_THREAD is not None:
        LOAD_MODEL_THREAD.join()
        global CHART_DATA
        global COMPLETED
        global LOG_RESULT_DATA
        global LOG_DATA
        global COMMENTS_STORE
        global DATA_STORE
        
        filename = '{}_{}_{}.csv'.format(youtube_id, sensitivity, limit)

        CHART_DATA = [0, 0]
        COMPLETED = False
        LOG_RESULT_DATA = None
        LOG_DATA = ''
        COMMENTS_STORE = []

        df = pd.DataFrame(columns=['id', 'comment', 'score', 'sensitivity'])
        toxic_count, nontoxic_count = 0 , 0
        count_list = []
        comment_list = []
        score_list = []
        sensitivity_list = []

        if not youtube_id:
            LOG_DATA = 'error'
            COMPLETED = True
            CHART_DATA = [0, 0]
            COMMENTS_STORE = []
            raise ValueError("you need to specify a Youtube ID")

        print("Downloading Youtube comments for video:", youtube_id)

        count = 0
        session = requests.Session()
        session.headers["User-Agent"] = USER_AGENT
        response = session.get(YOUTUBE_VIDEO_URL.format(youtube_id=youtube_id))
        html = response.text
        if "og:title" in html:
            for comment in download_comments(youtube_id):
                comment_content = comment['content']
                score = inference_v2(comment_content, sensitivity)
                count += 1
                count_list.append(count)
                comment_list.append(comment_content)
                score_list.append(score)
                sensitivity_list.append(sensitivity)

                if score > (sensitivity):
                    toxic_count += 1
                else:
                    nontoxic_count +=1
                # CHART_DATA = [(toxic_count / (toxic_count + nontoxic_count)) * 100, (nontoxic_count / (toxic_count + nontoxic_count)) * 100]
                CHART_DATA = [toxic_count, nontoxic_count]
                LOG_DATA = ' '.join(['[' + str(count) + ']', str(comment_content), 'score: ' + str(score)])
                EXTRA_LOG_DATA = [comment['content'], comment['time'], comment['author'], comment['votes'], comment['photo'], str(score)]
                COMMENTS_STORE.append(EXTRA_LOG_DATA)
                

                if limit and count >= limit:
                    COMPLETED = True
                    DATA_STORE[youtube_id].append({'chart_data':CHART_DATA, 'extra_log_data': EXTRA_LOG_DATA, 'task_finished': True, 'success': True, 'index': count, 'filename': filename})
                    df['id'], df['comment'], df['score'], df['sensitivity'] = count_list, comment_list, score_list, sensitivity_list
                    LOG_RESULT_DATA = filename
                    filepath = os.path.abspath(os.path.join('./', 'downloads', filename))
                    df.to_csv(filepath, encoding='utf-8')
                    break
                else:
                    DATA_STORE[youtube_id].append({'chart_data':CHART_DATA, 'extra_log_data': EXTRA_LOG_DATA, 'task_finished': False, 'success': True, 'index': count, 'filename': filename})



                print(comment_content, toxic_count, nontoxic_count, score)
                sys.stdout.write("Downloaded %d comment(s)\r" % count)
                sys.stdout.flush()
                
            print("\nDone!")

        else:
            print(f"The provided YouTube ID : {youtube_id} is invalid! ")
            DATA_STORE[youtube_id].append({'chart_data':[], 'extra_log_data': [], 'task_finished': True, 'success': False, 'index': -1, 'filename': ''})
            LOG_DATA = 'error'
            COMPLETED = True
            CHART_DATA = [0, 0]
            COMMENTS_STORE = []

    except Exception as e:
        print("Error:", str(e))
        sys.exit(1)


@app.route('/chart2-data')
def chart2_data():
    def send_processed_data():
        global COMPLETED
        while True:
            json_data = json.dumps({'toxic_data': CHART_DATA, 'processed': COMPLETED, 'log_message': LOG_DATA, 'result_file': LOG_RESULT_DATA})
            yield f"data:{json_data}\n\n"
            if COMPLETED:
                return
            time.sleep(1)

    return Response(send_processed_data(), mimetype='text/event-stream')


@app.route('/chart-data', methods=['GET'])
def chart_data():
    if request.method == 'GET':
        url = request.args.get('url')
        youtube_id = extract_id(url)

    def send_data(youtube_id):
        while len(DATA_STORE[youtube_id])>0:
            json_data = json.dumps(DATA_STORE[youtube_id].pop(0))
            yield f"data:{json_data}\n\n"
            time.sleep(1)

    return Response(send_data(youtube_id), mimetype='text/event-stream')


@app.route('/log-data')
def log_data():
    def send_log_data():
        while len(COMMENTS_STORE)>0:
            json_data = json.dumps({'log_data': COMMENTS_STORE.pop(0)})
            yield f"data:{json_data}\n\n"
            time.sleep(1)

    return Response(send_log_data(), mimetype='text/event-stream')


@app.route("/about.html")
def about():
    return render_template("about.html")


@app.route("/index.html")
def home_index():
    response = make_response(render_template("index.html"))
    response = add_header(response)
    return response


@app.route("/")
def home():
    global LOAD_MODEL_THREAD
    LOAD_MODEL_THREAD = threading.Thread(target=load_model, args=())
    LOAD_MODEL_THREAD.daemon = True
    LOAD_MODEL_THREAD.start()
    # cache.clear()
    response = make_response(render_template("index.html"))
    response = add_header(response)
    return response



@app.route('/predict',methods=['GET', 'POST'])
def predict():
    print('STARTING PREDICTION*********************')
    '''
    For rendering results on HTML GUI
    '''
    global COMPLETED
    global LIMIT

    COMPLETED = False
    COMMENT_URL = [x for x in request.form.values()]
    print('This..........', COMMENT_URL)
    if len(COMMENT_URL[0]) == 0:
        return jsonify(msg='URL missing', status='error')
    
    COMMENT_LINK = extract_id(COMMENT_URL[0])
    SENSITIVITY = float(COMMENT_URL[1])
    LIMIT = int(COMMENT_URL[2])
    if COMMENT_LINK is None:
        print("Invalid link or the link is not supported yet.")
        '''
        Add a function to show the error message in html page
        '''
        return render_template('index.html',name ='')

    else:
        print (COMMENT_LINK)
    
    scrapper_v2(COMMENT_LINK, SENSITIVITY, LIMIT)
    
    return jsonify(msg='scraping successfully', status='success')



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8082, debug=True, threaded=True)
