import datetime,time
import os,json,sys,configparser,requests

workdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(workdir)

config = configparser.ConfigParser()
config.read(os.path.join(workdir, "config.ini"),encoding="UTF-8")
configsection = config['Openai']

from functionplugin import aliyunossup
from functionplugin import posttoqw

class OpenaiBotImage:
    def __init__(self):
        self.openai_api_url = configsection['openai_api_domain'] + "/v1/images/generations"
        self.openai_api_key = configsection['openai_api_key']
        self.headers = {"Content-Type": "application/json","Authorization": "Bearer " + self.openai_api_key}
        self.model = "dall-e-3"

    def create_image(self,prompt_messages):
        size_list  = ['256x256', '512x512', '1024x1024', '1024x1792', '1792x1024']
        data = {
            "model": self.model,
            "prompt": prompt_messages,
            "n": 1,
            "size": "1024x1024"
        }
        ai_image_response = requests.post(self.openai_api_url, headers=self.headers, data=json.dumps(data)) 

        # print(ai_image_response.json())
        ai_image_url = ai_image_response.json()['data'][0]['url'] # 限制只返回一张图片

        # 请求图片url下载保存到本地
        image_data = requests.get(ai_image_url)
        if image_data.status_code == 200:
            current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            image_path = os.path.join(workdir, f'openaibot/image/aicreate/{current_time}.png')
            with open(image_path, "wb") as f:
                f.write(image_data.content)
            # 再上传到阿里云OSS上
            aliyunossup_function_args = {"local_file_path":image_path,"oss_file_dir":"images/aicreate"}
            oss_image_url = aliyunossup.aliyunossup(aliyunossup_function_args)["details"]
            posttoqw_function_args = {"text":oss_image_url}
            posttoqw.posttoqw(posttoqw_function_args)
            return oss_image_url
        else:
            print("图片下载失败。")
            return None
        
if __name__ == '__main__':
    if len(sys.argv) > 1:
        prompt = sys.argv[1]
    else:
        prompt = input("请输入你的问题：") or "玩具酒桶"
        
    openaibotimage = OpenaiBotImage()
    post_message = openaibotimage.create_image(prompt)
    print(post_message)