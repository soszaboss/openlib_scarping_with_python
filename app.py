from flask import Flask, redirect, render_template, request, url_for
import json

from main import get_paginations_links, scrape



app = Flask(__name__)


def get_data(page=1): 
    data = None
    try:
        data = json.load(open(f"scraped_data/page_{page}.json"))
    except FileNotFoundError:
        pass
    return data
    


@app.route("/")
def index():
    page = request.args.get("page", "1")
    if page.isdigit == False:
        page = 1
    page_numbers = 9
    if int(page) > page_numbers:
        page = page_numbers
    if int(page) < 1:
        page = 1
    
    data = get_data(page)
    if data == None:
        return redirect(url_for("start_scrape"))
    return render_template("index.html", data=data, page_numbers=page_numbers, page=int(page))


@app.route("/scrape")
def scrape_data():
    data = get_data()
    if data != None:
        return data
    base_url = "https://openlibrary.org"
    paginations_links = get_paginations_links(f"{base_url}/trending/forever")
    data = scrape(paginations_links, base_url)
    return data

@app.route("/start_scrape")
def start_scrape():
    return render_template("scraping.html")

if __name__ == "__main__":
    app.run(debug=True)