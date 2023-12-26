import os,json,sys,configparser
import requests
import google.generativeai as genai
import pathlib
import textwrap

workdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(workdir)

from speechmodules import text2speech

config = configparser.ConfigParser()
config.read(os.path.join(workdir, "config.ini"),encoding="UTF-8")
configsection = config['google']
google_api_key = configsection["key"]

genai.configure(api_key=google_api_key)

def modlelist():
    # 罗列当前支持的模型名称。
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)

class GoogleBotSingle:
    def __init__(self):
        pass

    def chat(self,prompt_messages,voice_name="zh-CN-XiaoxiaoNeural"):
        tts = text2speech.AzureTTS(voice_name)
        model = genai.GenerativeModel('gemini-pro')
        message = prompt_messages[-1]["content"]
        response = model.generate_content(message)
        print(response.text)
        return response.text

if __name__ == '__main__':
    modlelist()
    system = "You are a helpful assistant"
    prompt = input("请输入你的问题：")
    messages=[{"role":"system","content": system},{"role": "user", "content":prompt}]
    googlebotsingleclass = GoogleBotSingle()
    post_message = googlebotsingleclass.chat(messages)
    print(post_message)