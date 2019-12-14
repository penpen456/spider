"""
1.站点：https://www.5tps.vip/html/17854.html
2.下载内容：我当阴阳先生的那几年 有声小说
3.（1）第1个页面（集数页面）：https://www.5tps.vip/play/17854_55_1_4.html
   从这个页面获取第2个页面的url（在标签iframe里面）
  （2）第2个页面：https://www.5tps.vip/play/flw.asp?url=
   %BF%D6%B2%C0%D0%A1%CB%B5%2F%CE%D2%B5%B1%D2%F5%D1%F4%CF%C8%C9%FA%B5%C4%C4%C7%BC%B8%C4%EA%2F004%5FD%2Emp3
   &jiidx=17854%5F55%5F1%5F5%2Ehtml&jiids=17854%5F55%5F1%5F3%2Ehtml&id=17854&said=55
   从这个页面通过正则表达式获取mp3的下载url
  （3）第3个页面：http://177l.tt56w.com:8000/恐怖小说/我当阴阳先生的那几年/004_D'.mp3?611704400984x1575340827x611710531644-45929668993988116460
4.用线程+队列方式实现多线程下载（6线程
5.若超时，可以将集数丢回去重新等待下载
"""

import requests
from lxml import etree
import re
import threading
import queue
import time
import os


def req(url_queue):
    while True:
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36'
        }
        # proxy = {
        #     'https': 'https://localhost:8888'
        # }
        # 获取第一个页面
        sont = url_queue.get()
        url1 = 'https://www.5tps.vip/play/17854_55_1_{0}.html'.format(sont)
        try:
            res = requests.get(url1, headers=headers, verify=False)
        except requests.exceptions.ConnectionError:
            print('超时..重新下载')
            url_queue.put(sont)
            # 不需要判断是否为空，因为丢回去了肯定不为空
            continue
        else:
            html = etree.HTML(res.content.decode('gb2312'))
            x_path = html.xpath('//iframe/@src')[0]
            url2 = 'https://www.5tps.vip' + x_path
        # 获取第二个页面
        # res2 = requests.get(url2, headers=headers, verify=False, proxies=proxy)
        res2 = requests.get(url2, headers=headers, verify=False)
        try:
            s1 = 'http://177l.tt56w.com:8000/恐怖小说/我当阴阳先生的那几年/'
            s2 = re.search(r'\d{3}_[A-Z]+', res2.content.decode('gb2312')).group()
            s3 = re.search(r'\w{10,}-\w*', res2.content.decode('gb2312')).group()
            url3 = s1 + s2 + '.mp3?' + s3
            # 获取第三个页面（下载）
            res3 = requests.get(url3, headers=headers, verify=False)
        except AttributeError:
            print('第{}集页面下载网址异常,重新下载...'.format(sont))
            url_queue.put(sont)
        except requests.exceptions.ConnectionError:
            print('超时')
        else:
            # 保存mp3
            with open('./我当阴阳先生的那几年/第{}集.mp3'.format(sont), 'wb') as f:
                f.write(res3.content)
        finally:
            time.sleep(2)
            # 发送信号告知队列线程结束,和queue.join()配合,判断队列是否为空
            url_queue.task_done()


if __name__ == "__main__":
    # 忽略ssl警告
    requests.packages.urllib3.disable_warnings()
    # 创建目录
    os.mkdir('./我当阴阳先生的那几年')
    start = time.time()
    # 集数队列
    url_queue = queue.Queue()
    # 添加集数
    for i in range(1, 195):
        url_queue.put(i)
    # 创建6个线程，即线程池里面6个线程并发
    for i in range(6):
        t = threading.Thread(target=req, args=(url_queue,))
        t.setDaemon(True)
        t.start()
    # 等待队列为空
    url_queue.join()
    print('下载完成...用时', time.time()-start)
