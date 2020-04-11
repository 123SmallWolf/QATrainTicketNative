# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2019/10/10 17:47
# @Author  : LuYang
# @File    : nluProcess.py
from src.nlp_tools.entityExtractor import extractor
import json
import re
import datetime
import logging
logger = logging.getLogger('Frame.nlu')
logger.info('hello')

def date_change(currentData, flag: int):
    assert isinstance(flag, int), '更改日期出错'
    currentDay = datetime.datetime(int(currentData[0:4]), int(currentData[5:7]), int(currentData[8:10]))
    delta = datetime.timedelta(days=flag)
    changedDate = currentDay + delta
    my_yes_time = changedDate.strftime('%Y-%m-%d')
    return my_yes_time


def time_change(currentTime, flag: int):
    assert isinstance(flag, int), '更改时间出错'
    currentTime2 = datetime.datetime(int(currentTime[0:4]), int(currentTime[5:7]), int(currentTime[8:10]),
                                     int(currentTime[11:13]), int(currentTime[14:16]))
    delta = datetime.timedelta(minutes=flag)
    changedDate = currentTime2 + delta
    my_yes_time = changedDate.strftime('%Y-%m-%d/%H:%M').split('/')[1]
    return my_yes_time


def get_nlu_pattern(jsonPath):
    with open(jsonPath, 'r', encoding='utf-8') as jr:
        patterns = json.load(jr)
    return patterns['inform']


def understand_date_and_time(clientQues, slotInfo, nluPattern, confidence):
    """理解日期和时间"""
    # if slotInfo['departureDate'] is None:
    #     departureDate, _ = get_date(clientQues)
    #     slotInfo['departureDate'] = departureDate
    #
    # if slotInfo['departureTime'] is None or slotInfo['departureDate'] is None:
    #     _, departureTime = get_date(clientQues)
    #     slotInfo['departureTime'] = departureTime[:5] if departureTime is not None else None

    Patterns = nluPattern['tune_time']
    for pat in Patterns:
        regex = re.compile(pat['pattern'])
        if regex.search(clientQues) is not None:
            if pat['departureDate'] == '-1':  # 前一天
                slotInfo['departureDate'] = date_change(slotInfo['departureDate'], -1)
                confidence = pat['confidence']
                break

            if pat['departureDate'] == '+1':  # 后一天
                slotInfo['departureDate'] = date_change(slotInfo['departureDate'], +1)
                confidence = pat['confidence']
                break

            # if pat['departureTime'] == '-30':  # 早一点（早30分钟）
            #     slotInfo['departureTime'] = time_change(slotInfo['departureDate']+' '+slotInfo['departureTime'], -30)
            #     confidence = pat['confidence']
            #     break

            if pat['departureTime'] == '-':  # 早一点
                slotInfo['departureTime'] = slotInfo['firstStartTime'] if slotInfo['firstStartTime'] is not None else slotInfo['departureTime']
                slotInfo['nluState'] = 'u_earlier'
                confidence = pat['confidence']
                break

            if pat['departureTime'] == '+':  # 晚一点
                slotInfo['departureTime'] = slotInfo['lastStartTime'] if slotInfo['lastStartTime'] is not None else slotInfo['departureTime']
                slotInfo['nluState'] = 'u_later'
                confidence = pat['confidence']
                break

            # if pat['departureTime'] == '+30':  # 晚一点（晚30分钟）
            #     slotInfo['departureTime'] = time_change(slotInfo['departureDate']+' '+slotInfo['departureTime'], +30)
            #     confidence = pat['confidence']
            #     break

            if pat['departureTime'] == '?' and pat['departureDate'] == '?':  # 更改出行日期和时间
                departureDate, departureTime = get_date(clientQues)
                slotInfo['departureDate'] = departureDate
                slotInfo['departureTime'] = departureTime[:5] if departureTime is not None else None
                confidence = pat['confidence']
                break

            if pat['departureTime'] == '?' and pat['departureDate'] == '':  # 更改出行时间
                departureDate, departureTime = get_date(clientQues)
                slotInfo['departureTime'] = departureTime[:5] if departureTime is not None else None
                confidence = pat['confidence']
                break
        else:
            continue

    else:
        departureDate, departureTime = get_date(clientQues)
        if departureDate is not None:
            if slotInfo['departureDate'] is None:
                slotInfo['departureDate'] = departureDate
            else:
                if slotInfo['departureDate'] != departureDate:
                    slotInfo['departureDate'] = departureDate
                else:
                    pass
        else:
            pass

        if departureTime is not None:
            if slotInfo['departureTime'] is None:
                slotInfo['departureTime'] = departureTime
            else:
                if slotInfo['departureTime'] != departureTime:
                    slotInfo['departureTime'] = departureTime
                else:
                    pass
        else:
            pass

    return slotInfo, confidence


def check_location(locationList, rootPath):
    with open(rootPath+'/res/city_id.json', 'r', encoding='utf-8') as rj:
        name2Id = json.load(rj)

    if isinstance(locationList, list):
        for loc in locationList:
            assert loc in name2Id.keys(), '地点信息识别错误[%s]' % loc


def understand_departure_and_arrival(clientQues, slotInfo, nluPattern, confidence, rootPath):
    """"获取出发城市和到达城市"""
    if slotInfo['nlgState'] == 'askDeparture':
        location = get_location(clientQues)
        check_location(location, rootPath)
        if len(location) > 0:
            slotInfo['departure'] = location[0]
            slotInfo['nluState'] = 'u_departure_and_arrival'

    elif slotInfo['nlgState'] == 'reAskDeparture':
        location = get_location(clientQues)
        check_location(location, rootPath)
        if len(location) > 0:
            slotInfo['departure'] = location[0]
            slotInfo['nluState'] = 'u_departure_and_arrival'

    elif slotInfo['nlgState'] == 'askArrival':
        location = get_location(clientQues)
        check_location(location, rootPath)
        if len(location) > 0:
            slotInfo['arrival'] = location[0]
            slotInfo['nluState'] = 'u_departure_and_arrival'

    else:
        Patterns = nluPattern['enter_domain']
        location = get_location(clientQues)
        if len(location) > 0:
            check_location(location, rootPath)
            for loc in location:
                clientQues = re.sub(loc, '<city>', clientQues)
        for pat in Patterns:
            regex = re.compile(pat['pattern'])
            if regex.search(clientQues) is not None:
                if pat['departure'] == 'first' and pat['arrival'] == 'second':
                    slotInfo['departure'] = location[0]
                    slotInfo['arrival'] = location[1]
                    slotInfo['nluState'] = 'u_departure_and_arrival'
                    confidence = pat['confidence']
                    break

                if pat['departure'] == 'second' and pat['arrival'] == 'first':
                    slotInfo['departure'] = location[1]
                    slotInfo['arrival'] = location[0]
                    slotInfo['nluState'] = 'u_departure_and_arrival'
                    confidence = pat['confidence']
                    break

                if pat['departure'] == '' and pat['arrival'] == 'first':
                    slotInfo['arrival'] = location[0]
                    slotInfo['nluState'] = 'u_departure_and_arrival'
                    confidence = pat['confidence']
                    break

                if pat['departure'] == 'first' and pat['arrival'] == '':
                    slotInfo['departure'] = location[0]
                    slotInfo['nluState'] = 'u_departure_and_arrival'
                    confidence = pat['confidence']
                    break

                if pat['departure'] == '' and pat['arrival'] == '':
                    if slotInfo['newUsrDate']['desCity'] is not None or slotInfo['newUsrDate']['orgCity'] is not None:
                        slotInfo['arrival'] = slotInfo['newUsrDate']['desCity']
                        slotInfo['departure'] = slotInfo['newUsrDate']['orgCity']
                        slotInfo['departureDate'] = slotInfo['newUsrDate']['departDate']
                        slotInfo['nluState'] = 'u_departure_and_arrival'
                    # elif slotInfo['lastCityMentioned'] is not None:
                    #     slotInfo['arrival'] = slotInfo['lastCityMentioned']
                    #     slotInfo['nluState'] = 'u_departure_and_arrival'
                    elif slotInfo['lastCityMentioned'] is not None:
                        slotInfo['nluState'] = 'u_to_last_mentioned_city'

                    else:
                        slotInfo['nluState'] = 'u_departure_and_arrival'

                    confidence = pat['confidence']
                    break
            else:
                continue

    if slotInfo['departure'] is not None and slotInfo['arrival'] is not None and slotInfo['departure'] == slotInfo['arrival']:
        slotInfo['nluState'] = 'u_departure_and_arrival_identical'
        slotInfo['departure'] = None
        slotInfo['arrival'] = None

    return slotInfo, confidence


def understand_recommend(slotInfo, confidence):
    """理解推荐机制"""
    # noinspection PyBroadException
    if ((slotInfo['newUsrDate']['desCity'] is not None and slotInfo['arrival'] is None) or
        (slotInfo['newUsrDate']['orgCity'] is not None and slotInfo['departure'] is None) or
        (slotInfo['newUsrDate']['departDate'] is not None and slotInfo['departureDate'] is None)):

        slotInfo['departureDate'] = slotInfo['newUsrDate']['departDate']

        if slotInfo['departureDate'] is not None:
            slotInfo['departureTime'] = '00:00'

        slotInfo['arrival'] = slotInfo['newUsrDate']['desCity']
        slotInfo['departure'] = slotInfo['newUsrDate']['orgCity']

        slotInfo['nluState'] = 'u_recommendation'
        confidence += 0.01
        return slotInfo, confidence
    else:
        return slotInfo, confidence


def understand_book_or_bye(clientQues, slotInfo, nluPattern, confidence):
    """理解订票和取消订票"""
    Patterns = nluPattern['bookOrBye']
    for pat in Patterns:
        regex = re.compile(pat['pattern'])
        if regex.search(clientQues) is not None:
            if pat['attitude'] == 'p':
                slotInfo['nluState'] = 'u_book'
            if pat['attitude'] == 'n':
                slotInfo['nluState'] = 'u_bye'
            if pat['attitude'] == 'pn':
                slotInfo['nluState'] = 'u_continue'
            if pat['attitude'] == '?':
                slotInfo['nluState'] = 'u_other_recommendation'
            confidence = pat['confidence']
            break

    return slotInfo, confidence


def understand_train_type(clientQues, slotInfo, nluPattern, confidence):
    """理解选择的车型"""
    # noinspection PyBroadException
    Patterns = nluPattern['train_type']
    for pat in Patterns:
        regex = re.compile(pat['pattern'])
        if regex.search(clientQues) is not None:
            slotInfo['trainType'] = []

    if len(slotInfo['trainType']) == 0:
        for pat in Patterns:
            regex = re.compile(pat['pattern'])
            if regex.search(clientQues) is not None:
                slotInfo['trainType'].extend(pat['trainType'])
                confidence = pat['confidence']

    return slotInfo, confidence


def understand_seat_type(clientQues, slotInfo, nluPattern, confidence):
    """理解选择的坐席"""
    # noinspection PyBroadException
    Patterns = nluPattern['seat_type']
    for pat in Patterns:
        regex = re.compile(pat['pattern'])
        if regex.search(clientQues) is not None and slotInfo['nlgState'] != 'askTrainType':
            slotInfo['seatType'] = []

    if len(slotInfo['seatType']) == 0:
        for pat in Patterns:
            regex = re.compile(pat['pattern'])
            if regex.search(clientQues) is not None:
                if slotInfo['nlgState'] != 'askTrainType':
                    slotInfo['seatType'].extend(pat['seatType'])
                    confidence = pat['confidence']
                else:
                    pass

    return slotInfo, confidence


def understand_minimum_period(clientQues, slotInfo, nluPattern, confidence):
    """理解车次选取的条件"""
    Patterns = nluPattern['sequence']
    for pat in Patterns:
        regex = re.compile(pat['pattern'])
        if regex.search(clientQues) is not None:
            slotInfo['orderBy'] = pat['selectSequenceBy']
            slotInfo['nluState'] = 'u_min_period'
            confidence = pat['confidence']
            break

    return slotInfo, confidence


def understand_attitude(clientQues, slotInfo, nluPattern, confidence):
    """理解用户的态度"""
    # noinspection PyBroadException
    Patterns = nluPattern['attitudes']
    for pat in Patterns:
        regex = re.compile(pat['pattern'])
        if regex.search(clientQues) is not None:
            if pat['attitude'] == 'p':
                slotInfo['nluState'] = 'u_positive_attitude'
                confidence = pat['confidence']
                break

            if pat['attitude'] == 'n':
                slotInfo['nluState'] = 'u_negative_attitude'
                confidence = pat['confidence']
                break

    return slotInfo, confidence


def understand_cross_area(clientQues, slotInfo, nluPattern, confidence):
    """理解交叉domain"""
    # noinspection PyBroadException
    Patterns = nluPattern['crossArea']
    for pat in Patterns:
        regex = re.compile(pat['pattern'])
        if regex.search(clientQues) is not None:
            slotInfo['nluState'] = 'u_cross_area'
            confidence = pat['confidence']
            break

    return slotInfo, confidence


def nlu_process(clientQues, slotInfo, nluPattern, confidence, rootPath):
    clientQues = clientQues.strip()
    slotInfo, confidence = understand_cross_area(clientQues, slotInfo, nluPattern, confidence)
    slotInfo, confidence = understand_recommend(slotInfo, confidence)
    slotInfo, confidence = understand_book_or_bye(clientQues, slotInfo, nluPattern, confidence)
    if slotInfo['nluState'] == 'u_bye':
        return slotInfo, confidence
    slotInfo, confidence = understand_departure_and_arrival(clientQues, slotInfo, nluPattern, confidence, rootPath)
    slotInfo, confidence = understand_date_and_time(clientQues, slotInfo, nluPattern, confidence)
    slotInfo, confidence = understand_train_type(clientQues, slotInfo, nluPattern, confidence)
    slotInfo, confidence = understand_seat_type(clientQues, slotInfo, nluPattern, confidence)
    slotInfo, confidence = understand_minimum_period(clientQues, slotInfo, nluPattern, confidence)
    slotInfo, confidence = understand_attitude(clientQues, slotInfo, nluPattern, confidence)
    slotInfo, confidence = understand_cross_area(clientQues, slotInfo, nluPattern, confidence)
    return slotInfo, confidence


def get_date(clientQues):
    ext = extractor()
    extracts = ext.extract_time(clientQues)
    extracts = json.loads(extracts)
    # noinspection PyBroadException
    try:
        edate, etime = extracts['timestamp'].split(' ')
        return edate, etime
    except Exception:
        return None, None


def get_location(clientQues):
    ext = extractor()
    extracts = ext.extract_locations(clientQues)
    return extracts


if __name__ == '__main__':
    ex = extractor()
    sentence = '北京'
    d, t = get_date(sentence)
    print(d, t)
    de = ex.extract_locations(sentence)
    # de, ar = get_location(sentence)
    print(de)

    print(date_change('2019-10-01', +1))
