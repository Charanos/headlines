import os
import json
import feedparser
import urllib.parse
import urllib.request
from flask import Flask, render_template, session, request


app = Flask(__name__)
app.secret_key = 'dev'

rss_feeds = {
    'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
    'cnn': 'http://rss.cnn.com/rss/edition.rss',
    'fox': 'http://feeds.foxnews.com/foxnews/latest',
    'iol': 'http://www.iol.co.za/cmlink/1.640'
}


def get_weather(query):
    api_url = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=fea3eec3aef8e1bac0473be01228c0a6"
    query = urllib.parse.quote(query)
    url = api_url.format(query)
    data = urllib.request.urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get('weather'):
        weather = {
            "city": parsed["name"],
            "temparature": parsed["main"]["temp"],
            "description": parsed["weather"][0]["description"]
        }
    return weather


@app.route('/')
def get_news():
    query = request.args.get('publication')
    if not query or query.lower() not in rss_feeds:
        publication = 'bbc'
    else:
        publication = query.lower()

    feed = feedparser.parse(rss_feeds[publication])
    weather = get_weather("Machakos, KE")
    return render_template('index.html', weather=weather, rss_feeds=rss_feeds, articles=feed['entries'])


if __name__ == '__main__':
    app.run(port=5000, debug=True)
