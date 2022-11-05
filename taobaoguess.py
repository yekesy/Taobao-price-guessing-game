import base64
import csv
import difflib
import glob
import os
import re
import threading
import time
from urllib import parse

import numpy as np
import requests
from fake_useragent import UserAgent

cluefilename = 'clue.csv'


mylist = ['三福时尚长巾', '蓝月亮洗衣液', '准者针织运动长裤', '核桃黑豆粉600g*2', '可心柔洗脸巾8包', '荷雨翼科技外套',\
        '特步运动跑步鞋', '准者2022羽绒马甲' , 'NB官方休闲鞋', '珀莱雅面膜40片', '老庙18K镶钻手饰', '芙清皮肤修复敷料', \
        '当妮护衣留香珠*3', '安踏儿童帮板鞋',
       '荞麦方便面1箱']

def get_response(url):
    ua = UserAgent()

    headers = {
        'authority': 's.taobao.com',
        'cache-control': 'max-age=0',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cookie': 'cna=jKMMGOupxlMCAWpbGwO3zyh4; tracknick=tb311115932; _cc_=URm48syIZQ%3D%3D; thw=cn; hng=CN%7Czh-CN%7CCNY%7C156; miid=935759921262504718; t=bd88fe30e6685a4312aa896a54838a7e; sgcookie=E100kQv1bRHxrwnulL8HT5z2wacaf40qkSLYMR8tOCmVIjE%2FxrR5nzhju3UySug2dFrigMAy3v%2FjkNElYj%2BDcqmgdA%3D%3D; uc3=nk2=F5RGNwnC%2FkUVLHU%3D&vt3=F8dCuf2OXoGHiuEl2D8%3D&id2=VyyUy7sStBYaoA%3D%3D&lg2=U%2BGCWk%2F75gdr5Q%3D%3D; lgc=tb311115932; uc4=nk4=0%40FY4NAq0PgYBeuIHFyHE%2F9QSZnG6juw%3D%3D&id4=0%40VXtbYhfspVba1o0MN1OuNaxcY%2BUP; enc=tJQ9f26IYMQmwsNzfEZi6fJNcflLvL6bdcU4yyus3rqfsM37Mpy1jvcSMZ%2BYSaE5vziMtC9svi%2B4JVMfCnIsWA%3D%3D; _samesite_flag_=true; cookie2=112f2a76112f88f183403c6a3c4b721f; _tb_token_=eeeb18eb59e1; tk_trace=oTRxOWSBNwn9dPyorMJE%2FoPdY8zfvmw%2Fq5v3iwJfzrr80CDMiLUbZX4jcwHeizGatsFqHolN1SmeHD692%2BvAq7YJ%2FbITqs68WMjdAhcxP7WLdArSe8thnE40E0eWE4GQTvQP9j5XSLFbjZAE7XgwagUcgW%2Fg6rXAuZaws1NrrZksnq%2BsYQUb%2FHT%2Fa1m%2Fctub0jBbjlmp8ZDJGSpGyPMgg561G3vjIRPVnkhRCyG9GgwteJUZAsyQIkeh7xtdyN%2BF50TIambWylXMZhQW7LQGZ48rHl3Q; lLtC1_=1; v=0; mt=ci=-1_0; _m_h5_tk=b0940eb947e1d7b861c7715aa847bfc7_1608386181566; _m_h5_tk_enc=6a732872976b4415231b3a5270e90d9c; xlly_s=1; alitrackid=www.taobao.com; lastalitrackid=www.taobao.com; JSESSIONID=136875559FEC7BCA3591450E7EE11104; uc1=cookie14=Uoe0ZebpXxPftA%3D%3D; tfstk=cgSFBiAIAkEUdZx7kHtrPz1rd-xdZBAkGcJ2-atXaR-zGpLhi7lJIRGJQLRYjef..; l=eBI8YSBIOXAWZRYCBOfaourza779sIRYSuPzaNbMiOCP9_fp5rvCWZJUVfT9CnGVh6SBR3-wPvUJBeYBqnY4n5U62j-la_Dmn; isg=BAsLX3b80AwyYAwAj8PO7RC0mq_1oB8iDqsYtX0I5sqhnCv-BXFHcGI-cpxyuXca',
    }
    response = requests.get(url, headers=headers).content.decode('utf-8')
    # "raw_title":"卡蒙手套女2020秋冬季新款运动保暖护手休闲针织触屏防寒羊皮手套"
    # "view_price":"208.00"
    # "nick":"intersport旗舰店"
    # "item_loc":"江苏 连云港"
    # "view_sales":"0人付款"
    title = re.findall(r'\"raw_title\"\:\"(.*?)\"', response)

    nick = re.findall(r'\"nick\"\:\"(.*?)\"', response)[:-1]

    item_loc = re.findall(r'\"item_loc\"\:\"(.*?)\"', response)

    price = re.findall(r'\"view_price\"\:\"(.*?)\"', response)

    sales = re.findall(r'\"view_sales\"\:\"(.*?)\"', response)
    return [title, nick, item_loc, price, sales]


def maxdiff(list, str):
    max = difflib.SequenceMatcher(None, list[0][0], str).quick_ratio()
    result = list[0][0]
    for i in range(len(list[0])):
        if difflib.SequenceMatcher(None, list[0][i], str).quick_ratio() > max:
            max = difflib.SequenceMatcher(None, list[0][i], str).quick_ratio()
            result = list[0][i]
    return result
    # max=Levenshtein.ratio(list[0][0], str)
    # result =list[0][0]
    # for i in range(len(list[0])):
    #     if Levenshtein.ratio(list[0][0],str)>max:
    #         max=Levenshtein.ratio(list[0][0],str)
    #         result=list[0][i]
    # return result


def tocsv(file, goodsname, filename):
    qijianfile = [[], [], []]
    cluefile = [[], [], []]
    flog = True
    with open(cluefilename, 'a+', encoding='utf-8') as f:
        f.seek(0)
        clue = np.array([line.strip('\n') for line in f])
        f.close()
    with open(filename, 'a+', encoding='utf-8', newline='') as f:
        f.seek(0)
        write = csv.writer(f)
        if f.read() == '':
            write.writerow(('标题', '店铺', '价格'))
        # 这里我并不知道参与品牌和旗舰店哪个在前面，参与品牌优先，确保没有了，在考虑旗舰店
        for i in range(len(file[0])):
            for j in clue:
                if j in file[1][i]:
                    # print(file[3][i])
                    cluefile[0].append(file[0][i])
                    cluefile[1].append(file[1][i])
                    cluefile[2].append(file[3][i])
        for i in range(len(file[0])):
            if '旗舰店' in file[1][i]:
                # print(file[3][i])
                qijianfile[0].append(file[0][i])
                qijianfile[1].append(file[1][i])
                qijianfile[2].append(file[3][i])
        qijianfile = np.array(qijianfile)
        cluefile = np.array(qijianfile)
        for i in range(len(cluefile[0])):
            if flog:
                if cluefile[0][i] == maxdiff(cluefile, goodsname):
                    write.writerow((cluefile[0][i], cluefile[1][i], cluefile[2][i]))
                    flog = False
                    break
        if flog:
            for i in range(len(qijianfile[0])):
                if qijianfile[0][i] == maxdiff(qijianfile, goodsname):
                    write.writerow((qijianfile[0][i], qijianfile[1][i], qijianfile[2][i]))
                    break
    f.close()


def crawler(list):
    for i in list:
        key = parse.quote(i)
        url = 'https://s.taobao.com/search?q={}&s={}'
        url_page = url.format(key, 0 * 44)
        res = get_response(url_page)
        print(url_page)
        time.sleep(1)
        tocsv(res, i, filename=filename)


def dealdata():
    with open(filename, 'a+', encoding='utf-8', newline='') as f:
        f.seek(0)
        data = []
        data.append(f.readline())
        print(data)


class myThread(threading.Thread):  # 继承父类threading.Thread

    def __init__(self, goodslist):
        threading.Thread.__init__(self)
        self.goodslist = goodslist

    def run(self):  # 把要执行的代码写到run函数里面 线程在创建后会直接运行run函数
        print("Starting " + self.name)
        # print_time(self.name, self.counter, 5)
        crawler(self.goodslist)
        print("Exiting " + self.name)


if __name__ == '__main__':
    filename = 'taobao.csv'
    if os.path.exists('./taobao.csv'):
        os.remove('taobao.csv')
    path = glob.glob('./*jpg')
    thread1 = myThread(mylist[0:3])
    thread2 = myThread(mylist[3:6])
    thread3 = myThread(mylist[6:9])
    thread4 = myThread(mylist[9:12])
    thread5 = myThread(mylist[12:15])
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    thread5.start()
