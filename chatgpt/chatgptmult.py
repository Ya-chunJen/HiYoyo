import sys
import os
import json
import os
import copy
from .chatgpt import OpenAiChatGPT


chatgpt = OpenAiChatGPT()

class ChatGptMult:
    def __init__(self):
        pass

    def chatmult(self,username,prompt,system_content="You are a helpful assistant"):
        # 用户ID文件路径
        username_fpath = f"log/{username}.json"
        username_fpath = os.path.join(os.getcwd(),username_fpath)
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
        response_dit = chatgpt.chat(messages_thistime) #使用Azure的接口
        
        # 将本次的回答和历史记录整合
        message.append(response_dit)

        with open(username_fpath, "w",encoding='utf-8') as file:
            json.dump(message, file)

        # 单独获取结果并打印，并作为函数返回结果
        response_content = response_dit["content"]
        # print(response_content)
        return response_content

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if len(sys.argv) == 3:
            username = sys.argv[1]   
            prompt =  sys.argv[2]
            system_content = "You are a helpful assistant"
        if len(sys.argv)==4:
            username = sys.argv[1]   
            prompt =  sys.argv[2]
            system_content = sys.argv[3] 
        chatgptmult = ChatGptMult()
        chatgptmult.chatmult(username,prompt,system_content)