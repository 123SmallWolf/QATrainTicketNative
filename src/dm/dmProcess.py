# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2019/10/10 17:47
# @Author  : LuYang
# @File    : dmProcess.py


def dm_process(slotInfo):
    if slotInfo['nluState'] == 'u_recommendation':
        if slotInfo['departure'] is None:
            return 'askDeparture'
        elif slotInfo['arrival'] is None:
            return 'askArrival'
        elif slotInfo['departureDate'] is None:
            return 'askDepartureDate'
        elif len(slotInfo['trainType']) == 0:
            return 'askTrainType'
        elif len(slotInfo['seatType']) == 0:
            return 'askSeatType'
        else:
            return 'confirm'

    if slotInfo['nlgState'] == 'makeSureToLastMentionedCity' and slotInfo['nluState'] == 'u_positive_attitude':
        return 'askDeparture'
    if slotInfo['nlgState'] == 'makeSureToLastMentionedCity' and slotInfo['nluState'] == 'u_negative_attitude':
        return 'askArrival'
    if slotInfo['nluState'] == 'u_to_last_mentioned_city':
        slotInfo['arrival'] = slotInfo['lastCityMentioned']
        return 'makeSureToLastMentionedCity'

    if slotInfo['nluState'] == 'u_bye':  # 用户想要退出订票
        return 'stopQuery'
    elif slotInfo['nluState'] == 'u_book':  # 用户想要订票
        return 'supportBOOKLink'
    elif slotInfo['nluState'] == 'u_continue':  # 用户
        return 'continueQuery'
    elif slotInfo['nluState'] == 'u_other_recommendation':
        return 'askEarlierOrLater'
    elif slotInfo['nluState'] == 'u_departure_and_arrival_identical':
        return 'reAskDeparture'
    elif slotInfo['nluState'] == 'u_read_sever_date':
        return 'askToKnownCity'
    elif slotInfo['nluState'] == 'u_positive_attitude':
        return 'askDeparture'
    elif slotInfo['nluState'] == 'u_negative_attitude':
        return 'askArrival'
    elif slotInfo['nluState'] == 'u_cross_area':
        return 'prepareCrossArea'
    elif slotInfo['departure'] is None:
        return 'askDeparture'
    elif slotInfo['arrival'] is None:
        return 'askArrival'
    elif slotInfo['departureDate'] is None:
        return 'askDepartureDate'
    elif len(slotInfo['trainType']) == 0:
        return 'askTrainType'
    elif (slotInfo['departure'] is not None and slotInfo['arrival'] is not None and
          slotInfo['departureDate'] is not None and slotInfo['departureTime'] is not None and
          len(slotInfo['trainType']) != 0):
        return 'confirm'
    else:
        print('something wrong!\n')
