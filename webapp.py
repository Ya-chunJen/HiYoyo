# -*- coding: utf-8 -*-
"""HiYoyo 局域网 Web 聊天服务。

在同一局域网内的手机浏览器打开终端打印的地址即可使用。

启动：
    python3 webapp.py

配置（可选，在 config.ini 中）：
    [WebApp]
    port = 8666
"""
import json
import socket
import threading

from flask import Flask, request, Response, jsonify, send_from_directory

from core import config
from core.robots import RobotManager
from core.llm import LLMClient
from core.conversation import Conversation

app = Flask(__name__, static_folder=None)

robots = RobotManager()
robots.default()
llm = LLMClient()
_state_lock = threading.Lock()  # 保护角色切换与会话读写的线程安全


# ---------- 页面与静态资源 ----------

@app.route("/")
def index():
    return send_from_directory("web", "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory("web", filename)


# ---------- API ----------

def _robot_brief(robot: dict) -> dict:
    return {
        "id": robot["id"],
        "name": robot["name"],
        "keyword": robot["keyword"],
        "description": robot["description"],
        "greeting": robot["greeting"],
        "has_plugins": bool(robot.get("plugins") and robot["plugins"][0] != "none"),
    }


@app.route("/api/robots")
def api_robots():
    return jsonify({
        "current": robots.current["id"],
        "robots": [_robot_brief(r) for r in robots.robots],
    })


@app.route("/api/switch", methods=["POST"])
def api_switch():
    body = request.get_json(silent=True) or {}
    robot_id = body.get("id", "")
    with _state_lock:
        if robot_id not in {r["id"] for r in robots.robots}:
            return jsonify({"error": f"没有此角色：{robot_id}"}), 404
        robot = robots.switch(robot_id)
    return jsonify({"current": _robot_brief(robot)})


@app.route("/api/history")
def api_history():
    robot = robots.current
    conv = Conversation(robot.get("username") or robot["id"])
    return jsonify({"messages": conv.messages[-40:]})


@app.route("/api/clear", methods=["POST"])
def api_clear():
    robot = robots.current
    Conversation(robot.get("username") or robot["id"]).clear()
    return jsonify({"ok": True})


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


@app.route("/api/chat", methods=["POST"])
def api_chat():
    body = request.get_json(silent=True) or {}
    question = (body.get("text") or "").strip()
    if not question:
        return jsonify({"error": "消息不能为空"}), 400

    with _state_lock:
        robot = robots.current
        plugins = list(robot.get("plugins") or [])
        model = robot.get("model") or None

        conv = Conversation(robot.get("username") or robot["id"])
        conv.append({"role": "user", "content": question})
        messages = conv.build(robot["system"])

        def generate():
            answer = ""
            try:
                if not plugins or plugins[0] == "none":
                    # 无插件：逐字流式输出
                    for delta in llm.chat_stream(messages, model=model):
                        answer += delta
                        yield _sse({"type": "delta", "delta": delta})
                else:
                    # 带插件：等插件执行完后一次性返回最终回答
                    yield _sse({"type": "status", "text": "正在调用插件…"})
                    answer = llm.chat_with_plugins(messages, plugins, speaker=None, model=model)
                    yield _sse({"type": "delta", "delta": answer})
            except Exception as e:
                answer = answer or f"抱歉，请求模型服务时出错：{e}"
                yield _sse({"type": "error", "message": str(e)})

            conv.append({"role": "assistant", "content": answer})
            conv.save()
            yield _sse({"type": "done"})

        return Response(generate(), mimetype="text/event-stream",
                        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


def _lan_ip() -> str:
    """获取本机局域网 IP。"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


if __name__ == "__main__":
    port = int(config.get("WebApp", "port", "8666") or 8666)
    ip = _lan_ip()
    print(f"system:HiYoyo Web 聊天服务已启动！")
    print(f"system:本机访问   http://127.0.0.1:{port}")
    print(f"system:手机访问   http://{ip}:{port}   （确保手机与本机在同一局域网）")
    app.run(host="0.0.0.0", port=port, threaded=True)
