# -*- coding: utf-8 -*-
"""多轮会话历史管理。

会话记录以 JSON 数组形式保存在 log/<username>.json 中，
兼容旧版格式（同样为 messages 数组）。
"""
import os
import json

from core import config

workdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
LOG_DIR = os.path.join(workdir, "log")


class Conversation:
    def __init__(self, username: str):
        self.username = username or "You"
        os.makedirs(LOG_DIR, exist_ok=True)
        self.path = os.path.join(LOG_DIR, f"{self.username}.json")
        self.messages = []
        self.load()

    def load(self):
        """加载历史记录（若存在）。兼容旧版记录。"""
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    # 只保留 user / assistant 消息，system 每次由角色配置提供
                    self.messages = [m for m in data if m.get("role") in ("user", "assistant")]
            except (OSError, json.JSONDecodeError):
                self.messages = []

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.messages, f, ensure_ascii=False, indent=2)

    def append(self, message: dict):
        self.messages.append(message)

    def clear(self):
        self.messages = []
        self.save()

    def build(self, system_content: str, max_history: int = None) -> list:
        """组装本次请求的 messages：system + 最近 N 条历史。"""
        if max_history is None:
            max_history = config.llm()["max_history"]
        history = [m for m in self.messages if m.get("role") in ("user", "assistant")]
        if max_history > 0:
            history = history[-max_history:]
        return [{"role": "system", "content": system_content}] + history
