import matplotlib.pyplot as plt
import numpy
from flask import Flask, request, render_template, flash, redirect, url_for
from flask import make_response
import sys
import os

sys.path.append("..")

from Scraper.config import OUTPUT_PATH, update
from Scraper.LinkParser import extract_id
from Scraper.youtubeScraper import scrapper
from inference.inference import inference

app = Flask(__name__)
app.secret_key = os.urandom(24)


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
    # cache.clear()
    response = make_response(render_template("index.html"))
    response = add_header(response)
    return response


@app.route("/predict", methods=["POST"])
def predict():
    """
    For rendering results on HTML GUI
    """
    # cache.clear()
    COMMENT_URL = [x for x in request.form.values()]
    COMMENT_LINK = extract_id(COMMENT_URL[0])
    SENSITIVITY = int(COMMENT_URL[1])
    if COMMENT_LINK is None:
        print("Invalid link or the link is not supported yet.")
        """
        Add a function to show the error message in html page
        """
        flash("Invalid link or the link is not supported yet.")
        return redirect(url_for("home_index"))

    else:
        print(COMMENT_LINK)

    global output
    output = final_infer(COMMENT_LINK, SENSITIVITY)

    names = ["Toxic", "Non-Toxic"]
    values = output

    static_path = './apollo/Frontend/static/images/'
    # Bar plot
    x = numpy.arange(2)
    fig, ax = plt.subplots()
    plt.bar(2, values)
    plt.xticks(x, ("Toxic", "Non-Toxic"))
    if os.name == "nt":
        plt.savefig("static\\images\\new_plot.png", transparent=True)
    else:
        plt.savefig(static_path + "new_plot.png", transparent=True)

    # Pie chart, where the slices will be ordered and plotted counter-clockwise:
    labels = "Toxic", "Non-Toxic"
    sizes = output
    explode = (0.1, 0.1)  # only "explode" the 1st slice
    fig2, ax2 = plt.subplots()
    ax2.pie(
        sizes,
        explode=explode,
        labels=labels,
        autopct="%1.1f%%",
        colors={"red", "blue"},
        shadow=True,
        startangle=90,
    )
    ax2.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle.
    if os.name == "nt":
        plt.savefig("static\\images\\new_pie.png", transparent=True)
    else:
        plt.savefig(static_path + "new_pie.png", transparent=True)
    response = make_response(render_template("index.html", name="new_pie.png"))
    response = add_header(response)
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8082, debug=True, threaded=True)
