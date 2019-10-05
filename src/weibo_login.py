import requests
import rsa
import time
import re
import random
import urllib3
import base64
from urllib.parse import quote
from binascii import b2a_hex
from bs4 import BeautifulSoup
import time
urllib3.disable_warnings() # 取消警告

def get_timestamp():
    return int(time.time()*1000)  # 获取13位时间戳

class WeiBo():
    def __init__(self,username,password):
        self.username = username
        self.password = password
        self.session = requests.session() #登录用session
        self.session.headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
        }
        self.session.verify = False  # 取消证书验证

    def prelogin(self):
        '''预登录，获取一些必须的参数'''
        self.su = base64.b64encode(self.username.encode())  #阅读js得知用户名进行base64转码
        url = 'https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su={}&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)&_={}'.format(quote(self.su),get_timestamp()) #注意su要进行quote转码
        response = self.session.get(url).content.decode()
        # print(response)
        self.nonce = re.findall(r'"nonce":"(.*?)"',response)[0]
        self.pubkey = re.findall(r'"pubkey":"(.*?)"',response)[0]
        self.rsakv = re.findall(r'"rsakv":"(.*?)"',response)[0]
        self.servertime = re.findall(r'"servertime":(.*?),',response)[0]
        return self.nonce,self.pubkey,self.rsakv,self.servertime

    def get_sp(self):
        '''用rsa对明文密码进行加密，加密规则通过阅读js代码得知'''
        publickey = rsa.PublicKey(int(self.pubkey,16),int('10001',16))
        message = str(self.servertime) + '\t' + str(self.nonce) + '\n' + str(self.password)
        self.sp = rsa.encrypt(message.encode(),publickey)
        return b2a_hex(self.sp)

    def login(self):
        url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
        data = {
        'entry': 'weibo',
        'gateway': '1',
        'from':'',
        'savestate': '7',
        'qrcode_flag': 'false',
        'useticket': '1',
        'pagerefer': 'https://login.sina.com.cn/crossdomain2.php?action=logout&r=https%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl%3D%252F',
        'vsnf': '1',
        'su': self.su,
        'service': 'miniblog',
        'servertime': str(int(self.servertime)+random.randint(1,20)),
        'nonce': self.nonce,
        'pwencode': 'rsa2',
        'rsakv': self.rsakv,
        'sp': self.get_sp(),
        'sr': '1536 * 864',
        'encoding': 'UTF - 8',
        'prelt': '35',
        'url': 'https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
        'returntype': 'META',
        }
        response = self.session.post(url,data=data,allow_redirects=False).text # 提交账号密码等参数
        redirect_url = re.findall(r'location.replace\("(.*?)"\);',response)[0] # 微博在提交数据后会跳转，此处获取跳转的url
        result = self.session.get(redirect_url,allow_redirects=False).text  # 请求跳转页面
        ticket,ssosavestate = re.findall(r'ticket=(.*?)&ssosavestate=(.*?)"',result)[0] #获取ticket和ssosavestate参数
        uid_url = 'https://passport.weibo.com/wbsso/login?ticket={}&ssosavestate={}&callback=sinaSSOController.doCrossDomainCallBack&scriptId=ssoscript0&client=ssologin.js(v1.4.19)&_={}'.format(ticket,ssosavestate,get_timestamp())
        data = self.session.get(uid_url).text #请求获取uid
        uid = re.findall(r'"uniqueid":"(.*?)"',data)[0]
        print(uid)
        home_url = 'https://weibo.com/u/{}/home?wvr=5&lf=reg'.format(uid) #请求首页
        html = self.session.get(home_url)
        html.encoding = 'utf-8'
        #print(html.text)

    def get_pagenums(self, url):
        time.sleep(2)


    def get_preweibourl(self, url):
        time.sleep(2)
        response = self.session.post(url).text
        soup = BeautifulSoup(response, "html.parser")
        contents = soup.find_all("div", "content")
        infos = soup.find_all('div', 'card-act')
        for content, info in zip(contents, infos):
            weibo_content = content.find('p', 'txt').text.strip()
            weibo_name = content.find('a', 'name').text
            weibo_time = content.find('p', 'from').text.split()[0] + ' ' + content.find('p', 'from').text.split()[1]
            zan_num = info.find_all('li')
            print(zan_num[3].text)
            print(weibo_time)
            print(weibo_name)
            print(weibo_content)



    def main(self):
        self.prelogin()
        self.get_sp()
        self.login()
        #url = 'https://weibo.com/schuvann?from=myfollow_all&is_all=1'    # 酒肆亦
        #url = 'https://s.weibo.com/weibo/%25E5%258D%2581%25E4%25B8%2580%25E5%2581%2587%25E6%259C%259F%25E7%259A%2584%25E4%25BD%25A0%25E6%259C%25AC%25E4%25BA%25BA?q=%E8%87%AA%E5%8A%A8%E9%A9%BE%E9%A9%B6&timescope=custom:2019-10-01-5:2019-10-02-5&Refer=g'
        url = 'https://m.weibo.cn/'
        self.get_preweibourl(url)

if __name__ == '__main__':
    username = 'linb19@mails.tsinghua.edu.cn' # 微博账号
    password = 'linbin13579' # 微博密码
    weibo = WeiBo(username,password)
    weibo.main()