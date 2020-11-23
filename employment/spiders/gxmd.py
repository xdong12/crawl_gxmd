#!/usr/bin/env python3
# coding: utf-8
# Time: 2020/11/23 10:20
# Author: xd

import re
import scrapy
from bs4 import BeautifulSoup

from employment.settings import HEADERS


class GxmdSpider(scrapy.Spider):
    """第三轮学科评估"""
    name = 'gxmd'
    allowed_domains = ['gov.cn']
    # start_urls可以设置多个
    start_urls = ['https://hudong.moe.gov.cn/school/wcmdata/getPage.jsp?listid=10000023&page=1']


    # redis_key = 'ranking:start_urls'  # redis_key,用于在redis 添加起始url
    custom_settings = {
        "DEFAULT_REQUEST_HEADERS": HEADERS
    }

    def parse(self, response):
        text = response.text
        pages = re.findall('共([0-9]+)页', text)[0]
        for page in range(1, int(pages)+1):
            url = f'https://hudong.moe.gov.cn/school/wcmdata/getDataIndex.jsp?listid=10000023&page={page}'
            yield scrapy.Request(url=url, callback=self.parse_info, dont_filter=True)

    def parse_info(self, response):
        text = response.text
        url = response.url
        soup = BeautifulSoup(text, "html.parser")
        data = soup.find_all('tr')

        allUniv = []
        for tr in data:  # 每一行，对应每一个学校
            ltd = tr.find_all('td')
            if len(ltd) == 0:
                continue
            singleUniv = []

            for td in ltd:
                if td.string:
                    singleUniv.append(td.string.strip())
                else:
                    singleUniv.append(' ')
            allUniv.append(singleUniv)

        for i in range(0, len(allUniv)):
            u = allUniv[i]
            # 序号	学校名称	学校标识码	主管部门	所在省	所在地	办学层次	备注
            item = {}
            item['序号'] = u[0]
            item['学校名称'] = u[1]
            item['学校标识码'] = u[2]
            item['主管部门'] = u[3]
            item['所在省'] = u[4]
            item['所在地'] = u[5]
            item['办学层次'] = u[6]
            item['备注'] = u[7]
            item['来源'] = '高校名单'
            item['url'] = url
            yield item



