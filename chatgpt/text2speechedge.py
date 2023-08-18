#!/usr/bin/env python3

import asyncio
import edge_tts
from pydub import AudioSegment
from pydub.playback import play
import io


class EdgeTTS:
    def __init__(self,Azure_Voice_Name="zh-CN-XiaoxiaoNeural"):
        self.Azure_Voice_Name = Azure_Voice_Name
     
    async def text2speech_and_play(self,text):
        communicate = edge_tts.Communicate(text, self.Azure_Voice_Name)
        
        async for chunk in communicate.stream():
            if chunk["type"] == "WordBoundary":
                print(chunk["type"])
                audio_content = b''
            elif chunk["type"] == "audio":
                audio_content = audio_content + chunk["data"]    
                print(chunk["type"])
                #print(f"WordBoundary: {chunk}")
            audio_stream = io.BytesIO(audio_content)
            audio_segment = AudioSegment.from_file(audio_stream)
            play(audio_segment)

if __name__ == "__main__":
    text = input("请输入要转语音的文字内容：")
    tts = EdgeTTS()
    loop = asyncio.get_event_loop_policy().get_event_loop()
    try:
        loop.run_until_complete(tts.text2speech_and_play(text))
    finally:
        loop.close()