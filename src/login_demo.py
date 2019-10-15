import requests
import urllib
import base64

class login(object):
    session = requests.session()
    user_name = "linb19@mails.tsinghua.edu.cn"
    pass_word = "linbin13579"

    def get_username(self):
        return base64.b64encode(urllib.parse.quote(self.user_name).encode("utf-8")).decode("utf-8")


login = login()
login.get_username()