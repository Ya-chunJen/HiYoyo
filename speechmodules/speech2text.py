# -*- coding: utf-8 -*-
"""Azure 语音转文字（ASR），支持中/英/日自动识别。"""
import azure.cognitiveservices.speech as speechsdk

from core import config


class AzureASR:
    def __init__(self):
        speech_cfg = config.azure_speech()
        self.speech_config = speechsdk.SpeechConfig(
            subscription=speech_cfg["api_key"], region=speech_cfg["region"])

    def speech2text(self) -> str:
        """从默认麦克风录音并识别为文字；未识别到内容时返回 None。"""
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        auto_detect = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
            languages=["zh-CN", "en-US", "ja-JP"])
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.speech_config,
            audio_config=audio_config,
            auto_detect_source_language_config=auto_detect,
        )
        print("system:正在聆听...")
        result = recognizer.recognize_once_async().get()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return result.text
        elif result.reason == speechsdk.ResultReason.NoMatch:
            print("system:未侦测到语音，已退出监听。如需使用，请用唤醒词重新唤醒。")
        elif result.reason == speechsdk.ResultReason.Canceled:
            details = result.cancellation_details
            print("system:未侦测到语音，已退出监听。如需使用，请用唤醒词重新唤醒。")
            if details.reason == speechsdk.CancellationReason.Error:
                print(f"system:错误详情：{details.error_details}")
                print("system:请检查 AzureSpeech 的 key 和 region 配置。")
        return None


if __name__ == "__main__":
    asr = AzureASR()
    print(asr.speech2text())
