import os,json,sys,configparser
import openai

workdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(workdir)

from speechmodules import text2speech

config = configparser.ConfigParser()
config.read(os.path.join(workdir, "config.ini"),encoding="UTF-8")
configsection = config['Azureopenai']

def streamresult(completion):
    chunks_content = ""
    for chunk in completion:
        if chunk["choices"]:
            choices = chunk["choices"][0]
            delta = choices.get('delta', '')
            content = delta.get('content', '')
            chunks_content = chunks_content + content
            splitword_list = ["。", "！","？"]
            if any(splitword in content for splitword in splitword_list):
                print(chunks_content, end='', flush=True)  # 在纯文本对话模式下，可以将显示对话内容在终端中。
                yield chunks_content
                chunks_content = ""

class AzureBotSingle:
    def __init__(self):
        openai.api_type = "azure"
        openai.api_version = configsection['openai_api_version']
        openai.api_base = configsection['openai_api_base']
        openai.api_key = configsection['openai_api_key']
        self.gpt35_model = configsection['gpt35_deployment_name']

    def chat(self,prompt_messages,voice_name="zh-CN-XiaoxiaoNeural"):
        tts = text2speech.AzureTTS(voice_name)
        # if model is None:
        #     model = self.gpt35_model
        try:
            completion = openai.ChatCompletion.create(
                engine = self.gpt35_model,
                messages=prompt_messages,
                temperature=0.8,
                stream=True
                )
            stream_chunks = streamresult(completion)
            stream_content = ""
            while True:
                try:
                    stream_chunk = next(stream_chunks)
                    stream_content = stream_content + stream_chunk
                    #print(stream_content)
                except StopIteration:
                    break
                tts.text2speech_and_play(stream_chunk)
            return {"role": "assistant","content": stream_content}
            # response_message = completion.choices[0].message
            # print(response_message)
            # return response_message
        except openai.error.RateLimitError: # type: ignore
            response_message = {
                "role": "assistant",
                "content": "抱歉，服务器繁忙，请稍后重试!"
                }
            # print(response_message)
            return response_message

if __name__ == '__main__':
    system = "You are a helpful assistant"
    prompt = input("请输入你的问题：")
    messages=[{"role":"system","content": system},{"role": "user", "content":prompt}]
    azurebotsingle = AzureBotSingle()
    post_message = azurebotsingle.chat(messages)["content"]
    print(post_message)