# -*- coding: utf-8 -*-
"""统一的大模型客户端。

基于 openai>=1.x 官方 SDK，通过 base_url + model 即可接入任意
OpenAI 兼容服务：OpenAI / DeepSeek / 通义千问 / 智谱GLM / Kimi /
本地 Ollama 等，并支持流式输出与 Function Calling（插件系统）。
"""
import os
import json
import base64
import importlib.util

from openai import OpenAI

from core import config

workdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
PLUGIN_DIR = os.path.join(workdir, "functionplugin")
PLUGIN_LIST_PATH = os.path.join(PLUGIN_DIR, "functionpluginlist.json")


class LLMClient:
    def __init__(self):
        s = config.llm()
        self.client = OpenAI(
            api_key=s["api_key"] or "EMPTY",
            base_url=s["base_url"],
        )
        self.model = s["model"]
        self.vision_model = s["vision_model"]
        self.temperature = s["temperature"]

    # ---------- 基础对话 ----------

    def chat_stream(self, messages: list, model: str = None, temperature: float = None):
        """流式对话，逐段 yield 增量文本。"""
        stream = self.client.chat.completions.create(
            model=model or self.model,
            messages=messages,
            temperature=self.temperature if temperature is None else temperature,
            stream=True,
        )
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def chat(self, messages: list, model: str = None, temperature: float = None) -> str:
        """非流式对话，返回完整文本。"""
        resp = self.client.chat.completions.create(
            model=model or self.model,
            messages=messages,
            temperature=self.temperature if temperature is None else temperature,
            stream=False,
        )
        return resp.choices[0].message.content or ""

    # ---------- 带插件的对话 ----------

    def chat_with_plugins(self, messages: list, plugins: list = None,
                          speaker=None, model: str = None) -> str:
        """带插件（Function Calling）的对话。

        plugins: 插件名列表，如 ["sendemail", "posttoqw"]；
                 ["none"] 或空列表表示不使用插件；["auto"] 表示加载全部插件。
        speaker: 可选的 SentenceSpeaker，用于流式分句播报；为 None 时只打印。
        返回最终的 assistant 文本。
        """
        messages = [dict(m) for m in messages]
        plugins = plugins or ["none"]

        if not plugins or plugins[0] == "none":
            return self._stream_answer(messages, speaker, model)

        tools = self._load_tools(plugins)
        if not tools:
            print("system:没有找到可用的插件，按普通对话处理。")
            return self._stream_answer(messages, speaker, model)

        # 第一轮：不带流式，让模型决定是否调用工具
        try:
            resp = self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=self.temperature,
                stream=False,
            )
            msg = resp.choices[0].message
        except Exception as e:
            error_text = f"抱歉，请求模型服务时出错：{e}"
            print(error_text)
            return error_text

        if not msg.tool_calls:
            # 模型认为信息充足，直接给出面向用户的回答
            content = msg.content or ""
            print(content)
            if speaker:
                speaker.feed(content)
                speaker.finish()
            return content

        # 组装 assistant 的 tool_calls 消息
        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [tc.model_dump() for tc in msg.tool_calls],
        })

        # 逐个执行插件
        for tc in msg.tool_calls:
            fn_name = tc.function.name
            try:
                fn_args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                fn_args = {}
            result = self._run_plugin(fn_name, fn_args)
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "name": fn_name,
                "content": result.get("details", ""),
            })
            # 插件明确表示不需要再请求大模型时，直接把结果返回给用户
            if result.get("request_gpt_again") is False:
                print(result.get("details", ""))
                return result.get("details", "")

        # 第二轮：把工具结果交回模型，流式输出最终回答
        return self._stream_answer(messages, speaker, model)

    def _stream_answer(self, messages: list, speaker=None, model: str = None) -> str:
        """流式输出最终回答：边打印、边分句朗读，返回完整文本。"""
        if speaker is None:
            full = ""
            for delta in self.chat_stream(messages, model=model):
                print(delta, end="", flush=True)
                full += delta
            print()
            return full

        full = ""
        for delta in self.chat_stream(messages, model=model):
            speaker.feed(delta)
            full += delta
        speaker.finish()
        return full

    def _load_tools(self, plugins: list) -> list:
        """从 functionpluginlist.json 加载插件定义，包装成 OpenAI tools 格式。"""
        try:
            with open(PLUGIN_LIST_PATH, "r", encoding="UTF-8") as f:
                functions = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"system:读取插件列表失败：{e}")
            return []

        if "auto" in plugins:
            selected = functions
        else:
            selected = [f for f in functions if f.get("name") in plugins]

        return [{"type": "function", "function": fn} for fn in selected]

    @staticmethod
    def _run_plugin(name: str, args: dict) -> dict:
        """按「插件名 = 模块名 = 函数名」的约定加载并执行插件。

        插件返回约定格式：{"request_gpt_again": bool, "details": str}
        """
        module_path = os.path.join(PLUGIN_DIR, f"{name}.py")
        if not os.path.exists(module_path):
            return {"request_gpt_again": False,
                    "details": f"插件 {name} 不存在，请检查 functionplugin 目录。"}
        try:
            spec = importlib.util.spec_from_file_location(name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            fn = getattr(module, name)
            result = fn(args)
            if isinstance(result, dict) and "details" in result:
                result.setdefault("request_gpt_again", True)
                return result
            return {"request_gpt_again": True, "details": str(result)}
        except Exception as e:
            return {"request_gpt_again": False,
                    "details": f"插件 {name} 执行出错：{e}"}

    # ---------- 视觉（多模态） ----------

    def chat_with_image(self, images: list, prompt: str = "这张图片包含了什么内容？") -> str:
        """多模态识别。images 可为本地路径或 http(s) URL 列表。

        需要在 config.ini 的 [LLM] vision_model 中配置一个支持图片输入的模型。
        """
        model = self.vision_model or self.model
        content = [{"type": "text", "text": prompt}]
        for image in images:
            if image.startswith("http://") or image.startswith("https://"):
                url = image
            else:
                with open(image, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")
                url = f"data:image/jpeg;base64,{b64}"
            content.append({"type": "image_url", "image_url": {"url": url, "detail": "low"}})

        resp = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": content}],
            max_tokens=1000,
        )
        answer = resp.choices[0].message.content or ""
        print(answer)
        return answer
