# -*- coding: utf-8 -*-
"""
@Author : Shimon.Zhang
@Date   : 2020/6/2 10:22
@Desc   : 身份证接口爬取
"""
import requests
from lxml import etree
import sys
import os
import datetime
import time
import pandas as pd

def run(id_card):
    session = requests.session()
    url = "https://mid.weixingmap.com/"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36"
    }
    response = session.get(url=url, headers=headers).text
    __VIEWSTATE = etree.HTML(response).xpath('//input[@name="__VIEWSTATE"]/@value')[0]
    __VIEWSTATEGENERATOR = etree.HTML(response).xpath('//input[@name="__VIEWSTATEGENERATOR"]/@value')[0]
    __EVENTVALIDATION = etree.HTML(response).xpath('//input[@name="__EVENTVALIDATION"]/@value')[0]
    chaxun = "查询"

    data = {
        "__VIEWSTATE": __VIEWSTATE,
        "__VIEWSTATEGENERATOR": __VIEWSTATEGENERATOR,
        "__EVENTVALIDATION": __EVENTVALIDATION,
        "idcard": id_card,
        "chaxun": chaxun
    }

    resp = session.post(url=url, data=data).text
    code = etree.HTML(resp).xpath('//span[@id="code"]/text()')
    if len(code) == 0:
        print(id_card, "证件号码错误！")
        r_diqu = "证件号码错误！"
    else:
        diqu = etree.HTML(resp).xpath('//span[@id="diqu"]/text()')
        #shengri = etree.HTML(resp).xpath('//span[@id="shengri"]/text()')[0]
        #xingbie = etree.HTML(resp).xpath('//span[@id="xingbie"]/text()')[0]
        if len(diqu) == 0:
            print(id_card, "未查到发证地！")
            r_diqu = "未查到发证地！"
        else:
            print(id_card, diqu)
            r_diqu = diqu[0]
    #return {"code": code, "diqu": diqu, "shengri": shengri, "xingbie": xingbie}
    return {"diqu": r_diqu}


if __name__ == '__main__':
    '''
    if len(sys.argv) < 2:
        print("请带上身份证号码！")
    else:
        data = run(sys.argv[1])
        print(data)
    '''
    id_card_file = 'id_card.xlsx'
    round_nums_max = 3  # 扫描所查询文件的最大次数
    start_time = datetime.datetime.now()
    print('开始处理时间：', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    id_card_data = pd.read_excel(id_card_file, converters={'id_card':str, '发证地':str})
    total_id_card_query_begin = len(list(id_card_data.loc[id_card_data['发证地'].isnull(), 'id_card']))
    id_card_list = list(id_card_data.loc[id_card_data['发证地'].isnull(), 'id_card'])
    for id_card in id_card_list:
        result = run(id_card)
        id_card_data.loc[id_card_data['id_card'] == id_card, '发证地'] = result['diqu']

    id_card_data.to_excel(id_card_file, index=None)

    end_time = datetime.datetime.now()
    all_time = (end_time - start_time).seconds
    print('结束处理！当前时间：', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print('共耗时：', all_time // 3600, '时', (all_time % 3600) // 60, '分', (all_time % 3600) % 60, '秒')
    os.system("pause")

