import requests
import re
from bs4 import BeautifulSoup
import time
import pandas as pd
from fake_useragent import UserAgent
import time
import random
from xml.dom import minidom
import pickle
from xml.etree import ElementTree as ET



ret_weibos = []

###############################
#        list to xml          #
###############################


def addxmlchildcomment(root, childcomments):
    count = 1
    for childcomment in childcomments:
        perroot = ET.SubElement(root, 'childcomment{}'.format(count))
        count = count+1
        perroot.text = str(childcomment)
    return


def addxmlcomment(root, comments):
    count = 1
    for comment in comments:
        perroot = ET.SubElement(root, 'comment{}'.format(count))
        count = count + 1
        attr = {'comment_name':str(comment['comment_name']), 'comment_time':str(comment['comment_time']), 'like_count':str(comment['like_count'])}
        perroot.attrib = attr
        perroot.text = str(comment['comment_text'])
        if 'childcomments' in comment:
            addxmlchildcomment(perroot, comment['childcomments'])
    return



def writexml(ret_weibos):
    root = ET.Element('weibo_root')
    count = 1                                   # 用于微博数量计数
    for ret_weibo in ret_weibos:
        perroot = ET.SubElement(root, 'weibo{}'.format(count))
        attr = {'weibo_name':str(ret_weibo['weibo_name']), 'weibo_likecount':str(ret_weibo['weibo_likecount']), 'weibo_time':str(ret_weibo['weibo_time'])}
        perroot.attrib = attr
        perroot.text = str(ret_weibo['text'])
        if(ret_weibo['comment']):
            addxmlcomment(perroot, ret_weibo['comment'])
        count = count + 1
    w = ET.ElementTree(root)
    w.write('weibo.xml', 'utf-8', True)
    return

###############################
#        list to xml          #
###############################


class m_weibo():
    def __init__(self):
        self.ua = UserAgent()
        self.header = {
            #'cookie' : '_T_WM=30908099413; WEIBOCN_FROM=1110006030; SUHB=0rrrcFjWleRU50; SCF=AnFNRhQLFj5kEnyAmhHXGk5ygdvfTKigVqWWiUMnivISWQUYuWFaBkxaPKCO9qmbstw8RyWvCsIUn9x-1esFtjU.; SUB=_2A25wkoUlDeRhGeFN6lEU9y3JyTmIHXVQfCttrDV6PUJbkdBeLUqkkW1NQH8PbxOWYMPtW5QBcbKiuii7r6U_qjVW; SSOLoginState=1570174325; MLOGIN=1; XSRF-TOKEN=90da58',
            'user_agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
        }
        self.session = requests.session()
        self.session.headers = self.header
        self.session.verify = False

    def get_childcomment(self, mid):
        childcomments = []
        childcomment_url = 'https://m.weibo.cn/comments/hotFlowChild?cid={}&max_id=0&max_id_type=0'.format(mid)
        # 使用伪随机的user_agent
        #self.header['user_agent'] = self.ua.random
        #self.session.headers = self.header
        try:
            contents = self.session.post(childcomment_url).json()
        except:
            print(mid)
            return childcomments
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
                    try:
                        contents = self.session.post(comment_url).json()
                    except:
                        return childcomments
        return childcomments

    def get_comment(self, url, cardid):
        ret_comments = []
        if url:
            #try:
            # 使用伪随机的user_agent
            #self.header['user_agent'] = self.ua.random
            #self.session.headers = self.header
            # 加入随机时延间隔
            time.sleep(random.random()*3)
            html = self.session.post(url).text
            soup = BeautifulSoup(html, 'html.parser')
            # cardid = '4424019103314944'
            comment_url = 'https://m.weibo.cn/comments/hotflow?id={}&mid={}&max_id_type=0'.format(cardid, cardid)
            try:
                contents = self.session.post(comment_url).json()
                max_num = contents['data']['total_number']
            except:
                return ret_comments
            count = 0
            if max_num:
                while(count<max_num):
                    if count>100:
                        return ret_comments
                    try:
                        comments = contents['data']['data']
                    except:
                        time.sleep(2)
                        print('该条微博能爬取的评论数目达到上限，停止爬取')
                        return ret_comments
                    for comment in comments:
                        ret_comment = {}
                        ret_comment['comment_name'] = comment['user']['screen_name']
                        ret_comment['comment_time'] = comment['created_at']
                        ret_comment['like_count'] = comment['like_count']
                        ret_comment['comment_text'] = BeautifulSoup(comment['text'], "html.parser").text
                        comment_text = BeautifulSoup(comment['text'], "html.parser").text  # html内容转换
                        #comment_name = comment['user']['screen_name']
                        #comment_time = comment['created_at']
                        #like_count = comment['like_count']
                        #comment_text = BeautifulSoup(comment['text'], "html.parser").text  # html内容转换
                        print(ret_comment['comment_name'], ret_comment['comment_time'], ret_comment['like_count'], ret_comment['comment_text'])
                        if comment['total_number']:
                            ret_comment['childcomments'] = self.get_childcomment(comment['mid'])
                            #childcomments = self.get_childcomment(comment['mid'])
                            print(ret_comment['childcomments'])
                        ret_comments.append(ret_comment)
                    count = count+20
                    if contents['data']['max_id'] == 0:
                        break
                    if(count<max_num):
                        max_id = contents['data']['max_id']
                        comment_url = 'https://m.weibo.cn/comments/hotflow?id=4423614780285721&mid={}&max_id={}&max_id_type=0'.format(cardid, max_id)
                        # 使用伪随机的user_agent
                        #self.header['user_agent'] = self.ua.random
                        #self.session.headers = self.header
                        try:
                            contents = self.session.post(comment_url).json()
                        except:
                            return ret_comments


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
        # ret_weibos = []
        url = 'https://m.weibo.cn' # 移动版微博地址
        content_url = 'https://m.weibo.cn/api/container/getIndex?containerid=102803&openApp=0'
        # 使用伪随机的user_agent
        #self.header['user_agent'] = self.ua.random
        #self.session.headers = self.header
        surfnum = 15
        for i in range(surfnum):
            try:
                weibo_content = self.session.post(content_url).json()
            except:
                break
            print(weibo_content['ok'])
            for pre_weibo in weibo_content['data']['cards']:
                ret_weibo = {}
                print("开始爬取新的微博")
                # 加入随机时延间隔
                time.sleep(random.random() * 3)
                ret_weibo['weibo_name'] = pre_weibo['mblog']['user']['screen_name']
                ret_weibo['weibo_likecount'] = pre_weibo['mblog']['attitudes_count']
                ret_weibo['weibo_time'] = pre_weibo['mblog']['created_at']
                ret_weibo['weibo_time'] = self.time_transform(ret_weibo['weibo_time'])
                ret_weibo['text'] = BeautifulSoup(pre_weibo['mblog']['text'], "html.parser").text
                #weibo_name = pre_weibo['mblog']['user']['screen_name']
                #weibo_likecount = pre_weibo['mblog']['attitudes_count']
                #weibo_time = pre_weibo['mblog']['created_at']
                #weibo_time = self.time_transform(weibo_time)
                #weibo_text = BeautifulSoup(pre_weibo['mblog']['text'], "html.parser").text  # html内容转换

                # 获得单个微博的url
                cardid = pre_weibo['itemid']
                cardid = re.findall(r'mbloglist_(.*?)$', cardid)[0]   # 正则表达式末尾匹配需要加上末尾匹配符
                comment_url = 'https://m.weibo.cn/detail/{}'.format(cardid)         #获得每一条微博的具体地址
                print(comment_url)
                ret_weibo['comment'] = self.get_comment(comment_url, cardid)
                ret_weibos.append(ret_weibo)
        writexml(ret_weibos)
        f = open("deposit.txt","w", encoding='utf-8')
        f.write(str(ret_weibos))
        f.close()


"""
pickle读取list
import pickle
    fileHandle = open ( 'pickleFile.txt' ,'r') 
    testList = pickle.load ( fileHandle ) 
    fileHandle.close() 
"""

if __name__ == '__main__':
    m_weibo = m_weibo()
    m_weibo.main(1)
