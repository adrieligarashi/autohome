from flask import Flask, render_template
from autohome.news_analysis import News

app = Flask(__name__)

news = News()
news.get_news()


@app.route('/')
def index():
    return render_template('index_teste.html',
                           articles=news.news[0])


if __name__ == '__main__':
    app.run()
