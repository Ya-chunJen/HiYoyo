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
        tts = text2speech.AzureTTS(voice_name)
        data = {
            "model": self.model,
            "messages": prompt_messages,
            "max_tokens": 300
        }
        response = requests.post(self.openai_api_url, headers=self.headers, data=json.dumps(data)) 
        
        try:
            # 尝试获取 response 中的 'choices' 键值
            # print(response.text)
            result = response.json()['choices'][0]['message']
        except KeyError:
            # 如果 'choices' 键不存在，打印错误信息并返回默认值
            print("Error: 'choices' key not found in response.")
            result = {"role": "assistant","content":"图片解析错误。"}
        tts.text2speech_and_play(result["content"])
        # print(result["content"])
        return result

if __name__ == '__main__':
    system = "You are a helpful assistant"
    image_url  = input("请输入图片的URL：") or "https://upload.wikimedia.org/wikipedia/commons/7/73/China_IMG_3410_%2829112503573%29.jpg"
    prompt = input("请输入你针对图片的提问：") or "这张图片包含了什么内容？"
    prompt_with_image = [
          {"type": "text","text": prompt},
          {"type": "image_url","image_url": {"url":image_url,"detail": "low"}}
        ]
    messages=[{"role": "user", "content":prompt_with_image}]
    openaibotsinglevison = OpenaiBotSingleVison()
    post_message = openaibotsinglevison.chat_with_image(messages,"")["content"]
    print(post_message)