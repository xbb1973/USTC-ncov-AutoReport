import requests
import json
import smtplib
import time
import getpass
import re
import argparse
from email.mime.text import MIMEText
from email.header import Header
from bs4 import BeautifulSoup


class GradeReminder(object):
    def __init__(self, stuid, password, data_path):
        self.stuid = stuid
        self.password = password
        self.data_path = data_path

    def main_loop(self):
        while True:
            self.report()
            time.sleep(43200)

    def report(self):
        session = self.login()
        cookies = session.cookies
        try:
            data = session.get(
                "http://weixine.ustc.edu.cn/2020").text
            soup = BeautifulSoup(data, 'lxml')
            token = soup.find("input", {"name": "_token"})['value']
            
            print("begin report...")
            
            with open(self.data_path, "r+") as f:
                data = f.read()
                data = json.loads(data)
                data["_token"]=token

            headers = {
                'authority': 'weixine.ustc.edu.cn',
                'origin': 'http://weixine.ustc.edu.cn',
                'upgrade-insecure-requests': '1',
                'content-type': 'application/x-www-form-urlencoded',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'referer': 'http://weixine.ustc.edu.cn/2020/',
                'accept-language': 'zh-CN,zh;q=0.9',
                'Connection': 'close',
                'cookie': 'PHPSESSID=' + cookies.get("PHPSESSID") + ";XSRF-TOKEN=" + cookies.get("XSRF-TOKEN") + ";laravel_session="+cookies.get("laravel_session"),
            }

            url = "http://weixine.ustc.edu.cn/2020/daliy_report"
            session.post(url, data=data, headers=headers)
            data = session.get("http://weixine.ustc.edu.cn/2020").text
            soup = BeautifulSoup(data, 'lxml')
            pattern = re.compile("2020-0[0-9]-[0-9]{2}")
            token = soup.find(
                "span", {"style": "position: relative; top: 5px; color: #666;"})
            flag = False
            if pattern.search(token.text) is not None:
                date = pattern.search(token.text).group()
                flag = (time.strftime("%Y-%m-%d", time.localtime()) == date)
            if flag == False:
                print("Failed report.")
            else:
                print("Successful report.")
            #######################
            # self.send_mail(flag)
            #######################
            print("end report...")

        except ValueError:
            print("Error...")
            #######################
            # self.send_mail(False)
            #######################

    def send_mail(self, flag):
        #### Here is an example.
        sender = 'xxxxxxxxxx@qq.com'
        receiver = 'xxx@mail.ustc.edu.cn'

        mail_host = "smtp.qq.com"
        mail_user = "xxxxxxxxxx@qq.com"
        mail_pwd = ''           # Fill in smtp password of your smtp service.

        mail_content = 'Auto report content.'
        if flag == True:
            mail_title = 'Successful report'
        else:
            mail_title = 'Failed report'

        smtp = smtplib.SMTP_SSL(mail_host)
        # smtp.set_debuglevel(1)
        # smtp.starttls()
        smtp.ehlo(mail_host)
        smtp.login(mail_user, mail_pwd)

        msg = MIMEText(mail_content, "plain", "utf-8")
        msg['Subject'] = Header(mail_title, 'utf-8')
        msg['From'] = sender
        msg['To'] = receiver

        smtp.sendmail(sender, receiver, msg.as_string())
        smtp.quit()

    def login(self):
        url = "https://passport.ustc.edu.cn/login?service=http%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin"
        data = {
            'model': 'uplogin.jsp',
            'service': 'http://weixine.ustc.edu.cn/2020/caslogin',
            'stuid': self.stuid,
            'password': str(self.password),
        }
        session = requests.Session()
        print(session.post(url, data=data))

        print("login...")
        return session


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='USTC nCov auto report script.')
    parser.add_argument('data_path', help='path to your own data used for post method', type=str)
    args = parser.parse_args()
    stuid = getpass.getpass('Please input your stuid: ')
    password = getpass.getpass('Please input your password: ')
    my_grade_remainder = GradeReminder(stuid=stuid, password=password, data_path=args.data_path)
    my_grade_remainder.main_loop()
