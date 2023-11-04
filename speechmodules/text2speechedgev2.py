# 此方案，不需要讲生成的语音保存为文件，而是可以直接讲音频字节流，进行播放，但是每段音频开头都有一个爆破音
import os,json,sys,configparser
import asyncio
import edge_tts
import pyaudio
from pydub import AudioSegment
from io import BytesIO


workdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(workdir)

config = configparser.ConfigParser()
config.read(os.path.join(workdir, "config.ini"),encoding="UTF-8")

# https://github.com/rany2/edge-tts/blob/master/examples/streaming_with_subtitles.py

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

def byte2file(data_byte):
    # data_str = data_byte.decode('utf-8')
    with open('audio_data_wav.bin', 'wb') as f:
        f.write(data_byte)

def mp3towav(mp3_data):
    with BytesIO(mp3_data) as buffer:
        # 1、加载 MP3 格式的音频数据（data 为 MP3 格式的字节流）
        audio = AudioSegment.from_file(buffer, format='mp3')
        # 2. 使用 AudioSegment 对象的 export() 函数将音频数据转换为 WAV 格式的字节流。
        wav_data = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2).export(format='wav').read()
    return wav_data

class EdgeTTS:
    def __init__(self,Azure_Voice_Name="zh-CN-XiaoshuangNeural"): 
        self.Azure_Voice_Name = Azure_Voice_Name

    async def text2speech_and_play(self,text) -> None:
        # 如果嗓音文件为空的话，就不调用文本转语音模块，用于在纯文本的对话模式。
        if self.Azure_Voice_Name == "":
            return ""
        
        communicate = edge_tts.Communicate(text, self.Azure_Voice_Name)
        audio_data = b"" 

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data = audio_data + chunk["data"]
            elif chunk["type"] == "WordBoundary":
                pass
        # print(audio_data)
        audio_data_wav = mp3towav(audio_data)
        byte2file(audio_data_wav)
        # print(audio_data_wav)
        # 初始化 PyAudio
        p = pyaudio.PyAudio()
        # 打开音频流并开始播放
        stream=p.open(format=FORMAT,
                      channels=CHANNELS,
                      rate=RATE,
                      output=True)
        stream.write(audio_data_wav)
        stream.start_stream()
        stream.close()
        p.terminate()
    

if __name__ == '__main__':
    azuretts = EdgeTTS("zh-CN-XiaoxiaoNeural")
    loop = asyncio.get_event_loop_policy().get_event_loop()
    try:
        loop.run_until_complete(azuretts.text2speech_and_play("你好"))
    finally:
        loop.close()
    
    