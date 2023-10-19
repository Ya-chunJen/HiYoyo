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

# def streamresult(completion):
#     chunks_content = ""
#     for chunk in completion:
#         if chunk["choices"]:
#             choices = chunk["choices"][0]
#             delta = choices.get('delta', '')
#             content = delta.get('content', '')
#             chunks_content = chunks_content + content
#             splitword_list = ["。", "！","？"]
#             if any(splitword in content for splitword in splitword_list):
#                 print(chunks_content, end='', flush=True)  # 在纯文本对话模式下，可以将显示对话内容在终端中。
#                 yield chunks_content
#                 chunks_content = ""

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
            "messages": prompt_messages
        })
        # 以下是发送请求的过程
        response = requests.request("POST", self.requesturl, headers=self.headers, data=payload)
        # 以下是处理请求结果的过程
        # print(response.text)
        response_json = json.loads(response.text)
        if "result" in response_json:
            responseresult = response_json["result"]          
        else:
            responseresult = f'服务出错，错误码：{response_json["error_code"]}'
        print(responseresult)
        tts.text2speech_and_play(responseresult)
        return {"role": "assistant","content": responseresult}

        # try:
        #     completion = openai.ChatCompletion.create(
        #         engine = self.gpt35_model,
        #         messages=prompt_messages,
        #         temperature=0.8,
        #         stream=True
        #         )
        #     stream_chunks = streamresult(completion)
        #     stream_content = ""
        #     while True:
        #         try:
        #             stream_chunk = next(stream_chunks)
        #             stream_content = stream_content + stream_chunk
        #             #print(stream_content)
        #         except StopIteration:
        #             break
        #         tts.text2speech_and_play(stream_chunk)
        #     return {"role": "assistant","content": stream_content}
        #     # response_message = completion.choices[0].message
        #     # print(response_message)
        #     # return response_message
        # except openai.error.RateLimitError:
        #     response_message = {
        #         "role": "assistant",
        #         "content": "抱歉，服务器繁忙，请稍后重试!"
        #         }
        #     # print(response_message)
        #     return response_message

if __name__ == '__main__':
    system = "You are a helpful assistant"
    prompt = input("请输入你的问题：")
    messages=[{"role":"system","content": system},{"role": "user", "content":prompt}]
    erniebotsingle = ErnieBotSingle()
    post_message = erniebotsingle.chat(messages)["content"]
    print(post_message)