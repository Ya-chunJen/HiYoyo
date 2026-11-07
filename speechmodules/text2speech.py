# -*- coding: utf-8 -*-
"""Azure 文字转语音。一般不直接使用，请优先使用 core/tts.py 的统一 TTS 入口。"""
import azure.cognitiveservices.speech as speechsdk

from core import config


class AzureTTS:
    def __init__(self, voice_name: str = "zh-CN-XiaoshuangNeural"):
        speech_cfg = config.azure_speech()
        self.voice_name = voice_name
        self.speech_config = speechsdk.SpeechConfig(
            subscription=speech_cfg["api_key"], region=speech_cfg["region"])
        self.audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
        self.speech_config.speech_synthesis_voice_name = self.voice_name
        self.speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config, audio_config=self.audio_config)

    def speak(self, text: str):
        """合成并播放文本（阻塞直到播放完毕）。"""
        if not text or not text.strip():
            return
        result = self.speech_synthesizer.speak_text_async(text).get()
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("system:已经播放完毕！")
        elif result.reason == speechsdk.ResultReason.Canceled:
            details = result.cancellation_details
            print(f"system:语音合成被取消：{details.reason}")
            if details.reason == speechsdk.CancellationReason.Error and details.error_details:
                print(f"system:错误详情：{details.error_details}")

    # 兼容旧版方法名
    def text2speech_and_play(self, text: str):
        self.speak(text)


if __name__ == '__main__':
    azuretts = AzureTTS("zh-CN-YunzeNeural")
    azuretts.speak("嗯，你好，我是你的智能小伙伴，我的名字叫Yoyo，你可以和我畅所欲言，我是很会聊天的哦！")
