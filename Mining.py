import requests
import re
from bs4 import BeautifulSoup
from krwordrank.word import KRWordRank
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from krwordrank.hangle import normalize
from PIL import Image
import numpy as np


class crawling:

    def __init__(self, login_url='https://ssu.everytime.kr/user/login', api_url='https://api.everytime.kr'):
        LOGIN_INFO = {
            'userid': '',
            'password': '',
            'redirect': '/'
        }
        self.login_url = login_url
        self.api_url = api_url
        self.LOGIN_INFO = LOGIN_INFO

        with requests.Session() as self.s:
            login_res = self.s.post(login_url, data=LOGIN_INFO)

            if login_res.status_code != 200:  # log-in-check
                raise Exception('Log-in Failed')
            #  ~~~~~~~~~~~~~~~ Session 유지!

    def net(self):
        texts = []
        font_path = 'C:\\Windows\\Fonts\\경기천년제목_Light.ttf'

        everytime_board_list = self.s.post(self.api_url + '/find/board/article/list', data={
            'id': 384917,
            'limit_num': 20,
            'start_num': 0,
            'moiminfo': True,
        })
        sop = BeautifulSoup(everytime_board_list.content, 'html.parser')

        data = sop.find_all('article')

        for i in data:
            texts.append(str(re.findall(r'(?<=text=\")\w.*(?=\" t)', str(i))))

        texts = [normalize(text, english=True, number=True) for text in texts]
        wordrank_extractor = KRWordRank(
            min_count=0,  # 단어의 최소 출현 빈도수 (그래프 생성 시)
            max_length=10,  # 단어의 최대 길이
            verbose=True
        )

        beta = 0.85  # PageRank의 decaying factor beta
        max_iter = 10

        keywords, rank, graph = wordrank_extractor.extract(texts, beta, max_iter)


        for word, r in sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:30]:
            print('%8s:\t%.4f' % (word, r))
        print(keywords)
        print(len(texts))
        # Generate a word cloud image

        cat = np.array(Image.open("animal-674204_1920.jpg"))
        wordcloud = WordCloud(
            font_path=font_path,
            width=1920,
            height=1080,
            background_color="white",
            mask=cat).generate(str(texts))

        wordcloud = wordcloud.generate_from_frequencies(keywords)

        # Display the generated image:
        # the matplotlib way:

        fig = plt.figure(figsize=(19.20, 10.80))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.show()
        fig.savefig('./savefig_default.png')


a = crawling()
a.net()
