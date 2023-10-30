import os
import json
import os
import copy

import sys
workdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(workdir)

from chatgpt import chatgptsingle
from chatgpt import chatgptfunction

chatgptsingle = chatgptsingle.ChatGptSingle()
chatgptfunction = chatgptfunction.ChatGptFunction()

class ChatGptMult:
    def __init__(self):
        pass

    def chatmult(self,username,prompt,system_content="You are a helpful assistant",functionname="none",voice_name="zh-CN-XiaoxiaoNeural"):
        # 用户ID文件路径
        username_fpath = f"{username}.json"
        username_fpath = os.path.join(workdir,"log",username_fpath)
        # 判断用户ID文件是不是存在，存在就读取，不存在就建立
        if os.path.exists(username_fpath):
            with open(username_fpath) as f:
                message = json.load(f) 
        else:
            message = []
            system_dict = {"role":"system","content": system_content}
            message.append(system_dict)

        # 构造本次问答的问题
        prompt_dict = {"role":"user","content": prompt}
        
        # 将本次的提问和历史记录整合
        message.append(prompt_dict)

        # 如果聊天记录很长，只选取system和最近两轮的会话
        messages_thistime = copy.deepcopy(message)
        if len(messages_thistime)>=5:
            messages_thistime = [messages_thistime[0]] + messages_thistime[-4:]
            # print(messages_thistime)

        # 调用单轮会话的模块获取结果
        # response_dit = chatgptsingle.chat(messages_thistime,voice_name) #使用Azure的接口
        # 调用支持函数的单轮会话模块获取结果。
        response_dit = chatgptfunction.chat_with_funciton(messages_thistime,functionname,voice_name) 
        
        # print(response_dit)
        # 将本次的回答和历史记录整合
        message.append(response_dit)

        with open(username_fpath, "w",encoding='utf-8') as file:
            json.dump(message, file)

        # 单独获取结果并打印，并作为函数返回结果
        response_content = response_dit["content"]
        # print(response_content)
        return response_content

if __name__ == '__main__':
    username = "1"
    prompt =  input("请输入你的问题：")
    system_content = "你是一个有用的智能助手。"
    functionname = "none"
    chatgptmult = ChatGptMult()
    chatgptmult.chatmult(username,prompt,system_content,functionname)