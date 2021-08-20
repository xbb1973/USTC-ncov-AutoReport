# encoding=utf8
import requests
import json
import datetime
import pytz
import re
import argparse
from bs4 import BeautifulSoup
from PIL import Image
from ocr import ocr

class Report(object):
    def __init__(self, stuid, password, data_path):
        self.stuid = stuid
        self.password = password
        self.data_path = data_path

    def report(self):
        loginsuccess = False
        retrycount = 5
        while (not loginsuccess) and retrycount:
            session = self.login()
            getform = session.get("http://weixine.ustc.edu.cn/2020")
            retrycount = retrycount - 1
            if getform.url != "https://weixine.ustc.edu.cn/2020/home":
                print("Login Failed! Retry...")
            else:
                print("Login Successful!")
                loginsuccess = True
        if not loginsuccess:
            return False
        data = getform.text
        data = data.encode('ascii','ignore').decode('utf-8','ignore')
        soup = BeautifulSoup(data, 'html.parser')
        token = soup.find("input", {"name": "_token"})['value']

        with open(self.data_path, "r+") as f:
            data = f.read()
            data = json.loads(data)
            data["_token"]=token

        headers = {
            "content-type": "application/x-www-form-urlencoded",
        }

        url = "http://weixine.ustc.edu.cn/2020/daliy_report"
        session.post(url, data=data, headers=headers)
        data = session.get("http://weixine.ustc.edu.cn/2020").text
        soup = BeautifulSoup(data, 'html.parser')
        pattern = re.compile("2021-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}")
        token = soup.find(
            "span", {"style": "position: relative; top: 5px; color: #666;"})
        flag = False
        if pattern.search(token.text) is not None:
            date = pattern.search(token.text).group()
            print("Latest report: " + date)
            date = date + " +0800"
            reporttime = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S %z")
            timenow = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
            delta = timenow - reporttime
            print("{} second(s) before.".format(delta.seconds))
            if delta.seconds < 120:
                flag = True
        if flag == False:
            print("Report FAILED!")
        else:
            print("Report SUCCESSFUL!")
        return flag

    def login(self):
        url = "https://passport.ustc.edu.cn/login?service=http%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin"
        session = requests.Session()
        r = session.get(url)
        (cas_lt,) = re.findall(r"name=\"CAS_LT\" value=\"(.+)\"", r.text)
        raw = session.get(
            "https://passport.ustc.edu.cn/validatecode.jsp?type=login", stream=True
        ).raw
        img = Image.open(raw)
        lt = ocr(img)
        data = {
            "model": "uplogin.jsp",
            "CAS_LT": cas_lt,
            "service": "https://weixine.ustc.edu.cn/2020/caslogin",
            "username": self.stuid,
            "password": str(self.password),
            "warn": "",
            "showCode": 1,
            "button": "",
            "LT": lt,
        }
        session.post(url, data=data)

        print("login...")
        return session


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='URC nCov auto report script.')
    parser.add_argument('data_path', help='path to your own data used for post method', type=str)
    parser.add_argument('stuid', help='your student number', type=str)
    parser.add_argument('password', help='your CAS password', type=str)
    args = parser.parse_args()
    autorepoter = Report(stuid=args.stuid, password=args.password, data_path=args.data_path)
    count = 5
    while count != 0:
        ret = autorepoter.report()
        if ret != False:
            break
        print("Report Failed, retry...")
        count = count - 1
    if count != 0:
        exit(0)
    else:
        exit(-1)