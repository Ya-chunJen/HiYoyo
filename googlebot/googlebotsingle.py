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
GOOGLE_API_KEY = configsection["key"]

# Used to securely store your API key
# from google.colab import userdata

from IPython.display import display
from IPython.display import Markdown

def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

genai.configure(api_key=GOOGLE_API_KEY)

def modlelist():
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)

modlelist()

class GoogleBotSingle:
    def __init__(self):
        pass

    def chat(self,prompt_messages,voice_name="zh-CN-XiaoxiaoNeural"):
        tts = text2speech.AzureTTS(voice_name)
        model = genai.GenerativeModel('gemini-pro')
        message = prompt_messages[-1]["content"]
        response = model.generate_content(message)
        print()
        print(response.text)
        return to_markdown(response.text)

if __name__ == '__main__':
    system = "You are a helpful assistant"
    prompt = input("请输入你的问题：")
    messages=[{"role":"system","content": system},{"role": "user", "content":prompt}]
    googlebotsingleclass = GoogleBotSingle()
    post_message = googlebotsingleclass.chat(messages)
    print(post_message)