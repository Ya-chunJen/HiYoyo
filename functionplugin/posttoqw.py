# Python 3.9
import json
import requests
import sys


headers = {'Content-Type': 'application/json'}

def posttoqw(function_args):
    webhook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=c6434bc3-7ef0-4afc-9c20-f1ee4f822407"
    text_content = function_args['text']
    payload_message = {"msgtype": "text","text": {"content": text_content}}
    response = requests.request("POST", webhook_url, headers=headers, data=json.dumps(payload_message))
    response = json.loads(response.text)
    if not(response['errcode']):
        callback_json = {"request_gpt_again":False,"details":f"已将消息推送到企业微信群。"}
        return callback_json
    else:
        callback_json = {"request_gpt_again":False,"details":f"推送消息是出错，请检查。"}
        return callback_json

if __name__ == '__main__':
    function_args = {"text":"你好"}
    posttoqw(function_args)