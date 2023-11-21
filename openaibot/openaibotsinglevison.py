# 通过URL请求GPT4的多模态接口，即视觉识别接口。
import os,json,sys,configparser,requests
workdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(workdir)
from speechmodules import text2speech

# 读取openai的配置参数文件。
config = configparser.ConfigParser()
config.read(os.path.join(workdir, "config.ini"),encoding="UTF-8")
configsection = config['Openai']

import base64

# 定义一个函数，可以将本地图片进行base64编码。
def encode_image_base64(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

class OpenaiBotSingleVison:
    def __init__(self):
        # 从配置文件中，读取openai的api域名和key，并构造URL请求的头部。
        self.openai_api_url = configsection['openai_api_domain'] + "/v1/chat/completions"
        self.openai_api_key = configsection['openai_api_key']
        self.headers = {"Content-Type": "application/json","Authorization": "Bearer " + self.openai_api_key}
        self.model = "gpt-4-vision-preview" # 定义模型的名称，可能会随着时间而更新。

    def chat_with_image(self,images_list:list,prompt:str="这张图片包含了什么内容？"):
        # 构造请求的message
        messages_content = [{"type": "text","text": prompt}]
        messages = [{"role": "user", "content":messages_content}]

        for image_item in images_list:
            # 循环图片列表中的图片。
            if image_item.startswith("http") or image_item.startswith("https"):
                # 判断是不是url图片，如果是url图片的话，直接加到message中。
                messages_content_image = {"type": "image_url","image_url": {"url":image_item,"detail": "low"}}
            else:
                # 如果是本地图片的话，要调用函数，转为base64图片。
                image_item_base64 = encode_image_base64(image_item)
                messages_content_image = {"type": "image_url","image_url": {"url":f"data:image/jpeg;base64,{image_item_base64}","detail": "low"}}
            messages_content.append(messages_content_image)

        # 构造URL请求的数据部分。
        print(messages)
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 500 # 需要搞清楚这个参数的含义。
        }

        try:
            # 发起api请求
            ai_image_response = requests.post(self.openai_api_url, headers=self.headers, data=json.dumps(data)) 
            try:
                # 使用try处理异常情况，因为api的请求返回的数据，可能会由于内容过滤等原因，返回
                ai_image_response_dict = ai_image_response.json()['choices'][0]['message']
            except Exception as e:
                # 如果返回的是异常数据，就打印一下返回的文本内容。并且构造一个相同字典结构的返回数据，以使程序正确运行。
                print(ai_image_response.text) 
                ai_image_response_dict = {"role": "assistant","content":"singlevison模块：Ai返回数据异常，图片解析错误。"}
        except requests.exceptions.RequestException as e:
            print("请求发生异常：", e)
            ai_image_response_dict = {"role": "assistant","content":"singlevison模块：Ai接口请求异常，请依据打印内容进行检查。"}

        # 获取ai返回的文本数据，使用tts播放出来，并且打印出来。
        ai_image_response_content = ai_image_response_dict["content"]
        print(ai_image_response_content) # 先打印结果

        return ai_image_response_dict # 函数返回的数据是字典类型的数据，而不是文本数据。

if __name__ == '__main__':
    image_url_1  = input("请输入图片1的URL：") or "https://helpimage.paperol.cn/20231121160216.png"
    image_url_2  = input("请输入图片2的URL：") or "https://helpimage.paperol.cn/20231121160216.png"
    prompt = input("请输入你针对图片的提问：") or "这张图片内包含了什么内容？"
    images_list = [image_url_1,image_url_2]
    openaibotsinglevison = OpenaiBotSingleVison()
    ai_image_response_content = openaibotsinglevison.chat_with_image(images_list,prompt)["content"]
    # print(ai_image_response_content) # 函数中打印了结果，这里就不打印了。