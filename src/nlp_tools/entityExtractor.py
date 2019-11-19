import regex as re
from src.nlp_tools.normalizeTime import TimeNormalizer
from pyhanlp import *
from itertools import groupby


class extractor():
    def __init__(self):
        pass

    def get_location(self, word_pos_list):
        """
        get location by the pos of the word, such as 'ns'
        eg: get_location('内蒙古赤峰市松山区')


        :param: word_pos_list<list>
        :return: location_list<list> eg: ['陕西省安康市汉滨区', '安康市汉滨区', '汉滨区']

        """
        location_list = []
        if word_pos_list == []:
            return []

        for i, t in enumerate(word_pos_list):
            word = t[0]
            nature = t[1]
            if nature == 'ns':
                loc_tmp = word
                count = i + 1
                while count < len(word_pos_list):
                    next_word_pos = word_pos_list[count]
                    next_pos = next_word_pos[1]
                    next_word = next_word_pos[0]
                    if next_pos == 'ns' or 'n' == next_pos[0]:
                        loc_tmp += next_word
                    else:
                        break
                    count += 1
                location_list.append(loc_tmp)

        return location_list  # max(location_list)

    def extract_locations(self, text):
        """
        extract locations by from texts
        eg: extract_locations('我家住在陕西省安康市汉滨区。')


        :param: raw_text<string>
        :return: location_list<list> eg: ['陕西省安康市汉滨区', '安康市汉滨区', '汉滨区']

        """
        if text == '':
            return []
        seg_list = [(str(t.word), str(t.nature)) for t in HanLP.segment(text)]
        location_list = self.get_location(seg_list)
        return location_list

    def replace_chinese(self, text):
        """
        remove all the chinese characters in text
        eg: replace_chinese('我的email是ifee@baidu.com和dsdsd@dsdsd.com,李林的邮箱是eewewe@gmail.com哈哈哈')


        :param: raw_text
        :return: text_without_chinese<str>
        """
        if text == '':
            return []
        filtrate = re.compile(u'[\u4E00-\u9FA5]')
        text_without_chinese = filtrate.sub(r' ', text)
        return text_without_chinese

    def replace_cellphoneNum(self, text):
        """
        remove cellphone number from texts. If text contains cellphone No., the extract_time will report errors.
        hence, we remove it here.
        eg: extract_locations('我家住在陕西省安康市汉滨区，我的手机号是181-0006-5143。')


        :param: raw_text<string>
        :return: text_without_cellphone<string> eg: '我家住在陕西省安康市汉滨区，我的手机号是。'

        """
        eng_texts = self.replace_chinese(text)
        sep = ',!?:; ：，.。！？《》、|\\/abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        eng_split_texts = [''.join(g) for k, g in groupby(eng_texts, sep.__contains__) if not k]
        eng_split_texts_clean = [ele for ele in eng_split_texts if len(ele)>=7 and len(ele)<17]
        for phone_num in eng_split_texts_clean:
            text = text.replace(phone_num,'')
        return text

    def replace_ids(self, text):
        """
        remove cellphone number from texts. If text contains cellphone No., the extract_time will report errors.
        hence, we remove it here.
        eg: extract_locations('我家住在陕西省安康市汉滨区，我的身份证号是150404198412011312。')


        :param: raw_text<string>
        :return: text_without_ids<string> eg: '我家住在陕西省安康市汉滨区，我的身份证号号是。'

        """
        if text == '':
            return []
        eng_texts = self.replace_chinese(text)
        sep = ',!?:; ：，.。！？《》、|\\/abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        eng_split_texts = [''.join(g) for k, g in groupby(eng_texts, sep.__contains__) if not k]
        eng_split_texts_clean = [ele for ele in eng_split_texts if len(ele) == 18]

        id_pattern = r'^[1-9][0-7]\d{4}((19\d{2}(0[13-9]|1[012])(0[1-9]|[12]\d|30))|(19\d{2}(0[13578]|1[02])31)|(19\d{2}02(0[1-9]|1\d|2[0-8]))|(19([13579][26]|[2468][048]|0[48])0229))\d{3}(\d|X|x)?$'
        ids = []
        for eng_text in eng_split_texts_clean:
            result = re.match(id_pattern, eng_text, flags=0)
            if result:
                ids.append(result.string)

        for phone_num in ids:
            text = text.replace(phone_num, '')
        return text

    def extract_time(self, text):
        """
        extract timestamp from texts
        eg: extract_time('我于2018年1月1日获得1000万美金奖励。')


        :param: raw_text<string>
        :return: time_info<time_dict> eg: {"type": "timestamp", "timestamp": "2018-11-27 11:00:00"}

        """
        if text == '':
            return []
        tmp_text = self.replace_cellphoneNum(text)
        tmp_text = self.replace_ids(tmp_text)
        tn = TimeNormalizer()
        res = tn.parse(target=tmp_text)  # target为待分析语句，timeBase为基准时间默认是当前时间
        return res


if __name__ == '__main__':
    sentence = '从北京到南京'
    sentence2 = '我于2018年1月1日'
    et = extractor()
    myLocation = et.extract_locations(sentence)
    myTime = et.extract_time(sentence2)
    print(myLocation)
    print(myTime)
