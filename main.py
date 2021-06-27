import os
import feedparser
from flask import Flask, render_template, session, request


app = Flask(__name__)
app.secret_key = 'dev'

rss_feeds = {
    'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
    'cnn': 'http://rss.cnn.com/rss/edition.rss',
    'fox': 'http://feeds.foxnews.com/foxnews/latest',
    'iol': 'http://www.iol.co.za/cmlink/1.640'
}


@app.route('/')
@app.route('/<publication>')
def get_news(publication='bbc'):
    feed = feedparser.parse(rss_feeds[publication])
    return render_template('index.html', articles=feed['entries'])


if __name__ == '__main__':
    app.run(port=5000, debug=True)
