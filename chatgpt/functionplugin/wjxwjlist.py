import os
import smtplib
import json
import time
import hashlib
import configparser
import requests

config = configparser.ConfigParser()
config.read(os.path.join(os.getcwd(), "config.ini"),encoding="UTF-8")
configsection = config['WJX']

appkey = configsection['appkey']
headers = {'Content-Type': 'application/json'}
url = "https://www.wjx.cn/openapi/default.aspx"

def calculateSign(params, appkey):
    # 1. 对参数名按ASCII码排序
    sorted_params = sorted(params.items())
    # 2. 拼接所有参数名的值
    encoded_str = ""
    for key, value in sorted_params:
        if value:
            encoded_str += key + str(value)
    # 3. 将appkey加上拼接字符串，得到加密原串
    encrypted_str = appkey + encoded_str
    # 4. 进行SHA1加密
    sha1 = hashlib.sha1()
    sha1.update(encrypted_str.encode('utf8'))
    sign = sha1.hexdigest()
    # 5. 返回计算得到的签名
    return sign

def wjxwjlist(function_args):
    params = {
        'appid' : configsection['appid'],
        'ts' : int(time.time()),
        'encode' : "sha1",
        'action' : "1000002",
        'creater' : "renyajun"
    }
    sign = calculateSign(params, appkey)
    params['sign'] = sign
    response = requests.post(url, params=params, headers=headers)
    print(response.text)
    callback_json = {"request_gpt_again":True,"details":response.text}
    return json.dumps(callback_json)

if __name__ == '__main__':
    function_args = ""
    wjxwjlist(function_args)