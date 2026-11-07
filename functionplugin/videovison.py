# -*- coding: utf-8 -*-
"""videovison 插件：调用摄像头拍一张照片，让多模态模型「看到」外部世界。

需要在 config.ini 的 [LLM] vision_model 中配置一个支持图片输入的模型，
例如 gpt-4o-mini / qwen-vl-plus / glm-4v-flash 等。
"""
import os
import cv2
from datetime import datetime

workdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# 摄像头照片的临时保存目录
VISION_DIR = os.path.join(workdir, "log", "vision")


def getimagepath() -> str:
    """打开默认摄像头，抓拍一帧并保存为 jpg。"""
    os.makedirs(VISION_DIR, exist_ok=True)
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    success, frame = camera.read()
    camera.release()
    if not success:
        raise RuntimeError("摄像头抓拍失败，请检查摄像头设备。")
    time_str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    imagepath = os.path.join(VISION_DIR, f"photo{time_str}.jpg")
    cv2.imwrite(imagepath, frame)
    print("system:已抓拍照片：" + imagepath)
    return imagepath


def videovison(function_args):
    from core.llm import LLMClient

    prompt = function_args.get("text", "这张图片包含了什么内容？")
    imagepath = getimagepath()
    llm = LLMClient()
    answer = llm.chat_with_image([imagepath], prompt)
    return {"request_gpt_again": True, "details": answer}


if __name__ == '__main__':
    print(videovison({"text": "你看到了什么？"}))
