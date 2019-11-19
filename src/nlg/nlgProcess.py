# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2019/10/10 17:47
# @Author  : LuYang
# @File    : nlgProcess.py
import re
import urllib.parse
import heapq
import datetime
from src.nlg.query import query_tickets


def gain_answer_pattern(flag):
    answer_pattern = {
        "confirm": "根据您的需求，小智向您推荐<date>，从<departure>到<arrival>以下班次的列车，您可以选择[第一个/第二个]预定车次或更改查询条件再次查询",
        "confirmButEmpty": "小智没有为您查询到有效的列车信息，您可以修改查询信息再次尝试查询",
        "confirmButEmptyBySeat": "根据您选择的席别和出发时间，目前所有车次该席别的车票都已售尽，您可以选择其他席别或调整出发时间后再尝试查询。",
        "confirmButEmptyByLatest": "根据您选择的出发时间，已经没有更晚车次为您推荐，您可以输入已推荐车次编号购买车票或调整出发时间后再尝试查询。",
        "confirmButEmptyByEarliest": "根据您选择的出发时间，已经没有更早车次为您推荐，您可以输入已推荐车次编号购买车票或调整出发时间后再尝试查询。",
        "supportBOOKLink": "好的，您可以点击下方链接或复制下方链接到网页购买车票：",
        "askDepartureDate": "请问您的出行日期和出发时间？",
        "askDepartureTime": "请问您对出发时间有要求吗？",
        "askDeparture": "请问您的出发城市？",
        "askArrival": "请问您的目的城市？",
        "askTrainType": "请问您对列车类型有要求吗（例如动车、高铁、特快、普快等）？",
        "askSeatType": "请问您对座位席别有要求吗（例如商务座、一等座、二等座、硬卧、软卧等）？",
        "askEarlierOrLater": "请问您想出发时间早一点还是晚一点？",
        "askMoreServices": "请问您还需要查询其他车次吗？",
        "continueQuery": "请您输入出行信息",
        "reAskDeparture": "您选择的出发地和目的地相同，请您重新输入出发城市",
        "stopQuery": "好的，期待您下次继续使用火车票查询服务，小智将竭诚为您服务！",
        "askToKnownCity": "请问您是想预定去<arrival>的火车票吗？",
        "makeSureToLastMentionedCity": "请问您是想预定去<arrival>的火车票吗？",
        "prepareCrossArea": None
    }
    return answer_pattern[flag]


def generate_top3(informs):
    topN = 2
    result = []
    for inform in informs:
        if inform['train_no'][0] in ['D', 'G', 'C']:
            result.append('[{}]次列车，从[{}]站到[{}]站，出发时间[{}]，到达时间[{}]，预计时长[{}]'.format(  # ，商务座:{}，一等座:{}，二等座:{}，无座:{}
                inform['train_no'],
                inform['from_station_code'],
                inform['to_station_code'],
                inform['start_time'],
                inform['arrive_time'],
                inform['period']
                # inform['swz_num'],
                # inform['zy_num'],
                # inform['ze_num'],
                # inform['wz_num']
            ))
        else:
            result.append('[{}]次列车，从[{}]站到[{}]站，出发时间[{}]，到达时间[{}]，预计时长[{}]'.format(  # ，高级软卧:{}，软卧:{}，硬卧:{}，软座:{}，硬座:{}，无座:{}
                inform['train_no'],
                inform['from_station_code'],
                inform['to_station_code'],
                inform['start_time'],
                inform['arrive_time'],
                inform['period']
                # inform['gr_num'],
                # inform['rw_num'],
                # inform['yw_num'],
                # inform['rz_num'],
                # inform['yz_num'],
                # inform['wz_num']
            ))

    if len(result) > topN:
        return '\n'.join(result[:topN]), informs[0]['start_time'], informs[topN-1]['start_time']
    elif len(result) == 0:
        return '\n'.join(result[:]), None, None
    else:
        return '\n'.join(result[:]), informs[0]['start_time'], informs[len(result)-1]['start_time']


def sort_train_info(trainInforms, slotInfo):
    if slotInfo['departureTime'] is None:
        slotInfo['departureTime'] = '00:00'
    if slotInfo['nluState'] == 'u_earlier':
        tops = sorted(trainInforms, key=lambda s: s['start_time'], reverse=True)
        for top in tops:
            if top['start_time'] < slotInfo['departureTime']:
                yield top

    elif slotInfo['nluState'] == 'u_later':
        tops = sorted(trainInforms, key=lambda s: s['start_time'])
        for top in tops:
            if top['start_time'] > slotInfo['departureTime']:
                yield top

    elif slotInfo['nluState'] == 'u_min_period':
        tops = sorted(trainInforms, key=lambda s: s['period'])
        for top in tops:
            yield top

    else:
        tops = sorted(trainInforms, key=lambda s: s['start_time'])
        for top in tops:
            if top['start_time'] > slotInfo['departureTime']:
                yield top


def nlg_process(severQuesFlag, slotInfo, rootPath):
    if slotInfo['nluState'] == 'u_book':
        _, url = query_tickets(slotInfo, rootPath)
        url = urllib.parse.unquote(url, encoding="utf-8")
        url2 = str(url)
        bookLink = '<a target="_blank" href=' + url2 + '>立即订票</a>'
        # inputStr = '<a target="_blank" href="/item/%E6%95%99%E5%AD%A6">教学</a>'
        bookLink = '<a target="_blank" href=' + url2 + '>立即订票</a>'
        bookLink = str(bookLink)
        # bookLink = <a href="" target="_blank">立即订票</a>
        # bookLink = '<a href=\"' + url + '\" target=\"_blank\">立即订票</a>'
        # return gain_answer_pattern(severQuesFlag) + '\n' + url + '\n' + gain_answer_pattern('askMoreServices'), slotInfo
        return bookLink, slotInfo
    elif severQuesFlag in ['askToKnownCity', 'makeSureToLastMentionedCity']:
        severQues = gain_answer_pattern(severQuesFlag)
        severQues = re.sub(r'<arrival>', slotInfo['arrival'], severQues)
        return severQues, slotInfo,
    elif severQuesFlag == 'confirm' and slotInfo['nluState'] not in ['u_bye', 'u_book', 'u_continue']:
        severQues = gain_answer_pattern(severQuesFlag)
        severQues = re.sub(r'<date>', slotInfo['departureDate'], severQues)
        severQues = re.sub(r'<departure>', slotInfo['departure'], severQues)
        severQues = re.sub(r'<arrival>', slotInfo['arrival'], severQues)

        train_info, _ = query_tickets(slotInfo, rootPath)
        train_info = list(sort_train_info(train_info, slotInfo))
        recommendation, firstStartTime, lastStartTime = generate_top3(train_info)

        if recommendation != '':
            slotInfo['nlgState'] = 'confirm'
            slotInfo['firstStartTime'], slotInfo['lastStartTime'] = (firstStartTime, lastStartTime) if firstStartTime < lastStartTime else (lastStartTime, firstStartTime)
            return severQues + '\n' + recommendation, slotInfo
        elif recommendation == '' and slotInfo['nluState'] == 'u_seat_type':
            slotInfo['nlgState'] = 'confirmButEmptyBySeat'
            return gain_answer_pattern('confirmButEmptyBySeat'), slotInfo
        elif recommendation == '' and slotInfo['nluState'] == 'u_earlier':
            slotInfo['nlgState'] = 'confirmButEmptyByEarliest'
            return gain_answer_pattern('confirmButEmptyByEarliest'), slotInfo
        elif recommendation == '' and slotInfo['nluState'] == 'u_later':
            slotInfo['nlgState'] = 'confirmButEmptyByLatest'
            return gain_answer_pattern('confirmButEmptyByLatest'), slotInfo
        elif recommendation == '':
            slotInfo['nlgState'] = 'confirmButEmpty'
            return gain_answer_pattern('confirmButEmpty'), slotInfo
        else:
            pass
    else:
        slotInfo['nlgState'] = severQuesFlag
        return gain_answer_pattern(severQuesFlag), slotInfo
