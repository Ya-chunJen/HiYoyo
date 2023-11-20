import json
import requests
import sys


headers = {'Content-Type': 'application/json'}

def plugindemo(function_args):
    # 模块名称和模块中的函数，名称必须一致，这里均为plugindemo。必须接受function_args这个字段作为参数。
    webhook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=c6434bc3-7ef0-4afc-9c20-f1ee4f822407"
    text_content = function_args['text']
    payload_message = {"msgtype": "text","text": {"content": text_content}}
    response = requests.request("POST", webhook_url, headers=headers, data=json.dumps(payload_message))
    response = json.loads(response.text)
    if not(response['errcode']):
        callback_json = {"request_gpt_again":False,"details":f"已将消息推送到企业微信群。"}
        return callback_json
    else:
        # 函数回调必须有request_gpt_again字段，用于判断是否需要继续调用gpt.details字段用于更加详细的信息。
        callback_json = {"request_gpt_again":False,"details":f"推送消息是出错，请检查。"}
        # 函数返回必须以字符串形式。
        return callback_json

if __name__ == '__main__':
    function_args = {"text":"你好"}
    plugindemo(function_args)