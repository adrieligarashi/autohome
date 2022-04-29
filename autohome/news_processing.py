from newspaper import Article
from pygooglenews import GoogleNews
from googletrans import Translator


def get_news_from_google_feed(n=5):
    # Pega a url das n principais noticias do RSS do Google News
    gn = GoogleNews(country='BR', lang='pt')

    top_news = gn.top_news()['entries']

    links = [top_news[i]['link'] for i in range(n)]

    # Pega o conteudo das noticias
    noticias = {}
    for i, url in enumerate(links):
        article = Article(url, language='pt', fetch_images=False)
        article.download()
        article.parse()

        text = article.text
        text = text.replace('\n', ' ')
        text = text.strip()

        noticias[i] = {'title': article.title,
                       'text': text}

    return noticias


def translate_title(noticias: dict):
    translator = Translator()

    for content in noticias.values():
        trans = translator.translate(content['title'], src='pt', dest='en')
        content['translation'] = trans.text

    return noticias

if __name__ == '__main__':

    noticias = get_news_from_google_feed()
    noticias = translate_title(noticias)

    print(noticias[0])
