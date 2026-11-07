# -*- coding: utf-8 -*-
"""键盘唤醒方案：按回车键唤醒，不依赖麦克风监听和任何在线服务。

作为 openWakeWord 语音唤醒不可用时的兜底方案。语音识别（ASR）仍使用 Azure。
"""


class KeyboardWakeWord:
    def __init__(self):
        print("system:【键盘唤醒模式】按回车键唤醒智能音箱，Ctrl+C 退出。")

    def detect_wake_word(self) -> int:
        try:
            input()
        except EOFError:
            raise KeyboardInterrupt
        return 0

    def close(self):
        pass
