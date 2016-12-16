# -*- coding: utf-8 -*-

import requests
import datetime
import csv
import pickle
from bs4 import BeautifulSoup
from models import HouseModel
import config
import time
import sys
import os
from log import get_app_logger
reload(sys)
sys.setdefaultencoding('utf8')


g_logger = get_app_logger('lj-spider', 'spider.log')


class LianJiaHouseSpider(object):
    """docstring for HouseSpider"""
    LIANJIA_CHENGJIAO_BASEURL = 'http://cd.lianjia.com/chengjiao/'
    LIANJIA_CHENGJIAO_DBFILE = '{}/lianjia.csv'.format(config.PROJECT_DIR)
    LIANJIA_CHENGJIAO_GRAB_DBFILE = '{}/lianjia_grab'.format(config.PROJECT_DIR)

    def __init__(self):
        self.grab_urls = []
        if os.path.exists(self.LIANJIA_CHENGJIAO_GRAB_DBFILE):
            with open(self.LIANJIA_CHENGJIAO_GRAB_DBFILE, 'rb') as fd:
                self.grab_urls = pickle.load(fd)

    def run(self):
        for url in self.get_urls():
            g_logger.debug('STARTING TO GRAB {}'.format(url))
            try:
                htmlpage = self.download(url)
                soup = BeautifulSoup(htmlpage.content, "lxml", from_encoding="utf-8")
                tradedHoustList = soup.find("ul", class_="clinch-list").find_all('li')
            except Exception as e:
                g_logger.debug("Got error from main page [{}]".format(e))
                time.sleep(5)
                continue

            if not tradedHoustList:
                return
            house_models = []
            for item in tradedHoustList:
                # https://github.com/leven-ls/homeless
                # 房屋详情链接，唯一标识符
                try:
                    houseUrl = item.find("h2").a["href"] or ''
                    if houseUrl not in self.grab_urls:
                        self.grab_urls.append(houseUrl)
                    else:
                        continue
                    # 抓取 小区，户型，面积
                    title = item.find("h2").a
                    if title:
                        xiaoqu, houseType, square = (item.find("h2").a.string.split(" "))
                    else:
                        xiaoqu, houseType, square = ('Nav', 'Nav', 'Nav')

                    # 成交时间，朝向，楼层
                    houseInfo = item.find("div", class_="con").string

                    if houseInfo:
                        if len(houseInfo.split("/")) == 2:
                            orientation, floor = ([x.strip() for x in houseInfo.split("/")])
                            buildInfo = 'Nav'
                        if len(houseInfo.split("/")) == 3:
                            orientation, floor, buildInfo = ([x.strip() for x in houseInfo.split("/")])

                    div_cuns = item.find_all("div", class_="div-cun")

                    if div_cuns:
                        tradeDate = datetime.datetime.strptime(div_cuns[0].get_text(), '%Y.%m.%d') or datetime.datetime(1990, 1, 1)
                        perSquarePrice = div_cuns[1].strings.next() or 'Nav'
                        totalPrice = div_cuns[2].strings.next() or 'Nav'

                    m = HouseModel(xiaoqu=xiaoqu, type=houseType, square=square, orientation=orientation, floor=floor, build=buildInfo, tradedate=tradeDate, persquareprice=perSquarePrice, totalprice=totalPrice)
                    house_models.append(m)
                except Exception as e:
                    g_logger.debug("Got error from sub page [{}]".format(e))
                    time.sleep(5)
                    continue
            self.save(house_models)

    @staticmethod
    def download(url):
        htmlpage = None
        try:
            htmlpage = requests.get(url, timeout=30)
        except Exception as e:
            g_logger.debug(e)
        return htmlpage

    @staticmethod
    def format(htmlpage):
        house_model = None
        return house_model

    def get_urls(self):
        for index in range(1, 101):
            yield '{url}pg{page}'.format(url=self.LIANJIA_CHENGJIAO_BASEURL, page=index)

    def save(self, house_models):
        is_need_write_header = True
        if os.path.exists(self.LIANJIA_CHENGJIAO_DBFILE):
            is_need_write_header = False
        with open(self.LIANJIA_CHENGJIAO_DBFILE, 'a+') as csv_fd:
            csv_writer = csv.DictWriter(csv_fd, fieldnames=HouseModel.HOUSE_MODEL_DEF_COLUMNS)
            if is_need_write_header:
                csv_fd.write(','.join(HouseModel.HOUSE_MODEL_DEF_COLUMNS.values()))
                csv_fd.write('\n')
            for model in house_models:
                csv_writer.writerow(model.values)
        with open(self.LIANJIA_CHENGJIAO_GRAB_DBFILE, 'wb') as grab_fd:
            pickle.dump(self.grab_urls, grab_fd)
