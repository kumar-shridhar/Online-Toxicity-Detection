import matplotlib.pyplot as plt
from flask import Flask, request, render_template
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import sys

sys.path.append('..')
from apollo.Scraper.config import update_youtube_id, OUTPUT_PATH
from apollo.Scraper.youtubeScraper import scrapper
#from apollo.inference.inference import inference




app = Flask(__name__)

def scrape_data(COMMENT_LINK):
    update_youtube_id(COMMENT_LINK)

    output_file_name = scrapper()
    return output_file_name

def load_csv(COMMENT_LINK):

    output_file_name = scrape_data(COMMENT_LINK)
    outfile_path = OUTPUT_PATH + '/' + output_file_name
    return outfile_path

def final_infer(COMMENT_LINK):

    outfile_path = load_csv(COMMENT_LINK)
    VALUES = inference(outfile_path)
    return (VALUES)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict',methods=['POST'])
def predict():
    '''
    For rendering results on HTML GUI
    '''

    COMMENT_LINK = request.form.values()
    global output
    output = final_infer(COMMENT_LINK)

    names = ['Toxic', 'Non-Toxic']
    values = []
    values.append(output[0]/output[0] + output[1])
    values.append(output[1] / output[0] + output[1])

    fig1, ax1 = plt.subplots()
    ax1.pie(values, labels=names)
    ax1.axis('equal')
    plt.savefig('static/images/new_plot.png')
    return render_template('index.html',name ='new_plot.png')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8082, debug=True)