# -*- coding: utf-8 -*-
"""统一读取 config.ini。各配置段含义见 config_example.ini。"""
import os
import configparser

workdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

_config = configparser.ConfigParser()
_config.read(os.path.join(workdir, "config.ini"), encoding="UTF-8")


def get(section: str, key: str, default: str = "") -> str:
    """读取配置项，段或键不存在时返回默认值。"""
    try:
        return _config.get(section, key).strip()
    except (configparser.NoSectionError, configparser.NoOptionError, KeyError):
        return default


def llm() -> dict:
    """获取 LLM 配置（[LLM] 段：任意 OpenAI 兼容服务）。"""
    return {
        "base_url": get("LLM", "base_url") or "https://api.openai.com/v1",
        "api_key": get("LLM", "api_key"),
        "model": get("LLM", "model") or "gpt-4o-mini",
        "vision_model": get("LLM", "vision_model") or None,
        "temperature": float(get("LLM", "temperature", "0.7") or 0.7),
        "max_history": int(get("LLM", "max_history", "20") or 20),
    }


def azure_speech() -> dict:
    return {
        "api_key": get("AzureSpeech", "AZURE_API_KEY"),
        "region": get("AzureSpeech", "AZURE_REGION", "eastasia"),
    }


def wakeword() -> dict:
    return {
        "scheme": get("Wakeword", "WakeUpScheme", "OpenWakeWord"),
        "wakewordtext": get("Wakeword", "wakewordtext", "HiYoyo"),
        "sensitivity": float(get("Wakeword", "Sensitivity", "0.6") or 0.6),
        "stopword": get("Wakeword", "StopWord", "退下吧"),
        "openwakeword_model": get("Wakeword", "OpenWakeWord_Model", "hey_jarvis_v0.1"),
        "openwakeword_threshold": get("Wakeword", "OpenWakeWord_Threshold", "0.5"),
        "input_device": get("Wakeword", "Input_Device"),
    }
