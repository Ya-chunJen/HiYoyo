import os
import sys
import azure.cognitiveservices.speech as speechsdk
import configparser
import os

config = configparser.ConfigParser()
config.read(os.path.join(os.getcwd(), "config.ini"),encoding="UTF-8")

class AzureTTS:
    def __init__(self,Azure_Voice_Name="zh-CN-XiaoshuangNeural"):       
        self.Azure_API_KEY = config['AzureSpeech']['AZURE_API_KEY']
        self.Azure_REGION = config['AzureSpeech']['AZURE_REGION']
        self.Azure_Voice_Name = Azure_Voice_Name
        self.speech_config = speechsdk.SpeechConfig(subscription = self.Azure_API_KEY, region = self.Azure_REGION)
        self.audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
        self.speech_config.speech_synthesis_voice_name = self.Azure_Voice_Name
        self.speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=self.audio_config)

    def text2speech_and_play(self,text):
        speech_synthesis_result = self.speech_synthesizer.speak_text_async(text).get()

        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            # print("Speech synthesized for text [{}]".format(text))
            print("system:已经播放完毕！")
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            print("Speech synthesis canceled:{}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print("Error details :{}".format(cancellation_details.error_details))
                    print("Didy you set the speech resource key and region values?")

if __name__ == '__main__':
    azuretts = AzureTTS()
    azuretts.text2speech_and_play("嗯，你好，我是你的智能小伙伴，我的名字叫Yoyo，你可以和我畅所欲言，我是很会聊天的哦！")