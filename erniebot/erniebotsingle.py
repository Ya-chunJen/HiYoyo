import os
import requests
import json
import openai
import sys
import configparser
from . import text2speech
# import text2speech

config = configparser.ConfigParser()
config.read(os.path.join(os.getcwd(), "config.ini"),encoding="UTF-8")
configsection = config['baiduernie']

def get_access_token():
    """
    使用 API Key，Secret Key 获取access_token，替换下列示例中的应用API Key、应用Secret Key
    """
    ApiKey = configsection['ApiKey']
    keySecret = configsection['keySecret']
    url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={ApiKey}&client_secret={keySecret}"
    
    payload = json.dumps("")
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get("access_token")

class ErnieBotSingle:
    def __init__(self):
        self.requesturl = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token=" + get_access_token()
        self.headers = {'Content-Type': 'application/json'}

    def chat(self,prompt_messages,voice_name="zh-CN-XiaoxiaoNeural"):
        tts = text2speech.AzureTTS(voice_name)
        # 组装请求的参数和数据
        system = prompt_messages[0]["content"] # 文心一言的system不再messages中。需要从messages中获取。
        prompt_messages.pop(0)  # 文心一言的system不再messages中。需要从messages中删除。
        if len(prompt_messages) % 2 == 0:
            # 文心一言的messages长度必须为奇数
            prompt_messages.pop(0)
        payload = json.dumps({
            "system":system,
            "messages": prompt_messages,
            "stream": True
        })
        # 以下是发送请求的过程
        response = requests.request("POST", self.requesturl, headers=self.headers, data=payload)
        # 以下是处理请求结果的过程
        # print(response.text)
        responseresult = ""
        for line in response.iter_lines():
            linetext = line.decode(encoding='utf-8')
            if len(linetext) == 0:
                continue
            linetext = linetext.replace("data: ","")
            try:
                linejson = json.loads(linetext)
                lineresult = linejson['result']
                print(lineresult, end='')
                tts.text2speech_and_play(lineresult)
                responseresult = responseresult + lineresult
            except:
                responseresult = "服务请求异常！"
                print(responseresult)
                tts.text2speech_and_play(responseresult)
        return {"role": "assistant","content": responseresult}

if __name__ == '__main__':
    system = "You are a helpful assistant"
    prompt = input("请输入你的问题：")
    messages=[{"role":"system","content": system},{"role": "user", "content":prompt}]
    erniebotsingle = ErnieBotSingle()
    post_message = erniebotsingle.chat(messages)["content"]
    print(post_message)