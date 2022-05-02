import openai
import os
import regex as re

from dotenv import find_dotenv, load_dotenv
from newspaper import Article
from pygooglenews import GoogleNews
from googletrans import Translator


'''
This module is designed to fetch the top trending news in the Google News' RSS
and analyze the sentiment of them.
'''
class News():

    def __init__(self):

        gn = GoogleNews(country='BR', lang='pt')
        self.top_news = gn.top_news()['entries']

        self.news = None


    def get_top_news(self, n=5):
        '''
        Gets the n top news from Google News RSS Brazil, in portuguese and
        organizes it in a dictionary.
        '''
        links = [self.top_news[i]['link'] for i in range(n)]

        for i, url in enumerate(links):
            article = Article(url, language='pt', fetch_images=False)
            article.download()
            article.parse()

            text = article.text
            text = text.replace('\n', ' ')
            text = text.strip()

            self.news[i] = {'url': article.url,
                            'title': article.title,
                            'text': text
                           }


    def translate_titles(self):
        '''
        Receives the dict from get_news_from_google_feed, translates the title to
        english and returns the same dictionary with a new 'translation' key.
        '''
        translator = Translator()

        for content in self.news.values():
            trans = translator.translate(content['title'], src='pt', dest='en')
            content['translation'] = trans.text


    def get_sentiment_of_news(self):
        '''
        Receives the dict with translated title from translate_title, sends the title
        to OpenAI API and returns the same dictionary with a new 'sentiment' key.
        '''
        path = find_dotenv()
        load_dotenv(path)
        openai.api_key = os.environ.get('OPENAI_API_KEY')

        phrases = [f'{content["translation"]}' for content in self.news.values()]
        prompt = 'Classify in positive, neutral or negative the sentiment in these phrases:\n\n'

        for i, phrase in enumerate(phrases):
            prompt += f'{i+1}. "{phrase}"\n'
        prompt += '\nPhrases sentiment reatings:\n'

        res = openai.Completion.create(
            engine='text-davinci-002',
            prompt=prompt,
            temperature=0,
            max_tokens=60,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )

        classification = res['choices'][0]['text'].strip().split('\n')
        clean_classification = [re.sub('\d. ', '', sentiment) \
            for sentiment in classification]

        for i, sentiment in enumerate(clean_classification):
            self.news[i]['sentiment'] = sentiment


    def get_news(self, n=5):
        '''
        Gets the top n news from Google News' RSS and returns a dictionary with
        the titles, text, translation of the title and sentiment of the article.
        ---------
        Receives:
            - n: The number of news to analyze
        ---------
        Returns: dictionary
            - self.news: {- n: {
                url: The article's URL
                title: The original title of the article
                text: The original text of the article
                translation: The translation of the title of the article
                sentiment: The classification of the sentiment of the article,
                           in negative, neutral or positive.
            }}
        '''
        self.news = {}
        self.get_top_news(n)
        self.translate_titles()
        self.get_sentiment_of_news()

        return self.news

    def get_news_by_sentiment(self):
        '''
        Gets the dictionary with the news already analyzes and separates them
        into 3 lists, one for each possible sentiment.
        ----------
        Returns: tuple
            - positive_news: A list with the positive news.
            - neutral_news: A list with the neutral news.
            - negative_news: A list with the negative news.
        '''
        if not self.news:
            self.get_news()

        positive_news = [self.news[i] for i, article in self.news.items() \
                         if article['sentiment'].lower() == 'positive'.lower()]

        neutral_news = [self.news[i] for i, article in self.news.items() \
                    if article['sentiment'].lower() == 'neutral'.lower()]

        negative_news = [self.news[i] for i, article in self.news.items() \
            if article['sentiment'].lower() == 'negative'.lower()]

        return positive_news, neutral_news, negative_news


if __name__ == '__main__':
    news = News()
    positive, neutral, negative = news.get_news_by_sentiment()

    if len(positive) != 0:
        print(positive[0])
    if len(neutral) != 0:
        print(neutral[0])
    if len(negative) != 0:
        print(negative[0])
