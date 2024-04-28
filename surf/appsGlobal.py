# -*- coding: utf-8 -*-
"""
Created By      : ZedFeorius(fuzequan)
Created Time    : 2024/3/26 17:27
File Name       : appsGloble.py
Last Edit Time  : 
"""
import logging
import os
from logging.handlers import TimedRotatingFileHandler


def getPlatformPath():
    cur_path = os.path.dirname(os.path.abspath(__file__))  # 当前文件路径
    cur_path_list = cur_path.split(os.sep)  # 按文件夹炸开
    platform_path = os.sep.join(cur_path_list[0:4]) if os.sep.join(cur_path_list[0:4])!= cur_path else os.sep.join(cur_path_list[0:3]) # 取前俩文件夹
    return platform_path


def getAppName():
    curr = os.path.dirname(os.path.abspath(__file__))
    app_name = curr.split("/")[-1] if curr.split("/")[-1] != curr else curr.split("\\")[-1]
    return app_name


APPNAME = getAppName()
PLATFROMPATH = getPlatformPath()
APPHOME = os.path.join(PLATFROMPATH, APPNAME)


def get_logger(logfile=APPNAME):
    """获取日志句柄的方法"""
    logger = logging.getLogger(logfile)
    logger.setLevel(logging.DEBUG)
    logroot = os.path.join(APPHOME, 'logs')

    if not os.path.exists(logroot):
        os.mkdir(logroot)
    filehandle = TimedRotatingFileHandler(os.path.normpath(logroot + "/" + \
                                                              logfile + ".log"), 'midnight')
    filehandle.suffix = "%Y-%m-%d"
    filehandle.setLevel(logging.DEBUG)
    consolehandle = logging.StreamHandler()
    consolehandle.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    filehandle.setFormatter(formatter)
    consolehandle.setFormatter(formatter)
    logger.addHandler(filehandle)
    logger.addHandler(consolehandle)
    return logger


logger = get_logger()

CHAT_TEMP = {
    "_id": "",
    "_index": "chat_message",
    "_source": {
        "chat_id": "",
        "type": "",
        "content": "",
        "user_id": "",
        "chat_time": ""
    }
}
