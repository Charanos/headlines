import os
import json
import datetime
import feedparser
import urllib.parse
import urllib.request
from flask import Flask, render_template, session, request, make_response


app = Flask(__name__)
app.secret_key = 'dev'

rss_feeds = {
    'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
    'cnn': 'http://rss.cnn.com/rss/edition.rss',
    'fox': 'http://feeds.foxnews.com/foxnews/latest',
    'iol': 'http://www.iol.co.za/cmlink/1.640'
}

defaults = {
    "publication": "bbc",
    "city": "Nairobi, KE",
    "currency_to": "USD",
    "currency_from": "KES",
}


def get_news(query):
    """ Get new from user selection or present defaults """

    if not query or query.lower() not in rss_feeds:
        news_feed = defaults['publication']
    else:
        news_feed = query.lower()

    feed = feedparser.parse(rss_feeds[news_feed])
    return feed['entries']


def get_rates(frm, to):
    """ get latest currency rates from api and return to user """

    currency_url = "http://data.fixer.io/api/latest?access_key=2b1092f749f853eaa52e415c47e3504a"
    data = urllib.request.urlopen(currency_url).read()
    parsed = json.loads(data).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return (to_rate/frm_rate, parsed.keys())


def get_weather(query):
    """ Get current weather from api selection or present defaults """

    api_url = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=fea3eec3aef8e1bac0473be01228c0a6"
    query = urllib.parse.quote(query)
    url = api_url.format(query)
    data = urllib.request.urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get('weather'):
        weather = {
            "city": parsed["name"],
            "country": parsed['sys']['country'],
            "temparature": parsed["main"]["temp"],
            "description": parsed["weather"][0]["description"]
        }
    return weather


@app.route('/')
def index():
    # get customized headlines based on user selection or default
    publication = request.args.get('publication')
    if not publication:
        publication = request.cookies.get('publication')
        if not publication:
            publication = defaults['publication']

    articles = get_news(publication)

    # get customized weather based upon user input or default
    city = request.args.get('city')
    if not city:
        city = request.cookies.get('city')
        if not publication:
            city = defaults['city']

    weather = get_weather(city)

    # get customized currency based on user input or default
    currency_to = request.args.get("currency_to")
    if not currency_to:
        currency_to = request.cookies.get('currency_to')
        if not currency_to:
            currency_to = defaults['currency_to']

    currency_from = request.args.get("currency_from")
    if not currency_from:
        currency_from = request.cookies.get('currency_from')
        if not currency_from:
            currency_from = defaults['currency_from']

    rate, currencies = get_rates(currency_from, currency_to)

    response_str = make_response(
        render_template('index.html',
                        rate=rate,
                        weather=weather,
                        articles=articles,
                        rss_feeds=rss_feeds,
                        currency_to=currency_to,
                        currency_from=currency_from,
                        currencies=sorted(currencies)
                        ))
    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response_str.set_cookie("city", city, expires=expires)
    response_str.set_cookie("publication", publication, expires=expires)
    response_str.set_cookie("currency_from", currency_from, expires=expires)
    response_str.set_cookie("currency_to", currency_to, expires=expires)

    return response_str


if __name__ == '__main__':
    app.run(port=5000, debug=True)
