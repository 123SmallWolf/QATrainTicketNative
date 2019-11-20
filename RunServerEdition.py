# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2019/10/25 13:11
# @Author  : LuYang
# @File    : RunServerEdition.py
from flask import Flask, request
from flask_bootstrap import Bootstrap
from flask_cors import *
from Frame import Frame
from pprint import pprint
import json


app = Flask(__name__)
# CORS(app, supports_credentials=True)
bootstrap = Bootstrap(app)
QATrainTickets = Frame()


def get_json_obj(request):
    in_dict = None
    if 'application/json' in request.headers.environ['CONTENT_TYPE']:
        in_dict = request.json
    elif 'application/x-www-form-urlencoded' in request.headers.environ['CONTENT_TYPE']:
        print('WARN: CONTENT_TYPE = x-www-form-urlencoded')
        in_dict = request.form.to_dict()
    return in_dict


def get_utt_sb(input):
    text = None
    privates = None
    user_date = None
    if isinstance(input, dict) and 'publicZone' in input.keys():
        publics = input['publicZone']
        if isinstance(publics, list) and len(publics) > 0:
            turn = publics[len(publics) - 1]
            if isinstance(turn, dict):
                text = turn.get('post', {}).get('utterance', None)

    if isinstance(input, dict):
        privates = input.get('privateZone', None)

    if isinstance(input, dict):
        user_date = input.get('userData', None)

    return text, privates, user_date


@app.route('/Response', methods=['POST'])
def register_Response():
    print('----------------Response------------------')
    inputs, session_block, user_date = get_utt_sb(get_json_obj(request))
    if inputs is None:
        print("inputs数据为空", request)
    if session_block is None:
        print("session_block数据解析不正确", request)
        return None
    if user_date is None:
        print("user_date数据解析不正确", request)
        return None

    print('------Before------')
    print('turn:{}'.format(QATrainTickets.turn))
    print('inputs information:{}'.format(inputs))
    # print('user_date:{}'.format(user_date))
    print('session_block:{}'.format(session_block))

    answer, confidence, slotInf, isOver, newUserData = QATrainTickets.process(dialogue=inputs, serverSessionBlock=session_block, serverDate=user_date)

    output = {
        "utterance": answer,
        "emotion": None,
        "confidence": confidence,
        "confidence_mean": 0.59,
        "newprivate": slotInf,
        "newuserdata": newUserData,
        "recommend": slotInf['crossArea'],  # default == None
        "isover": isOver
    }
    print('------After------')
    pprint('output information:{}'.format(output))
    print('###################################################################################')
    return json.dumps(output)


@app.route('/Activation', methods=['POST'])
def register_Activation():
    print('---------------Activation----------------')
    # 获得数据，按不同文本类型不同处理
    input, session_block, user_date = get_utt_sb(get_json_obj(request))
    if input is None or session_block is None:
        print("[ERROR]数据解析不正确", request)
        return None
    print('activation:input:{}'.format(input))
    # pprint(session_block)
    confidence = QATrainTickets.prejudge(input)  # , session_block, user_date
    # 直接允许通过
    output = {
        "confidence": confidence,
        "threshold": 0.59,
        "priority": 0.5
    }
    pprint('activation:output:{}'.format(output))
    return json.dumps(output)


if __name__ == '__main__':
   # app.run(host='127.0.0.1', port=5000)
    app.run(host='0.0.0.0', port=6680)
