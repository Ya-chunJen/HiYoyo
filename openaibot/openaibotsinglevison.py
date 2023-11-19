import os,json,sys,configparser

workdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(workdir)

from speechmodules import text2speech


config = configparser.ConfigParser()
config.read(os.path.join(workdir, "config.ini"),encoding="UTF-8")
configsection = config['Openai']

import requests

class OpenaiBotSingleVison:
    def __init__(self):
        self.openai_api_url = configsection['openai_api_domain'] + "/v1/chat/completions"
        self.openai_api_key = configsection['openai_api_key']
        self.headers = {"Content-Type": "application/json","Authorization": "Bearer " + self.openai_api_key}
        self.model = "gpt-4-vision-preview"

    def chat_with_image(self,prompt_messages,voice_name="zh-CN-XiaoxiaoNeural"):
        tts = text2speech.AzureTTS("zh-CN-XiaoxiaoNeural")
        data = {
            "model": self.model,
            "messages": prompt_messages,
            "max_tokens": 300
        }
        response = requests.post(self.openai_api_url, headers=self.headers, data=json.dumps(data)) 
        print(response.text)
        print(response.json())
        result = response.json()['choices'][0]['message']
        tts.text2speech_and_play(result["content"])
        print(result["content"])
        return result

if __name__ == '__main__':
    system = "You are a helpful assistant"
    image_url  = input("请输入图片的URL：")
    prompt = input("请输入你针对图片的提问：")
    # image_url  = "https://upload.wikimedia.org/wikipedia/commons/7/73/China_IMG_3410_%2829112503573%29.jpg"
    # prompt = "这张图片包含了什么内容？"
    prompt_with_image = [
          {"type": "text","text": prompt},
          {"type": "image_url","image_url": image_url}
        ]
    messages=[{"role": "user", "content":prompt_with_image}]
    openaibotsinglevison = OpenaiBotSingleVison()
    post_message = openaibotsinglevison.chat_with_image(messages,"")["content"]
    print(post_message)