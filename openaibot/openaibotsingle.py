import os,json,sys,configparser

workdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(workdir)

config = configparser.ConfigParser()
config.read(os.path.join(workdir, "config.ini"),encoding="UTF-8")
configsection = config['Openai']
OPENAI_API_KEY = configsection['openai_api_key']
OPENAI_API_URL = configsection['openai_api_url']

import requests

# API 访问地址
url = OPENAI_API_URL + "/v1/chat/completions"

# 请求头部信息
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer "+OPENAI_API_KEY
}

# 请求体数据
data = {
    "model": "gpt-3.5-turbo",
    "messages": [
        {
            "role": "system",
            "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
        },
        {
            "role": "user",
            "content": "Compose a poem that explains the concept of recursion in programming."
        }
    ]
}

# 发送请求
response = requests.post(url, headers=headers, data=json.dumps(data))

# 获取响应数据
result = response.json()

# 打印响应数据
print(result)