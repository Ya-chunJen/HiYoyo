import os,json,sys,configparser

workdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(workdir)

from speechmodules import text2speech

config = configparser.ConfigParser()
config.read(os.path.join(workdir, "config.ini"),encoding="UTF-8")
configsection = config['Openai']

import requests

class OpenaiBotSingle:
    def __init__(self):
        self.openai_api_url = configsection['openai_api_domain'] + "/v1/chat/completions"
        self.openai_api_key = configsection['openai_api_key']
        self.headers = {"Content-Type": "application/json","Authorization": "Bearer " + self.openai_api_key}
        self.model = "gpt-3.5-turbo"

    def chat(self,prompt_messages,voice_name="zh-CN-XiaoxiaoNeural"):
        tts = text2speech.AzureTTS(voice_name)
        data = {
            "model": self.model,
            "messages": prompt_messages
        }
        response = requests.post(self.openai_api_url, headers=self.headers, data=json.dumps(data))
        try:
            # print(response.json())
            result = response.json()['choices'][0]['message']
        except KeyError:
            print(response.text)
            result = {"role": "assistant","content":"Ai接口返回异常。"}
        tts.text2speech_and_play(result["content"])
        print(result["content"])
        return result

if __name__ == '__main__':
    system = "You are a helpful assistant"
    prompt = input("请输入你的问题：")
    messages=[{"role":"system","content": system},{"role": "user", "content":prompt}]
    openaibotsingle = OpenaiBotSingle()
    post_message = openaibotsingle.chat(messages)["content"]
    print(post_message)