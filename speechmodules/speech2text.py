import azure.cognitiveservices.speech as speechsdk
import configparser
import os

config = configparser.ConfigParser()
config.read(os.path.join(os.getcwd(), "config.ini"),encoding="UTF-8")
audio_file_path = os.path.join(os.getcwd(), "speechfile/speech.wav")

class AzureASR:
    def __init__(self):
        self.AZURE_API_KEY = config['AzureSpeech']['AZURE_API_KEY']
        self.AZURE_REGION = config['AzureSpeech']['AZURE_REGION']
        self.speech_config = speechsdk.SpeechConfig(subscription=self.AZURE_API_KEY, region=self.AZURE_REGION)

    def speech2text(self, audio_path: str = audio_file_path, if_microphone: bool = True):
        self.speech_config.speech_recognition_language = "zh-CN"
        audio_config_recognizer = speechsdk.audio.AudioConfig(use_default_microphone=True)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config, audio_config=audio_config_recognizer)
        print("system:正在聆听...")
        speech_recognition_result = speech_recognizer.recognize_once_async().get()

        if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
            # print("You:{}".format(speech_recognition_result.text))
            return speech_recognition_result.text
        elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
            print("system:未侦测到语音,已退出监听。如需使用，请用唤醒词重新唤醒。")
            # print("system:未侦测到语音，详细信息 :{}".format(speech_recognition_result.no_match_details))
        elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_recognition_result.cancellation_details
            print("system:未侦测到语音,已退出监听。如需使用，请用唤醒词重新唤醒。")
            # print("system:未侦测到语音，详细信息:{}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details:{}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")
        # os.remove(audio_file_path)
        return None

if __name__ == "__main__":
    asr = AzureASR()
    result = asr.speech2text()
    print(result)