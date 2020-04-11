# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2019/10/10 17:47
# @Author  : LuYang
# @File    : Frame.py
from src.nlu.nluProcess import nlu_process
from src.dm.dmProcess import dm_process
from src.nlg.nlgProcess import nlg_process
import os
import json
import copy
import re
import logging

logger = logging.getLogger('Frame')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')

fh = logging.FileHandler('logging.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)


whole_nlu_state = ['enter_domain', 'u_earlier', 'u_later', 'u_departure_and_arrival',
                   'u_departure_and_arrival_identical', 'u_book', 'u_bye', 'u_continue',
                   'u_other_recommendation', 'u_min_period', 'u_read_sever_date',
                   'u_positive_attitude', 'u_negative_attitude', 'u_recommendation', 'u_cross_area',
                   'u_to_last_mentioned_city']


class Frame(object):
    def __init__(self):
        self.rootPath = os.path.dirname(__file__)
        self.slotInfo = {}
        self.confidence = 0.5
        self.slotInfo = self.init_slot_info(self.slotInfo)
        self.nluPattern = self.get_nlu_pattern(self.rootPath + '/res/pattern.json')
        self.wholeTrainInform = None
        self.turn = 0
        self.lastCity = None
        self.newUserDate = {'orgCity': None, 'desCity': None, 'departDate': None}

    @staticmethod
    def init_slot_info(slotDict):
        slotDict['departure'] = None        # 出发城市
        slotDict['arrival'] = None          # 到达城市
        slotDict['departureDate'] = None    # 出发日期：yyyy-mm-dd
        slotDict['departureTime'] = None    # 出发精确时间
        slotDict['trainType'] = []          # 列车类型，例如只看动车/高铁
        slotDict['seatType'] = []           # 席别类型
        slotDict['orderBy'] = None          # 筛选的条件
        slotDict['nlgState'] = None         # nlg状态
        slotDict['nluState'] = None         # nlu状态
        slotDict['sessionOver'] = None      # 用于记录多轮对话是否结束
        slotDict['firstStartTime'] = None
        slotDict['lastStartTime'] = None
        slotDict['lastCityMentioned'] = None
        slotDict['crossArea'] = None
        slotDict['url'] = None
        slotDict['newUsrDate'] = {'orgCity': None, 'desCity': None, 'departDate': None}

        return slotDict

    @staticmethod
    def get_nlu_pattern(jsonPath):
        with open(jsonPath, 'r', encoding='utf-8') as jr:
            patterns = json.load(jr)
        return patterns

    @staticmethod
    def get_last_city_mentioned(userDate):
        user_date = userDate if isinstance(userDate, dict) else dict({})
        last_city = None
        last_cities = user_date.get('place', [])
        if len(last_cities) > 0:
            c = last_cities[-1]
            if isinstance(c, dict):
                last_city = c.get('city', '')

                last_city = last_city[:-1] if (last_city != '' and last_city is not None) else None
        return last_city

    @staticmethod
    def get_new_user_date_mentioned(userDate):
        new_user_date = userDate if isinstance(userDate, dict) else dict({})
        new_user_date['orgCity'] = new_user_date.get('orgCity', None)
        new_user_date['desCity'] = new_user_date.get('desCity', None)
        new_user_date['departDate'] = new_user_date.get('departDate', None)

        return {'orgCity': new_user_date['orgCity'], 'desCity': new_user_date['desCity'], 'departDate': new_user_date['departDate']}

    def __confidence_update(self, flag):
        if flag == '+':
            for patternType in self.nluPattern:
                for singlePattern in self.nluPattern[patternType]:
                    if singlePattern['confidence'] >= 0.85:
                        continue
                    else:
                        singlePattern['confidence'] += 0.01

        if flag == '-':
            for patternType in self.nluPattern:
                for singlePattern in self.nluPattern[patternType]:
                    if singlePattern['confidence'] <= 0.6:
                        continue
                    else:
                        singlePattern['confidence'] -= 0.005

    def __clear_inform(self):
        self.slotInfo = self.init_slot_info(self.slotInfo)

    def __call__(self, *args, **kwargs):
        return

    def process(self, dialogue, serverSessionBlock, serverDate):
        self.turn += 1

        self.slotInfo = self.init_slot_info(self.slotInfo) if serverSessionBlock == {} else serverSessionBlock

        self.slotInfo['lastCityMentioned'] = self.get_last_city_mentioned(serverDate)
        self.slotInfo['newUsrDate'] = self.get_new_user_date_mentioned(serverDate)

        self.slotInfo, self.confidence = nlu_process(dialogue, self.slotInfo, self.nluPattern, self.confidence, self.rootPath)

        self.newUserDate = {'orgCity': self.slotInfo['departure'], 'desCity': self.slotInfo['arrival'], 'departDate': self.slotInfo['departureDate']}

        if self.slotInfo['nluState'] in whole_nlu_state:
            # self.__confidence_update('+')
            severQuesFlag = dm_process(self.slotInfo)
            if severQuesFlag in ['continueQuery', 'stopQuery']:
                self.__clear_inform()
            severQuesGenerated, self.slotInfo = nlg_process(severQuesFlag, self.slotInfo, self.rootPath)

            # if self.slotInfo['nlgState'] == 'stopQuery':
            #     self.slotInfo['sessionOver'] = True
            #     self.slotInfo['crossArea'] = None
            if self.slotInfo['nluState'] == 'u_cross_area':
                self.__clear_inform()
                self.slotInfo['crossArea'] = 'book_ticket'
                self.confidence = 0.5
                return None, '{:.2f}'.format(self.confidence), self.slotInfo, True, self.newUserDate
            else:
                self.slotInfo['crossArea'] = None
                self.slotInfo['sessionOver'] = False

            if severQuesGenerated == '本次查询结束，小智期待下次为您服务！':
                self.__clear_inform()
                self.slotInfo['sessionOver'] = True
                self.confidence = 0.5
                self.newUserDate = {'orgCity': None, 'desCity': None, 'departDate': None}
            elif severQuesGenerated == '请您输入出行信息':
                self.__clear_inform()
                self.newUserDate = {'orgCity': None, 'desCity': None, 'departDate': None}
            # print('AAAAAAAAAAAAAAAAAAAAAAAAAAAA\n')
            # print(severQuesGenerated)
            return severQuesGenerated, '{:.2f}'.format(self.confidence), self.slotInfo, self.slotInfo['sessionOver'], self.newUserDate

        else:
            logger.info('当前聊天内容不在火车票domain')
            # self.__confidence_update('-')
            return None, '{:.2f}'.format(0.5), self.slotInfo, self.slotInfo['sessionOver'], self.newUserDate

    def prejudge(self, dialogue):
        for kind in self.nluPattern.keys():
            for pat in self.nluPattern[kind]:
                regex = re.compile(pat['pattern'])
                if regex.search(dialogue) is not None:
                    # cfd = pat['confidence']
                    # self.confidence = cfd
                    # return '{:.2f}'.format(self.confidence)
                    if kind == 'enter_domain':
                        cfd = pat['confidence']
                        self.confidence = cfd
                        return '{:.2f}'.format(self.confidence)
                    elif self.slotInfo['nluState'] in whole_nlu_state:
                        cfd = pat['confidence']
                        self.confidence = cfd
                        return '{:.2f}'.format(self.confidence)
                    else:
                        return '{:.2f}'.format(0.5)
        else:
            if self.slotInfo['nluState'] in whole_nlu_state:
                with open(self.rootPath + '/res/city_id.json', 'r', encoding='utf-8') as rj:
                    name2Id = json.load(rj)
                if dialogue[-1] in ['.', '。', '?', '？', '!', '！', ',', '，']:
                    dialogue = dialogue[:-1]
                if dialogue in name2Id.keys():
                    return '{:.2f}'.format(0.65)
                else:
                    return '{:.2f}'.format(0.5)
            else:
                return '{:.2f}'.format(0.5)
