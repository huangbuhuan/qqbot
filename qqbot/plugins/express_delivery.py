# -*- coding: utf-8 -*-

import requests
import schedule
import time
from datetime import datetime
import threading

def startJob():
    while True:
        schedule.run_pending()
        time.sleep(1)

t = threading.Thread(target=startJob, name='LoopThread')
t.start()

url = 'http://api.shujuzhihui.cn/api/sjzhApi/searchExpress'
header = {'Content-Type': 'application/json'}

appKey = 'f57ee88ba80e422982b6ed88dac447a8'

msg_container = {}

def search_express(bot, contact, content):
    strs = content.split(' ')
    if len(strs) == 2:
        print(strs[1])
    else:
        bot.SendTo(contact, '快递查询格式错误输入错误, 请输入: [快递 xxxxx]')
        return
    expressNo = content.split(' ')[1]
    data = {}
    try:
        response = requests.post(url = url, data = {
            'appKey': appKey,
            'expressNo': expressNo
        })
        data = response.json()
        return data
    except Exception as e:
        print(e)    
    finally:
        return data

def handler(bot, contact, content):
    data = search_express(bot, contact, content)
    if data['ERRORCODE'] != '0':
        bot.SendTo(contact, '没有查询到相关数据')

    else:
        result = data['RESULT']
        result['context'].sort(key = lambda x : datetime.strptime(x['time'],'%Y-%m-%d %H:%M:%S'), reverse = False)
        express_no = content.split(' ')[1]
        if express_no in msg_container:
            msg = msg_container[express_no]
            if len(msg) < len(result['context']):
                msg_container[express_no] = result['context']
                bot.SendTo(contact, result['context'][-1])
        else:
            msg_container[express_no] = result['context']
            for msg in result['context']:
                bot.SendTo(contact, '时间 ' + msg['time'] + ' ' + msg['desc'])

def onQQMessage(bot, contact, member, content):
    if '快递' in content:
        data = search_express(bot, contact, content)

        if data['ERRORCODE'] != '0':
            bot.SendTo(contact, '没有查询到相关数据')
        else:
            result = data['RESULT']
            bot.SendTo(contact, '快递名 ' + result['com'])

            # 按时间排序
            result['context'].sort(key = lambda x : datetime.strptime(x['time'],'%Y-%m-%d %H:%M:%S'), reverse = False)
            for msg in result['context']:
                bot.SendTo(contact, '时间 ' + msg['time'] + ' ' + msg['desc'])

    elif content == '黄步欢':
        bot.SendTo(contact, '是猪')
    elif '监控' in content:
        schedule.every(10).minutes.do(handler(bot, contact, content))
    else:
        bot.SendTo(contact, '是猪')

