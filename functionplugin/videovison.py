import os,json,sys,configparser
import cv2
from datetime import datetime

workdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(workdir)

from openaibot.openaibotsinglevison import OpenaiBotSingleVison
from functionplugin import aliyunossup

opanaibotsinglevisonclass = OpenaiBotSingleVison()

# 获取当前时间
now = datetime.now()

# 格式化为字符串
time_str = now.strftime("%Y-%m-%d-%H-%M-%S")

def getimagepath():
    # 打开默认摄像头，参数0表示设备编号，如果有多个摄像头，则可能需要选择不同的编号
    camera = cv2.VideoCapture(0)
    # 设置摄像头的分辨率
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    # 读取一帧图像
    success, frame = camera.read()
    # 如果读取成功，则保存图像到本地文件
    imagepath = f"{workdir}/openaibot/image/photo{time_str}.jpg"
    if success:
        cv2.imwrite(imagepath, frame)
    # 释放摄像头
    camera.release()
    imageurl = aliyunossup.upfile(imagepath,"gpt4vison")
    print(imageurl)
    return imageurl

def videovison(function_args):
    text_content = function_args['text']
    imageurl = getimagepath()
    prompt_with_image = [
          {"type": "text","text": text_content},
          {"type": "image_url","image_url": imageurl}
        ]
    messages=[{"role": "user", "content":prompt_with_image}]
    image_text_content = opanaibotsinglevisonclass.chat_with_image(messages,"zh-CN-XiaoxiaoNeural")["content"]
    print(text_content)
    return {"request_gpt_again":True,"details":f"{image_text_content}"}


if __name__ == '__main__':
    function_args = {"text":"这张照片里有什么内容？"}
    videovison(function_args)