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
    aliyunossup_args = {"file_path":imagepath,"file_dir":"gpt4vison"}
    imageurl = aliyunossup.aliyunossup(aliyunossup_args)["details"]
    print("捕捉到的图像：" + imageurl)
    return imageurl

def videovison(function_args):
    prompt = function_args['text']
    imageurl = getimagepath()
    images_list = [imageurl]

    ai_image_response_content = opanaibotsinglevisonclass.chat_with_image(images_list,prompt)["content"]
    # print(ai_image_response_content)
    callback_json = {"request_gpt_again":True,"details":f"{ai_image_response_content}"}
    return callback_json

if __name__ == '__main__':
    function_args = {"text":"你看到了什么？"}
    videovison(function_args)