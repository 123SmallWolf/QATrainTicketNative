# !/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2019/11/20 1:38
# @Author  : LuYang
# @File    : sysLog.py
import yaml
import logging
import logging.config
import os

ResRoot = os.path.abspath(os.path.join(os.path.dirname(__file__), 'res'))
logging_file = os.path.abspath(os.path.join(ResRoot, 'logging.yaml'))


def setup_logging(default_level=logging.DEBUG):
    if logging_file is not None and os.path.exists(logging_file):
        with open(logging_file, 'r', encoding='utf-8') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
        logging.warning('%s 配置文件不存在', logging_file)


if __name__ == '__main__':
    setup_logging()
