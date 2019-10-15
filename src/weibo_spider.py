# 想要抓取到微博的数据，首先需要登录微博
#-*- encoding:utf-8 -*-

import base64
import requests
import re
import rsa
import binascii

def Get_cookies():
    '''登陆新浪微博，获取登陆后的Cookie，返回到变量cookies中'''
    #username = input(u'请输入用户名：')
    #password = input(u'请输入密码：')
    username = 'linb19@mails.tsinghua.edu.cn'
    password = 'linbin13579'


    url = 'http://login.sina.com.cn/sso/prelogin.php?entry=sso&callback=sinaSSOController.preloginCallBack&su=%s&rsakt=mod&client=ssologin.js(v1.4.4)%' + username
    html = requests.get(url).content
    html = html.decode('utf-8')
    print(html)
    servertime = re.findall('"servertime":(.*?),',html,re.S)[0]
    nonce = re.findall('"nonce":"(.*?)"',html,re.S)[0]
    pubkey = re.findall('"pubkey":"(.*?)"',html,re.S)[0]
    rsakv = re.findall('"rsakv":"(.*?)"',html,re.S)[0]

    username = username.encode('utf-8')

    username = base64.b64encode(username) #加密用户名
    rsaPublickey = int(pubkey, 16)
    key = rsa.PublicKey(rsaPublickey, 65537) #创建公钥
    message = str(servertime) + '\t' + str(nonce) + '\n' + str(password) #拼接明文js加密文件中得到
    message = message.encode('utf-8')
    passwd = rsa.encrypt(message, key) #加密
    passwd = binascii.b2a_hex(passwd) #将加密信息转换为16进制。

    login_url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.4)'
    data = {'entry': 'weibo',
        'gateway': '1',
        'from': '',
        'savestate': '7',
        'userticket': '1',
        'ssosimplelogin': '1',
        'vsnf': '1',
        'vsnval': '',
        'su': username,
        'service': 'miniblog',
        'servertime': servertime,
        'nonce': nonce,
        'pwencode': 'rsa2',
        'sp': passwd,
        'encoding': 'UTF-8',
        'prelt': '115',
        'rsakv' : rsakv,
        'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
        'returntype': 'META'
        }
    html = requests.post(login_url,data=data).content
    html = html.decode('utf-8')
    urlnew = re.findall('location.replace\(\'(.*?)\'',html,re.S)[0]

    #发送get请求并保存cookies
    cookies = requests.get(urlnew).cookies
    return cookies

cookies = Get_cookies()
print(cookies)