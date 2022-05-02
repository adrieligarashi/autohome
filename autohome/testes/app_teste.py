from flask import Flask, render_template
from autohome.news_analysis import News
from autohome.music_player import MusicPlayer

app = Flask(__name__)

news = News()
positive, neutral, negative = news.get_news_by_sentiment()

sp = MusicPlayer()
uri, _ = sp.create_custom_playlist(mood='happy')
token = sp.auth.get_cached_token()['access_token']


@app.route('/')
def index():
    return render_template('index_teste.html',
                           title=negative[0]['title'],
                           article=negative[0]['text'],
                           token=token,
                           site=negative[0]['url'],
                           playlist=uri,
                           felling_spotify='happy'
                           )

@app.route('/news')
def newspage():
    return render_template('news_page.html',
                           title=negative[0]['title'],
                           )

if __name__ == '__main__':
    app.run()
