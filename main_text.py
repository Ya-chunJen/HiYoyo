# -*- coding: utf-8 -*-
"""HiYoyo 智能助手 - 文本模式主程序。

在终端中以文本形式对话（无需声音输入输出），支持热词：
  - 模式切换      列出所有角色并切换
  - 打开对话文件  用系统默认程序打开当前会话记录
  - 清空对话      清空当前角色的会话历史
  - 语音对话模式  切换到语音模式（main.py）
"""
import os
import sys

from core.config import workdir
sys.path.append(workdir)

from core.llm import LLMClient
from core.robots import RobotManager
from core.conversation import Conversation


def input_line(prompt: str = "") -> str:
    try:
        return input(prompt)
    except EOFError:
        return ""


class YoyoText:
    def __init__(self):
        self.robots = RobotManager()
        self.llm = LLMClient()
        self.hotwords = ["模式切换", "打开对话文件", "清空对话", "语音对话模式"]
        self.robots.default()

    def _conversation(self) -> Conversation:
        robot = self.robots.current
        return Conversation(robot.get("username") or robot["id"])

    def hotword(self, word: str):
        robot = self.robots.current
        if word == "模式切换":
            print("现有角色如下：")
            for r in self.robots.robots:
                print(f"  - {r['keyword']}（{r['name']}）：{r['description']}")
            keyword = input_line("请输入角色关键词以切换：")
            if keyword in self.robots.keywords:
                self.robots.switch_by_keyword(keyword)
                robot = self.robots.current
                print(f"system:已切换到「{keyword}」。当前角色：{robot['name']} - {robot['description']}")
            else:
                print("system:没有这个关键词对应的角色。")
        elif word == "打开对话文件":
            path = os.path.join(workdir, "log", f"{robot.get('username') or robot['id']}.json")
            if sys.platform == "darwin":
                os.system(f'open "{path}"')
            elif os.name == "nt":
                os.startfile(path)  # type: ignore
            else:
                os.system(f'xdg-open "{path}"')
        elif word == "清空对话":
            self._conversation().clear()
            print("system:当前角色的会话历史已清空。")
        elif word == "语音对话模式":
            from main import Yoyo
            Yoyo().loop()

    def run(self):
        robot = self.robots.current
        print("system:欢迎进入HiYoyo智能助手，你可以直接对话，也可以输入「模式切换」切换角色。")
        print(f"system:当前角色「{robot['name']}」：{robot['description']}")
        while True:
            question = input_line(f"{robot.get('username', 'You')}：")
            if not question.strip():
                continue

            target = self.robots.find_keyword(question)
            hotword = next((w for w in self.hotwords if w in question), None)

            if target is not None:
                self.robots.switch(target["id"])
                robot = self.robots.current
                print(f"system:已切换到「{target['keyword']}」。当前角色：{robot['name']}")
            elif hotword:
                self.hotword(hotword)
            else:
                conv = self._conversation()
                conv.append({"role": "user", "content": question})
                messages = conv.build(robot["system"])
                print(f"{robot['name']}(AI)：", end="", flush=True)
                answer = self.llm.chat_with_plugins(messages, robot.get("plugins"), speaker=None,
                                                    model=robot.get("model") or None)
                conv.append({"role": "assistant", "content": answer})
                conv.save()

    def loop(self):
        while True:
            try:
                self.run()
            except KeyboardInterrupt:
                print("\nsystem:再见！")
                break


if __name__ == '__main__':
    YoyoText().loop()
