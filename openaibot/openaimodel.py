# 罗列目前这个openai账号支持的model列表。

import os,json,sys,configparser

workdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(workdir)

import requests

config = configparser.ConfigParser()
config.read(os.path.join(workdir, "config.ini"),encoding="UTF-8")
configsection = config['Openai']

openai_api_url = "https://api.openai.com/v1/models"
openai_api_key = configsection['openai_api_key']

headers = {"Content-Type": "application/json","Authorization": "Bearer " + openai_api_key}

response = requests.get(openai_api_url, headers=headers) 

model_list = response.json()["data"]

for model_dict in model_list:
    model_id = model_dict["id"]
    print(model_id)
