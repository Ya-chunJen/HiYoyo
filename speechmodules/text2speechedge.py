# 此语音方案，需要先把生成的语音文件保存为文件，然后在读取文件并播放。

import os,json,sys,configparser
import asyncio
import edge_tts
from pydub import AudioSegment
from pydub.playback import play
import random

workdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(workdir)

config = configparser.ConfigParser()
config.read(os.path.join(workdir, "config.ini"),encoding="UTF-8")

# https://github.com/rany2/edge-tts/blob/master/examples/streaming_with_subtitles.py

filename = str(random.randint(1000,9999)) + ".wav"
tepfile = os.path.join(workdir, "speechmodules","tepfile",filename)

class EdgeTTS:
    def __init__(self,Azure_Voice_Name="zh-CN-XiaoshuangNeural"): 
        self.Azure_Voice_Name = Azure_Voice_Name

    async def text2speech_and_play(self,text) -> None:
        # 如果嗓音文件为空的话，就不调用文本转语音模块，用于在纯文本的对话模式。
        if self.Azure_Voice_Name == "":
            return ""
        communicate = edge_tts.Communicate(text, self.Azure_Voice_Name)
        await communicate.save(tepfile)

        # 加载 MP3 文件
        audio = AudioSegment.from_file(tepfile, format='mp3')
        play(audio)

        # 删除临时文件
        # os.remove(tepfile)

if __name__ == '__main__':
    azuretts = EdgeTTS("zh-CN-XiaoxiaoNeural")
    loop = asyncio.get_event_loop_policy().get_event_loop()
    try:
        loop.run_until_complete(azuretts.text2speech_and_play("嗯，你好，我是你的智能小伙伴，我的名字叫Yoyo，你可以和我畅所欲言，我是很会聊天的哦！"))
    finally:
        loop.close()