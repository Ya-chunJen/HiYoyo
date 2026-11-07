# HiYoyo 基于大模型的智能音箱

一个基于大语言模型（LLM）的智能音箱项目，可以运行在主流操作系统上（Windows、macOS、Linux，甚至树莓派、香橙派等单板机）。

项目灵感来源于 [Orator](https://github.com/MedalCollector/Orator)，并在初期参考了其核心实现。

## 2026 大版本更新说明

项目最初诞生于 2023 年大模型兴起之际，本次做了整体重构升级：

1. **统一 LLM 接入**：基于 `openai>=1.x` 官方 SDK，通过 `base_url + model` 两行配置即可接入任意 OpenAI 兼容服务——OpenAI、DeepSeek、通义千问、智谱GLM、Kimi、本地 Ollama 等，不再需要为每家厂商维护一套代码（旧的 openaibot / azurebot / erniebot 三套模块已合并为 `core/llm.py`）。
2. **流式响应 + 分句朗读**：大模型边生成边打印、边按句朗读，响应体感大幅提升。
3. **免费 TTS 兜底**：文字转语音支持 Azure 语音与免费的 Edge-TTS 双引擎，角色音色通过 `azure:` / `edge:` 前缀选择，未配置 Azure key 时自动使用 Edge-TTS。
4. **移除 snowboy 与 Picovoice**：snowboy 停更多年无法编译、Picovoice 免费套餐已于 2026-06-30 停运，均已移除（历史代码可在 git 记录中找回），唤醒词改用完全离线免费的 openWakeWord。
5. **插件系统保留并增强**：Function Calling 插件契约不变，任何支持 tool calls 的模型都可以驱动插件「动起来」（发邮件、控制履带车、看摄像头等）。
6. **角色配置重新设计**：`robot_info.json` 采用更简洁的新格式，同时兼容旧格式自动转换；修正了旧配置中多位「方言兔」打招呼语串词的问题。
7. **视觉能力升级**：`videovison` 插件改用 base64 直传本地图片，不再强依赖阿里云 OSS，配合 `vision_model` 配置即可使用。

## 基本实现原理

1. 使用 openWakeWord 持续监听麦克风，检测唤醒词（完全离线、免费、无需 key；也可选回车键唤醒）；
2. 唤醒后调用 Azure 语音识别（ASR），把听到的话转成文字（支持中/英/日自动识别）；
3. 将文字连同会话历史发给 LLM，流式获取回答；
4. 回答按句切分，交给 TTS（Azure 或 Edge-TTS）朗读；
5. 对话中说出其他「智能语音角色」的关键词即可切换角色；说出停止词或保持沉默则进入睡眠，等待唤醒词再次唤醒。

## 安装部署

### 1、硬件要求

- 支持麦克风和扬声器的音频设备（带麦克风的耳机也可以），建议 USB 连接而非蓝牙。

### 2、软件要求

- Python 3.9+
- 安装依赖：

```bash
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3、账号需求

- **任意一家 OpenAI 兼容的大模型服务**（DeepSeek / 通义千问 / GLM / Kimi / OpenAI / 本地 Ollama 均可），拿到 `base_url`、`api_key` 和模型名。
- **Azure 语音服务** key（ASR 必需；如果只用文本模式或 Edge-TTS 朗读，可以不配）。
- 语音唤醒使用 openWakeWord，**免费离线、无需任何 key**（首次使用联网下载约 2MB 模型）。

## 使用步骤

### 1. 配置

复制 `config_example.ini` 为 `config.ini`，填写：

- `[LLM]`：`base_url`、`api_key`、`model`（常用厂商的配置示例直接写在注释里）；
- `[AzureSpeech]`：Azure 语音的 key 和区域；- `[Wakeword]`：`WakeUpScheme` 推荐用默认的 `OpenWakeWord`（离线免费）；内置唤醒词 `hey jarvis` / `alexa` / `hey mycroft`，可通过 `OpenWakeWord_Model` 选择、`OpenWakeWord_Threshold` 调灵敏度。

> 配置说明：所有配置段见 `config_example.ini`，大模型统一使用 `[LLM]` 段接入。

### 2. 启动

```bash
# 文本模式（终端对话，无需麦克风）
python3 main_text.py

# 语音模式（智能音箱）
python3 main.py

# 局域网 Web 模式（手机浏览器聊天）
python3 webapp.py
```

### 3. 手机上使用（Web 模式）

启动 `webapp.py` 后，终端会打印局域网地址（如 `http://192.168.x.x:8666`），确保手机与本机连接同一 Wi-Fi，用手机浏览器打开即可：

- 移动端优先的聊天界面，自动适配深色模式；
- 顶栏菜单可随时切换 21 个「智能语音角色」，会话历史按角色自动加载；
- 回答流式逐字显示；🗑 按钮可清空当前角色的对话历史；
- 端口可在 config.ini 中通过 `[WebApp] port` 修改（默认 8666）。

## 「智能语音角色」

在 `robot_info.json` 中配置，理论上可以配置无限多个角色，对话时说出角色的 `keyword` 即可切换。新格式示例：

```json
{
    "default_robot": "xiaozhushou",
    "robots": [
        {
            "id": "xiaozhushou",
            "name": "小助手",
            "keyword": "小助手模式",
            "description": "默认模式，一个智能小助手",
            "greeting": "嗯，你好！",
            "system": "你的名字叫Yoyo，是一个语音智能助手。回答字数控制在100个字以内。",
            "voice": "edge:zh-CN-XiaoxiaoNeural",
            "plugins": [],
            "model": "",
            "username": "You"
        }
    ]
}
```

字段说明：

| 字段 | 说明 |
| --- | --- |
| `id` | 角色 id，不能是中文 |
| `name` | 角色名称，用于展示 |
| `keyword` | 语音切换关键词，对话中说出即切换到该角色 |
| `greeting` | 唤醒/切换到该角色时的打招呼语 |
| `system` | 请求 LLM 时的 system prompt |
| `voice` | 音色：`azure:xxx` 用 Azure，`edge:xxx` 用 Edge-TTS，留空自动选择，`""` 纯静音 |
| `plugins` | 该角色可用的插件名列表，`["auto"]` 为全部，`[]` 为不用插件 |
| `model` | 可为该角色单独指定模型，留空使用全局 `[LLM] model` |
| `username` | 会话记录文件名（log/ 目录下） |

Edge-TTS 可用音色见：https://speech.platform.balena.com/voices 或运行 `edge-tts --list-voices`。

## 插件（Function Calling）

- 插件列表在 `functionplugin/functionpluginlist.json` 中定义，格式为 OpenAI tools 规范；
- 插件程序放在 `functionplugin/` 目录下，**插件名、模块名、函数名必须完全一致**；
- 插件函数只接受一个 `function_args` 字典参数；
- 返回约定格式：`{"request_gpt_again": True/False, "details": "..."}`——`True` 表示把 details 交回 LLM 组织回答，`False` 表示直接把 details 返回给用户。

内置插件：`search`（联网搜索）、`sendemail`（发邮件）、`posttoqw`（推送企业微信群）、`querytime`（查时间）、`macshell`（执行 Mac 终端命令）、`videovison`（摄像头视觉，需配 `vision_model`）、`wjxwjlist` / `wjxanalysis`（问卷星）、`tank`（履带车硬件控制，需树莓派/香橙派）等。

## 文件目录说明

```
HiYoyo/
├── main.py                  # 语音模式主程序
├── main_text.py             # 文本模式主程序（支持热词：模式切换/清空对话等）
├── webapp.py                # 局域网 Web 聊天服务（手机浏览器使用）
├── web/index.html           # Web 聊天页面（移动端优先，单文件）
├── config_example.ini       # 配置文件模板，复制为 config.ini
├── robot_info.json          # 「智能语音角色」配置
├── core/
│   ├── config.py            # 配置读取（兼容旧版配置段）
│   ├── llm.py               # 统一 LLM 客户端（流式、工具调用、多模态）
│   ├── conversation.py      # 多轮会话历史管理（log/*.json）
│   ├── robots.py            # 角色管理与切换
│   └── tts.py               # 统一 TTS（Azure / Edge-TTS 双引擎）+ 分句朗读器
├── speechmodules/
│   ├── speech2text.py       # Azure 语音识别
│   └── text2speech.py       # Azure 语音合成
├── functionplugin/          # 插件目录
└── log/                     # 会话记录（按 username 存储）
```

## 部署为开机自启（Linux 示例）

```bash
sudo nano /etc/systemd/system/hiyoyo.service
```

```ini
[Unit]
Description=HiYoyo Smart Speaker
After=multi-user.target

[Service]
Type=simple
WorkingDirectory=/home/orangepi/HiYoyo
ExecStart=/usr/bin/python3 /home/orangepi/HiYoyo/main.py
Restart=on-abort

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now hiyoyo.service
```

macOS 可以把启动命令写成 `.command` 文件双击运行：

```bash
#!/bin/bash
cd /path/to/HiYoyo && python3 main.py
```
