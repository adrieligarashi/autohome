from newspaper import Article
from pygooglenews import GoogleNews


def get_news_text_from_google_feed(n=5):
    # Pega a url das n principais noticias do RSS do Google News
    gn = GoogleNews(country='BR', lang='pt')

    top_news = gn.top_news()['entries']

    links = [top_news[i]['link'] for i in range(n)]

    # Pega o conteudo das noticias
    textos = []
    keywords = []
    for url in links:
        article = Article(url, language='pt')
        article.download()
        article.parse()
        article.nlp()

        texto = article.text
        texto = texto.replace('\n', ' ')
        texto = texto.strip()

        textos.append(texto)
        keywords.append(article.keywords)

    return textos, keywords

if __name__ == '__main__':

    textos, kws = get_news_text_from_google_feed()
    print(repr(textos[0]))
    print(kws[0])
