# -*- coding: utf-8 -*-
"""openWakeWord 唤醒方案：完全离线、无需任何 API key。

模型文件在首次运行时自动下载（需要能访问 GitHub，可用代理），
下载后即离线使用。内置唤醒词：hey jarvis / alexa / hey mycroft。

实现要点：openWakeWord 模型内部维护跨帧的音频特征缓存，
必须以 80ms（1280 采样）小块连续喂数据，且检测命中前不要 reset()，
否则识别率会严重下降。
"""
import os

import numpy as np
import sounddevice as sd

from core import config

SAMPLE_RATE = 16000
CHUNK = 1280  # 80ms @16kHz，openWakeWord 官方推荐的流式喂数粒度

# 调试开关：启动前 export HIYOYO_WW_DEBUG=1 可看到实时分数与音量
DEBUG = os.environ.get("HIYOYO_WW_DEBUG", "") == "1"

# 可用的内置唤醒词模型（省略 .onnx 后缀）
AVAILABLE_MODELS = ["hey_jarvis_v0.1", "alexa_v0.1", "hey_mycroft_v0.1"]


class OpenWakeWordEngine:
    def __init__(self):
        ww = config.wakeword()
        self.threshold = float(ww["openwakeword_threshold"] or 0.5)
        model_name = ww["openwakeword_model"] or "hey_jarvis_v0.1"
        if model_name not in AVAILABLE_MODELS:
            print(f"system:唤醒词模型 {model_name} 不在可用列表 {AVAILABLE_MODELS} 中，使用 hey_jarvis_v0.1。")
            model_name = "hey_jarvis_v0.1"
        self.model_name = model_name
        self._frames = 0

        self._ensure_model()

        from openwakeword.model import Model

        self.model = Model(
            wakeword_models=[os.path.join(self._models_dir(), model_name + ".onnx")],
            inference_framework="onnx",
        )

        self.stream = sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=CHUNK,
            dtype="int16",
            channels=1,
            device=self._resolve_device(ww.get("input_device", "")),
        )
        self.stream.start()
        self._check_input_level()
        print(f"system:【语音唤醒模式】openWakeWord，唤醒词：{model_name.replace('_v0.1', '').replace('_', ' ')}"
              f"（阈值 {self.threshold}，可用 HIYOYO_WW_DEBUG=1 查看实时分数）")

    @staticmethod
    def _resolve_device(name: str):
        """按名称模糊匹配输入设备；留空用系统默认。匹配不到则回退默认并提示。"""
        if not name:
            return None
        for d in sd.query_devices():
            if d["max_input_channels"] > 0 and name.lower() in d["name"].lower():
                print(f"system:使用输入设备 [{d['index']}] {d['name']}")
                return d["index"]
        print(f"system:未找到名称包含「{name}」的输入设备，使用系统默认设备。")
        return None

    # ---------- 模型管理 ----------

    @staticmethod
    def _models_dir() -> str:
        import openwakeword

        return os.path.join(os.path.dirname(openwakeword.__file__), "resources", "models")

    def _ensure_model(self):
        """模型缺失时自动下载（走系统代理环境变量）。"""
        path = os.path.join(self._models_dir(), self.model_name + ".onnx")
        if os.path.exists(path) and os.path.getsize(path) > 10000:
            return
        print(f"system:首次使用 openWakeWord，正在下载唤醒词模型 {self.model_name}…")
        from openwakeword.utils import download_models

        download_models(model_names=[self.model_name])
        print("system:模型下载完成。")

    def _check_input_level(self):
        """开机自检：读 0.5 秒音频，若接近静音大概率是麦克风设备/权限问题。"""
        data, overflowed = self.stream.read(SAMPLE_RATE // 2)
        audio = np.frombuffer(bytes(data), dtype=np.int16).astype(np.float32)
        rms = float(np.sqrt(np.mean(np.square(audio))))
        peak = float(np.max(np.abs(audio)))
        if peak < 50:
            print(f"system:警告：麦克风输入几乎无声（峰值 {peak:.0f}），"
                  "请检查系统输入设备选择与麦克风权限（系统设置 -> 隐私与安全性 -> 麦克风）。")
        elif DEBUG:
            print(f"system:麦克风自检 OK（RMS {rms:.0f}，峰值 {peak:.0f}）")

    # ---------- 主循环调用 ----------

    def detect_wake_word(self) -> int:
        """读取 80ms 音频并预测；命中唤醒词返回 0，否则返回 -1。"""
        data, overflowed = self.stream.read(CHUNK)
        frame = np.frombuffer(bytes(data), dtype=np.int16)
        scores = self.model.predict(frame)
        self._frames += 1

        if DEBUG and self._frames % 12 == 0:  # 约每秒打印一次
            peak = int(np.max(np.abs(frame.astype(np.int32))))
            print(f"debug:分数 {scores} | 音量峰值 {peak}")

        score = max(scores.values()) if scores else 0.0
        if score >= self.threshold:
            self.model.reset()  # 命中后重置特征缓存，等待下一次唤醒
            return 0
        return -1

    def close(self):
        self.stream.stop()
        self.stream.close()


if __name__ == "__main__":
    engine = OpenWakeWordEngine()
    print("正在检测唤醒词... 按 Ctrl+C 退出")
    try:
        while True:
            if engine.detect_wake_word() >= 0:
                print("我听到了！")
    except KeyboardInterrupt:
        engine.close()
