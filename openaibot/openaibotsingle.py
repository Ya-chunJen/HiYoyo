# 通过URL请求OpanAI的接口。
import os,json,sys,configparser,requests
workdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(workdir)
from speechmodules import text2speech

# 读取openai的配置参数文件。
config = configparser.ConfigParser()
config.read(os.path.join(workdir, "config.ini"),encoding="UTF-8")
configsection = config['Openai']

class OpenaiBotSingle:
    def __init__(self,modelname = "gpt-3.5-turbo-1106"):
        # 从配置文件中，读取openai的api域名和key，并构造URL请求的头部。
        self.openai_api_url = configsection['openai_api_domain'] + "/v1/chat/completions"
        self.openai_api_key = configsection['openai_api_key']
        self.headers = {"Content-Type": "application/json","Authorization": "Bearer " + self.openai_api_key}
        self.model = modelname # 定义模型的名称，可能会随着时间而更新。

    def chat(self,prompt_messages,voice_name="zh-CN-XiaoxiaoNeural"):
        # 定义对话的函数，并初始化tts,如果初始化tts时，没有音色的配置，tts就不会生效。
        tts = text2speech.AzureTTS(voice_name)
        # 构造URL请求的数据部分。
        data = {
            "model": self.model,
            "messages": prompt_messages
        }
        
        try:
            # 发起api请求。
            ai_response = requests.post(self.openai_api_url, headers=self.headers, data=json.dumps(data))
            try:         
                # 使用try处理异常情况，因为api的请求返回的数据，可能会由于内容过滤等原因，返回
                ai_response_dict = ai_response.json()['choices'][0]['message']
            except Exception as e:
                # 如果返回的是异常数据，就打印一下返回的文本内容。并且构造一个相同字典结构的返回数据，以使程序正确运行。
                print(ai_response.text) 
                ai_response_dict = {"role": "assistant","content":"single模块：Ai返回数据异常，请依据打印内容进行检查。"}          
        except requests.exceptions.RequestException as e:
            print("请求发生异常：", e)
            ai_response_dict = {"role": "assistant","content":"single模块：Ai接口请求异常，请依据打印内容进行检查。"}
        
        # 获取ai返回的文本数据，使用tts播放出来，并且打印出来。
        ai_response_content = ai_response_dict["content"]
        print(ai_response_content) # 先打印结果
        tts.text2speech_and_play(ai_response_content)  # 再播放声音。
        return ai_response_dict # 函数返回的数据是字典类型的数据，而不是文本数据。

if __name__ == '__main__':
    system = input("请输入system的内容：") or "You are a helpful assistant"
    prompt = input("请输入你给ai的问题：") or "现在的日期是？"
    messages=[
        {"role":"system","content": system},
        {"role": "user", "content":prompt}
        ]
    openaibotsingle = OpenaiBotSingle()
    ai_response_content = openaibotsingle.chat(messages)["content"]
    # print(ai_response_content) # 函数中打印了结果，这里就不打印了。