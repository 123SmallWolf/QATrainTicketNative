# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2019/10/14 10:35
# @Author  : LuYang
# @File    : RunOriginEdition.py
from Frame import Frame
from pprint import pprint

# server_date = {"place": [{"province": "山东省", "city": "青岛市", "departDate": "2019-11-11"}]}
server_date = None

sessionBlock = {}
session = Frame()
while True:
    print('<<< ', end='')
    query = input()
    preConfidence = session.prejudge(query)  # , sessionBlock, server_date
    print(preConfidence)
    answer, confidence, slotInf, isOver, _ = session.process(query, sessionBlock, server_date)
    sessionBlock = slotInf
    print('>>>[cfd:{:.2}] {}'.format(confidence, answer))
    # pprint(session.slotInfo)
