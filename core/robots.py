# -*- coding: utf-8 -*-
"""「智能语音角色」管理。

新版 robot_info.json 格式：
{
    "default_robot": "xiaozhushou",
    "robots": [
        {
            "id": "xiaozhushou",           # 角色 id，不能是中文
            "name": "小助手",               # 角色名称，用于展示
            "keyword": "小助手模式",        # 语音切换关键词
            "description": "默认模式",      # 角色简介
            "greeting": "嗯，你好！",       # 唤醒后的打招呼语
            "system": "你是……",            # LLM 的 system prompt
            "voice": "edge:zh-CN-XiaoxiaoNeural",  # azure:/edge:/留空自动
            "plugins": [],                 # 插件名列表，["auto"] 为全部
            "model": "",                   # 覆盖全局模型，留空用全局
            "username": "You"              # 会话记录文件名
        }
    ]
}

同时兼容旧版（顶层数组、robot_ 前缀字段）格式，加载时自动转换。
"""
import os
import json

workdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
ROBOT_INFO_PATH = os.path.join(workdir, "robot_info.json")


def _normalize(raw: dict) -> dict:
    """把新旧两种字段名归一化为统一结构。"""
    return {
        "id": raw.get("id") or raw.get("robot_id") or "",
        "name": raw.get("name") or raw.get("robot_name") or "",
        "keyword": raw.get("keyword") or raw.get("robot_keyword") or "",
        "description": raw.get("description") or raw.get("robot_describe") or "",
        "greeting": raw.get("greeting") or raw.get("robot_reply_word") or "",
        "system": raw.get("system") or raw.get("robot_system_content") or "You are a helpful assistant.",
        "voice": raw.get("voice") or raw.get("robot_voice_name") or "",
        "plugins": raw.get("plugins") if raw.get("plugins") is not None
                   else raw.get("robot_function_model") or [],
        "model": raw.get("model") or "",
        "username": raw.get("username") or raw.get("id") or raw.get("robot_id") or "You",
    }


class RobotManager:
    def __init__(self, path: str = ROBOT_INFO_PATH):
        with open(path, "r", encoding="UTF-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            # 旧版格式：顶层数组
            self.robots = [_normalize(r) for r in data]
            self.default_robot = self.robots[0]["id"] if self.robots else ""
        else:
            self.robots = [_normalize(r) for r in data.get("robots", [])]
            self.default_robot = data.get("default_robot") or (
                self.robots[0]["id"] if self.robots else "")

        self._by_id = {r["id"]: r for r in self.robots}
        self._by_keyword = {r["keyword"]: r for r in self.robots if r["keyword"]}
        self.current = None

    @property
    def keywords(self) -> list:
        return list(self._by_keyword.keys())

    def switch(self, robot_id: str) -> dict:
        """按角色 id 切换当前角色。"""
        if robot_id not in self._by_id:
            raise SystemExit(f"没有此配置的角色：{robot_id}")
        self.current = self._by_id[robot_id]
        return self.current

    def switch_by_keyword(self, keyword: str) -> dict:
        """按切换关键词切换当前角色。"""
        robot = self._by_keyword.get(keyword)
        if robot is None:
            raise SystemExit(f"没有此关键词对应的角色：{keyword}")
        self.current = robot
        return robot

    def find_keyword(self, text: str):
        """判断文本中是否包含任意角色的切换关键词，命中则返回该角色。"""
        for keyword, robot in self._by_keyword.items():
            if keyword and keyword in text:
                return robot
        return None

    def default(self) -> dict:
        return self.switch(self.default_robot)
