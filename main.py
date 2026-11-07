# -*- coding: utf-8 -*-
"""HiYoyo 智能音箱 - 语音模式主程序。

流程：唤醒词唤醒 -> Azure ASR 语音转文字 -> LLM（可带插件）流式回答
-> 分句 TTS 朗读；对话中说出其他角色的关键词即可切换角色，
说出停止词或保持沉默则进入睡眠。
"""
import sys

from core import config
from core.config import workdir
sys.path.append(workdir)

from core.llm import LLMClient
from core.robots import RobotManager
from core.tts import TTS, SentenceSpeaker
from core.conversation import Conversation
from speechmodules.speech2text import AzureASR


class Yoyo:
    def __init__(self):
        self.robots = RobotManager()
        self.llm = LLMClient()
        self.asr = AzureASR()
        self.stopword = config.wakeword()["stopword"]
        self.robots.default()

    # ---------- 唤醒词 ----------

    def _setup_wakeword(self):
        ww = config.wakeword()
        scheme = ww["scheme"].lower()

        if scheme == "keyboard":
            from core.wakeword_keyboard import KeyboardWakeWord
            self.wakeword = KeyboardWakeWord()
            return

        if scheme == "openwakeword":
            from core.wakeword_openwakeword import OpenWakeWordEngine
            self.wakeword = OpenWakeWordEngine()
            return

        raise SystemExit("config.ini 中 WakeUpScheme 可选值：OpenWakeWord / Keyboard")

    # ---------- 对话 ----------

    def chat(self, question: str):
        """处理一轮对话：历史 -> LLM（可带插件）-> 流式打印 + 分句朗读 -> 存档。"""
        robot = self.robots.current
        tts = TTS(robot.get("voice", ""))
        # 纯文本音色（voice 为空）时不启用朗读
        speaker = SentenceSpeaker(tts) if robot.get("voice", "") else None

        conv = Conversation(robot.get("username") or robot["id"])
        conv.append({"role": "user", "content": question})

        messages = conv.build(robot["system"])
        model = robot.get("model") or None
        answer = self.llm.chat_with_plugins(messages, robot.get("plugins"), speaker=speaker, model=model)

        conv.append({"role": "assistant", "content": answer})
        conv.save()

    # ---------- 主循环 ----------

    def run(self):
        robot = self.robots.current
        print(f"system:叮叮当当！我的唤醒词是：{config.wakeword()['wakewordtext']}")
        TTS("edge:zh-CN-XiaoxiaoNeural").speak(
            f"叮叮当当！我的唤醒词是：{config.wakeword()['wakewordtext']}")

        while True:
            # 持续监测唤醒词，未监测到则保持监听
            if self.wakeword.detect_wake_word() < 0:
                continue

            print(f"{robot['name']}:{robot['greeting']}")
            TTS(robot.get("voice", "")).speak(robot["greeting"])

            keep_awake = True
            while keep_awake:
                question = self.asr.speech2text()
                if not question or self.stopword in question:
                    print(f"{robot.get('username', 'You')}:{question}")
                    print(f"system:拜拜，有事用唤醒词叫我。已进入睡眠模式！")
                    TTS(robot.get("voice", "")).speak("拜拜，有事用唤醒词叫我。")
                    keep_awake = False
                    continue

                # 判断是否要切换角色
                target = self.robots.find_keyword(question)
                if target is not None:
                    self.robots.switch(target["id"])
                    robot = self.robots.current
                    print(f"system:已切换到「{target['keyword']}」。")
                    TTS(robot.get("voice", "")).speak(f"已切换到「{target['keyword']}」，{robot['greeting']}")
                    continue

                print(f"{robot.get('username', 'You')}:{question}")
                self.chat(question)

    def loop(self):
        self._setup_wakeword()
        while True:
            try:
                self.run()
            except KeyboardInterrupt:
                print("\nsystem:再见！")
                break


if __name__ == '__main__':
    yoyo = Yoyo()
    yoyo.loop()
