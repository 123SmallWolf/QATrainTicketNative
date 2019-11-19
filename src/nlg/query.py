# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2019/10/10 17:47
# @Author  : LuYang
# @File    : query.py
import urllib.parse
import requests
import re
import json
import collections
from pprint import pprint
# from selenium import webdriver


def query_tickets(slotInfo, rootPath):
    assert isinstance(slotInfo, dict), 'slotInfo type wrong!'

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
               "Host": "kyfw.12306.cn",
               "Referer": "https://kyfw.12306.cn/otn/leftTicket/init",
               "X-Requested-With": "XMLHttpRequest"}
    init_url = 'https://kyfw.12306.cn/otn/leftTicket/init'

    left_url = 'https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date=2019-10-23&leftTicketDTO.from_station=WHN&leftTicketDTO.to_station=TJP&purpose_codes=ADULT'

    data = {'linktypeid': 'dc',
            'fs': None,
            'ts': None,
            'data': None,
            'flag': None}

    data['fs'] = slotInfo['departure']
    data['ts'] = slotInfo['arrival']
    data['data'] = slotInfo['departureDate']
    data['flag'] = 'N,N,Y' if slotInfo['trainType'] not in ['D', 'G', 'C'] else 'N,Y,Y'

    with open(rootPath+'/res/city_id.json', 'r', encoding='utf-8') as rj:
        cityId = json.load(rj)
        left_url = ("https://kyfw.12306.cn/otn/leftTicket/query?"
                    "leftTicketDTO.train_date={}"
                    "&leftTicketDTO.from_station={}"
                    "&leftTicketDTO.to_station={}"
                    "&purpose_codes=ADULT").format(data['data'], cityId[data['fs']], cityId[data['ts']])

        data['fs'] = data['fs'] + ',' + cityId[data['fs']]
        data['ts'] = data['ts'] + ',' + cityId[data['ts']]

    payload = urllib.parse.urlencode(data, encoding='utf-8')
    payload = re.sub('%2C', ',', payload)

    q = requests.Session()
    url1 = init_url + '?' + payload
    r = q.get(url1, headers=headers)

    l = q.get(left_url, headers=headers)

    inf = js_transform(json.loads(l.text)['data']['result'], rootPath, slotInfo)

    return inf, r.url


def js_transform(data, rootPath, slotInfo):
    trainInform = []
    with open(rootPath+'/res/city_id.json', 'r', encoding='utf-8') as rj:
        name2Id = json.load(rj)
        id2Name = {v: k for k, v in name2Id.items()}

    for subDate in data:
        splitSubData = subDate.split('|')
        # cw = {'secretHBStr': '', 'secretStr': '', 'buttonTextInfo': ''}
        # cw['secretHBStr'] = splitSubData[36]
        # cw['secretStr'] = splitSubData[0]  # secretStr索引为0
        # cw['buttonTextInfo'] = splitSubData[1]
        cu = {
            'start_time': '',
            'arrive_time': '',
            'period': '',

            'start_station_code': '',
            'end_station_code': '',

            'from_station_code': '',
            'to_station_code': '',

            'canWebBuy': '',
            'start_train_date': '',
            'station_train_code': '',

            'rw_num': '',  # 软卧
            'yw_num': '',  # 硬卧
            'rz_num': '',  # 软座
            'yz_num': '',  # 硬座
            'wz_num': '',  # 无座
            'ze_num': '',  # 二等座
            'zy_num': '',  # 一等座
            'swz_num': ''  # 商务特等座
        }
        cu = collections.OrderedDict()
        cu['train_no'] = splitSubData[3]  # 车次
        cu['start_station_code'] = id2Name[splitSubData[4]]  # 起始站代号
        cu['end_station_code'] = id2Name[splitSubData[5]]  # 终点站代号
        cu['from_station_code'] = id2Name[splitSubData[6]]  # 出发站代号
        cu['to_station_code'] = id2Name[splitSubData[7]]  # 到达站代号
        cu['start_time'] = splitSubData[8]  # 出发时间
        cu['arrive_time'] = splitSubData[9]  # 到达时间
        cu['period'] = splitSubData[10]  # 历时
        cu['canWebBuy'] = splitSubData[11]  # 是否能购买：Y 可以
        cu['yp_info'] = splitSubData[12]
        cu['start_train_date'] = splitSubData[13]  # 出发日期
        cu['train_seat_feature'] = splitSubData[14]
        # cu['location_code'] = splitSubData[15]
        # cu['from_station_no'] = splitSubData[16]
        # cu['to_station_no'] = splitSubData[17]
        # cu['is_support_card'] = splitSubData[18]
        cu['controlled_train_flag'] = splitSubData[19]
        cu['gg_num'] = splitSubData[20]
        cu['gr_num'] = splitSubData[21] if splitSubData[21] != '' else '无'  # 高级软卧
        cu['qt_num'] = splitSubData[22] if splitSubData[22] != '' else '无'  # 其他
        cu['rw_num'] = splitSubData[23] if splitSubData[23] != '' else '无'  # 软卧
        cu['rz_num'] = splitSubData[24] if splitSubData[24] != '' else '无'  # 软座
        # cu['tz_num'] = splitSubData[25]
        cu['wz_num'] = splitSubData[26] if splitSubData[26] != '' else '无'  # 无座
        # cu['yb_num'] = splitSubData[27]
        cu['yw_num'] = splitSubData[28] if splitSubData[28] != '' else '无'  # 硬卧
        cu['yz_num'] = splitSubData[29] if splitSubData[29] != '' else '无'  # 硬座
        cu['ze_num'] = splitSubData[30] if splitSubData[30] != '' else '无'  # 二等座
        cu['zy_num'] = splitSubData[31] if splitSubData[31] != '' else '无'  # 一等座
        cu['swz_num'] = splitSubData[32] if splitSubData[32] != '' else '无'  # 商务座
        cu['srrb_num'] = splitSubData[33]
        # cu['yp_ex'] = splitSubData[34]
        cu['seat_types'] = splitSubData[35]
        # cu['exchange_train_flag'] = splitSubData[36]
        # cu['from_station_name'] = cv[splitSubData[6]]
        # cu['to_station_name'] = cv[splitSubData[7]]
        # print(cu)
        existTicketsCondition = ''.join(list(cu['swz_num'] + cu['zy_num'] + cu['ze_num'] + cu['wz_num'] + cu['yz_num'] +
                                             cu['yw_num'] + cu['rz_num'] + cu['rw_num'] + cu['gr_num']))
        existSeatsCondition = ''.join(list(cu['swz_num'] + cu['zy_num'] + cu['ze_num'] + cu['yz_num'] + cu['yw_num'] +
                                           cu['rz_num'] + cu['rw_num'] + cu['gr_num']))
        ticketsDistribution = {'商务座': cu['swz_num'],
                               '一等座': cu['zy_num'],
                               '二等座': cu['ze_num'],
                               '高级软卧': cu['gr_num'],
                               '软卧': cu['rw_num'],
                               '硬卧': cu['yw_num'],
                               '软座': cu['rz_num'],
                               '硬座': cu['yz_num'],
                               '无座': cu['wz_num']}

        if cu['canWebBuy'] == 'Y':
            if cu['train_no'][0] in slotInfo['trainType']:
                if len(slotInfo['seatType']) == 0:  # 席别未做要求
                    if slotInfo['orderBy'] == 'existTickets' and existTicketsCondition != '无' * 9:  # 有票
                        trainInform.append(cu)
                    elif slotInfo['orderBy'] == 'existSeats' and existSeatsCondition != '无' * 8:  # 有座
                        trainInform.append(cu)
                    elif slotInfo['orderBy'] == 'minPeriod':
                        trainInform.append(cu)
                    elif slotInfo['orderBy'] is None:
                        trainInform.append(cu)
                else:  # 席别有要求
                    try:
                        for seat in slotInfo['seatType']:
                            if ticketsDistribution[seat] != '无':
                                trainInform.append(cu)
                                break
                    except KeyError as e:
                        print(e)
        else:
            pass

    return trainInform


if __name__ == '__main__':
    slotInfo = {}
    slotInfo['departure'] = '北京'
    slotInfo['arrival'] = '天津'
    slotInfo['departureDate'] = '2019-10-23'
    slotInfo['trainType'] = 'N,N,Y'
    result, url0 = query_tickets(slotInfo, r'C:\Users\80693\PycharmProjects\QATrainTicketNative')
    pprint(result)
    print(url0)
