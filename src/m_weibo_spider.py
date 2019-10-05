import requests
import re
from bs4 import BeautifulSoup
import time
import pandas as pd

class m_weibo():
    def __init__(self):
        self.header = {
            'cookie' : '_T_WM=30908099413; WEIBOCN_FROM=1110006030; SUHB=0rrrcFjWleRU50; SCF=AnFNRhQLFj5kEnyAmhHXGk5ygdvfTKigVqWWiUMnivISWQUYuWFaBkxaPKCO9qmbstw8RyWvCsIUn9x-1esFtjU.; SUB=_2A25wkoUlDeRhGeFN6lEU9y3JyTmIHXVQfCttrDV6PUJbkdBeLUqkkW1NQH8PbxOWYMPtW5QBcbKiuii7r6U_qjVW; SSOLoginState=1570174325; MLOGIN=1; XSRF-TOKEN=90da58',
            'user_agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
        }
        self.session = requests.session()
        self.session.headers = self.header
        self.session.verify = False

    def get_childcomment(self, mid):
        childcomments = []
        childcomment_url = 'https://m.weibo.cn/comments/hotFlowChild?cid={}&max_id=0&max_id_type=0'.format(mid)
        try:
            contents = self.session.post(childcomment_url).json()
        except:
            print(mid)
        max_num = contents['total_number']
        count = 0
        if max_num:
            while (count < max_num):
                comments = contents['data']
                for comment in comments:
                    comment_text = BeautifulSoup(comment['text'], "html.parser").text  # html内容转换
                    childcomments.append(comment_text)
                count = count + 10
                if contents['max_id'] == 0:
                    break
                if (count < max_num):
                    max_id = contents['max_id']
                    comment_url = 'https://m.weibo.cn/comments/hotFlowChild?cid={}&max_id={}&max_id_type=0'.format(mid, max_id)
                    contents = self.session.post(comment_url).json()
        return childcomments

    def get_comment(self, url, cardid):
        if url:
            #try:
            html = self.session.post(url).text
            soup = BeautifulSoup(html, 'html.parser')
            # cardid = '4424019103314944'
            comment_url = 'https://m.weibo.cn/comments/hotflow?id={}&mid={}&max_id_type=0'.format(cardid, cardid)
            contents = self.session.post(comment_url).json()
            max_num = contents['data']['total_number']
            count = 0
            if max_num:
                while(count<max_num):
                    try:
                        comments = contents['data']['data']
                    except:
                        time.sleep(2)
                        print('该条微博能爬取的评论数目达到上限，停止爬取')
                        return
                    for comment in comments:
                        comment_name = comment['user']['screen_name']
                        comment_time = comment['created_at']
                        like_count = comment['like_count']
                        comment_text = BeautifulSoup(comment['text'], "html.parser").text  # html内容转换
                        print(comment_name, comment_time, like_count, comment_text)
                        if comment['total_number']:
                            childcomments = self.get_childcomment(comment['mid'])
                            print(childcomments)
                    count = count+20
                    if contents['data']['max_id'] == 0:
                        break
                    if(count<max_num):
                        max_id = contents['data']['max_id']
                        comment_url = 'https://m.weibo.cn/comments/hotflow?id=4423614780285721&mid={}&max_id={}&max_id_type=0'.format(cardid, max_id)
                        contents = self.session.post(comment_url).json()


    def time_transform(self, weibo_time):
        now_time = time.time()
        if '小时' in weibo_time:
            weibo_time = int(re.findall(r'(.*?)小时', weibo_time)[0])
            weibo_time = now_time - weibo_time * 3600
        elif '分钟' in weibo_time:
            weibo_time = int(re.findall(r'(.*?)分钟', weibo_time)[0])
            weibo_time = now_time - weibo_time * 60
        elif '昨天' in weibo_time:
            weibo_time = now_time - 3600 * 12

        if isinstance(weibo_time, float):
            weibo_time = timeArray = time.localtime(weibo_time)
            weibo_time = time.strftime("%Y--%m--%d %H:%M:%S", weibo_time)
        else:
            pass
        return weibo_time

    def main(self, page):
        url = 'https://m.weibo.cn' # 移动版微博地址
        content_url = 'https://m.weibo.cn/api/container/getIndex?containerid=102803&openApp=0'
        weibo_content = self.session.post(content_url).json()
        print(weibo_content)
        for pre_weibo in weibo_content['data']['cards']:
            print("开始爬取新的微博")
            time.sleep(2)
            weibo_name = pre_weibo['mblog']['user']['screen_name']
            weibo_likecount = pre_weibo['mblog']['attitudes_count']
            weibo_time = pre_weibo['mblog']['created_at']
            weibo_time = self.time_transform(weibo_time)
            weibo_text = BeautifulSoup(pre_weibo['mblog']['text'], "html.parser").text  # html内容转换

            # 获得单个微博的url
            cardid = pre_weibo['itemid']
            cardid = re.findall(r'mbloglist_(.*?)$', cardid)[0]   # 正则表达式末尾匹配需要加上末尾匹配符
            comment_url = 'https://m.weibo.cn/detail/{}'.format(cardid)         #获得每一条微博的具体地址
            print(comment_url)
            self.get_comment(comment_url, cardid)
            #break

if __name__ == '__main__':
    m_weibo = m_weibo()
    m_weibo.main(1)
