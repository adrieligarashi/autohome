import openai
import os
import regex as re

from dotenv import find_dotenv, load_dotenv
from newspaper import Article
from pygooglenews import GoogleNews
from googletrans import Translator


def get_news_from_google_feed(n=5):
    '''
    Gets the n top news from Google News RSS Brazil, in portuguese.
    ----------
    Returns: - Dict:
                - n: From 0 to n news
                    - title: The title of the article
                    - text: The text of the article
    '''
    gn = GoogleNews(country='BR', lang='pt')
    top_news = gn.top_news()['entries']
    links = [top_news[i]['link'] for i in range(n)]

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
    '''
    Receives the dict from get_news_from_google_feed, translates the title to
    english and returns the same dictionary with a new 'translation' key.
    --------------
    Receives: - Dict: {n: {'title': , 'text': }}
    --------------
    Returns: - Dict:
                - n: from 0 to n news
                    - title: The title of the article
                    - text: The text of the article
                    - translation: The title translated to english
    '''
    translator = Translator()

    for content in noticias.values():
        trans = translator.translate(content['title'], src='pt', dest='en')
        content['translation'] = trans.text

    return noticias


def get_sentiment_of_news(noticias):
    '''
    Receives the dict with translated title from translate_title, sends the title
    to OpenAI API and returns the same dictionary with a new 'sentiment' key.
    -----------
    Receives: - Dict: {n: {'title': , 'text': , 'translation': }}
    -----------
    Returns: -Dict:
                - n: from 0 to n news
                    - title: The title of the article
                    - text: The text of the article
                    - translation: The title translated to english
                    - sentiment: The news' title classified in Positive, Neutral
                                 or Negative
    '''
    path = find_dotenv()
    load_dotenv(path)
    openai.api_key = os.environ.get('OPENAI_API_KEY')

    phrases = [f'{content["translation"]}' for content in noticias.values()]

    prompt = 'Classify in positive, neutral or negative the sentiment in these phrases:\n\n'
    for i, phrase in enumerate(phrases):
        prompt = prompt + f'{i+1}. "{phrase}"\n'
    prompt = prompt + '\nPhrases sentiment ratings:\n'


    res = openai.Completion.create(
        engine='text-davinci-002',
        prompt=prompt,
        temperature=0,
        max_tokens=60,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )

    classif = res['choices'][0]['text'].strip().split('\n')
    clean_classif = [re.sub('\d. ', '', sentiment) for sentiment in classif]

    for i, sentiment in enumerate(clean_classif):
        noticias[i]['sentiment'] = sentiment

    return noticias


if __name__ == '__main__':

    noticias = get_news_from_google_feed()
    noticias = translate_title(noticias)
    noticias = get_sentiment_of_news(noticias)

    print(noticias[0])
