import os,json,sys,configparser

workdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(workdir)

config = configparser.ConfigParser()
config.read(os.path.join(workdir, "config.ini"),encoding="UTF-8")
configsection = config['Openai']

import requests

class OpenaiBotImage:
    def __init__(self):
        self.openai_api_url = "https://api.openai.com/v1/images/generations"
        self.openai_api_key = configsection['openai_api_key']
        self.headers = {"Content-Type": "application/json","Authorization": "Bearer " + self.openai_api_key}
        self.model = "dall-e-3"

    def create(self,prompt_messages):
        data = {
            "model": self.model,
            "prompt": prompt_messages,
            "n": 1,
            "size": "1024x1024"
        }
        response = requests.post(self.openai_api_url, headers=self.headers, data=json.dumps(data)) 

        print(response.json())
        result = response.json()['data'][0]['url']
        return result

if __name__ == '__main__':
    prompt = input("请输入你的问题：")
    openaibotimage = OpenaiBotImage()
    post_message = openaibotimage.create(prompt)
    print(post_message)