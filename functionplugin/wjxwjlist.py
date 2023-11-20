import os
import smtplib
import json
import time
import hashlib
import configparser
import requests
import sys
workdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(workdir)

config = configparser.ConfigParser()
config.read(os.path.join(workdir, "config.ini"),encoding="UTF-8")
configsection = config['WJX']

appkey = configsection['appkey']
headers = {'Content-Type': 'application/json'}
url = "https://www.wjx.cn/openapi/default.aspx"

table = PrettyTable()
table.field_names = ["id", "标题", "答卷数"]

def calculateSign(params, appkey):
    # 1. 对参数名按ASCII码排序
    sorted_params = sorted(params.items())
    # print(sorted_params)
    # 2. 拼接所有参数名的值
    encoded_str = ""
    for key, value in sorted_params:
        if value:
            encoded_str +=  str(value)
    # print(encoded_str)
    # 3. 将appkey加上拼接字符串，得到加密原串
    
    encrypted_str =  encoded_str + appkey
    # 4. 进行SHA1加密
    sha1 = hashlib.sha1()
    sha1.update(encrypted_str.encode('utf8'))
    sign = sha1.hexdigest()
    # 5. 返回计算得到的签名
    return sign

def wjxwjlist(function_args):
    days = function_args["days"]
    params = {
        'appid' : configsection['appid'],
        'ts' : int(time.time()),
        'encode' : "sha1",
        'action' : "1000002",
        'creater' : "renyajun",
        'time_type' : 2,
        'sort' : 1,
        'begin_time' : int(time.time()*1000) - days*86400000,
        'end_time' :int(time.time()*1000)

    }
    sign = calculateSign(params, appkey)
    params['sign'] = sign
    response = requests.post(url, params=params, headers=headers)
    if json.loads(response.text)['result']:
        activitys_list_json = json.loads(response.text)['data']['activitys']
        for name, info in activitys_list_json.items():
            title = info["title"]
            answer_total = info["answer_total"]
            table.add_row([name, title, answer_total])
        
    print(table)
    table_str = str(table)
    callback_json = {"request_gpt_again":True,"details":table_str}
    return callback_json

if __name__ == '__main__':
    function_args = {"days":5}
    wjxwjlist(function_args)