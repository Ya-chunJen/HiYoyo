# -*- coding: utf-8 -*-
"""文字转语音（TTS）统一模块。

支持两种引擎，通过 voice 参数的前缀选择：
  - "azure:zh-CN-XiaoxiaoNeural"  使用 Azure 语音服务（需要 [AzureSpeech] 配置）
  - "edge:zh-CN-XiaoxiaoNeural"   使用免费的 Edge-TTS（无需任何 key）
  - 不带前缀                       自动选择：配置了 Azure key 用 Azure，否则用 Edge
  - 空字符串                       不发声（纯文本模式）
"""
import os
import asyncio
import tempfile
import platform
import subprocess
import threading

from core import config


class NullTTS:
    """静音实现，用于纯文本对话模式。"""

    def speak(self, text: str):
        pass


class EdgeTTS:
    """基于 edge-tts 的免费语音合成，生成 mp3 后调用系统播放器播放。"""

    def __init__(self, voice: str = "zh-CN-XiaoxiaoNeural"):
        self.voice = voice

    def speak(self, text: str):
        if not text or not text.strip():
            return
        import edge_tts

        fd, path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
        try:
            communicate = edge_tts.Communicate(text, self.voice)
            asyncio.run(communicate.save(path))
            _play_audio_file(path)
        finally:
            if os.path.exists(path):
                os.remove(path)


def _play_audio_file(path: str):
    """跨平台播放一个音频文件（阻塞直到播放完毕）。"""
    sysname = platform.system()
    if sysname == "Darwin":
        subprocess.run(["afplay", path], check=False)
    elif sysname == "Windows":
        try:
            from playsound import playsound

            playsound(path)
        except Exception as e:
            print(f"system:音频播放失败 {e}")
    else:
        # Linux：优先 playsound，失败则尝试 ffplay
        try:
            from playsound import playsound

            playsound(path)
        except Exception:
            subprocess.run(
                ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", path],
                check=False,
            )


class AzureTTSLazy:
    """懒加载的 Azure TTS 包装（首次发声时才初始化 SDK，加快启动）。"""

    def __init__(self, voice_name: str):
        self.voice_name = voice_name
        self._impl = None
        self._lock = threading.Lock()

    def _get_impl(self):
        if self._impl is None:
            with self._lock:
                if self._impl is None:
                    from speechmodules.text2speech import AzureTTS

                    self._impl = AzureTTS(self.voice_name)
        return self._impl

    def speak(self, text: str):
        self._get_impl().speak(text)


class TTS:
    """统一 TTS 入口。"""

    def __init__(self, voice: str = ""):
        voice = (voice or "").strip()
        if not voice:
            self._impl = NullTTS()
            return

        engine = None
        if ":" in voice:
            prefix, name = voice.split(":", 1)
            if prefix.lower() in ("azure", "edge"):
                engine = prefix.lower()
                voice = name

        azure_key = config.azure_speech()["api_key"]
        if engine == "azure" or (engine is None and azure_key):
            self._impl = AzureTTSLazy(voice)
        else:
            self._impl = EdgeTTS(voice or "zh-CN-XiaoxiaoNeural")

    def speak(self, text: str):
        try:
            self._impl.speak(text)
        except Exception as e:
            print(f"system:TTS播放异常：{e}")


class SentenceSpeaker:
    """流式输出时的分句播报器。

    feed() 接收 LLM 的增量文本：边打印边积累，遇到句末标点就把
    一整句放进队列，由后台线程依次朗读，避免阻塞流式接收。
    finish() 会把最后不足一句的残余文本播完并等待队列清空。
    """

    _END_PUNCT = "。！？!?；;\n"

    def __init__(self, tts: TTS):
        self.tts = tts
        self._buffer = ""
        self._queue = []
        self._lock = threading.Lock()
        self._done = threading.Event()
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def _worker(self):
        while True:
            sentence = None
            with self._lock:
                if self._queue:
                    sentence = self._queue.pop(0)
            if sentence is None:
                if self._done.is_set():
                    return
                threading.Event().wait(0.05)
                continue
            self.tts.speak(sentence)

    def feed(self, delta: str):
        if not delta:
            return
        print(delta, end="", flush=True)
        self._buffer += delta
        # 遇到句末标点就切出一句
        while True:
            idx = -1
            for i, ch in enumerate(self._buffer):
                if ch in self._END_PUNCT:
                    idx = i
                    break
            if idx < 0:
                break
            sentence = self._buffer[: idx + 1].strip()
            self._buffer = self._buffer[idx + 1:]
            if sentence:
                with self._lock:
                    self._queue.append(sentence)

    def finish(self):
        if self._buffer.strip():
            with self._lock:
                self._queue.append(self._buffer.strip())
            self._buffer = ""
        self._done.set()
        self._thread.join(timeout=120)
        print()
