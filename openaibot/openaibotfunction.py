import os,json,sys,configparser
import openai
import importlib

workdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(workdir)

from openaibot import openaibotsingle
from speechmodules import text2speech

openaibotsingleclass = openaibotsingle.OpenaiBotSingle()

config = configparser.ConfigParser()
config.read(os.path.join(workdir, "config.ini"),encoding="UTF-8")
configsection = config['Openai']

import requests

def find_values_by_index(list1, list2, index):
    # 两个元素数量一致的列表，列表元素均为字符串。已知一个列表的值，寻找另一个列表中，其下标一致的值。
    result = ""
    for i in range(len(list1)):
        if list1[i] == index:
            result = list2[i]
    return result

def filter_dict_array(dict_array, key, val_array):
    """
    过滤数组中key为指定值的字典元素
    functions = filter_dict_array(functions,"name",function_call)
    """
    result = []
    for d in dict_array:
        for v in  val_array:
            if d.get(key) == v: # 精准匹配
                result.append(d)
    return result


class OpenaiBotFunction:
    def __init__(self):
        self.openai_api_url = configsection['openai_api_domain'] + "/v1/chat/completions"
        self.openai_api_key = configsection['openai_api_key']
        self.headers = {"Content-Type": "application/json","Authorization": "Bearer " + self.openai_api_key}
        self.model = "gpt-3.5-turbo"

    def chat_with_funciton(self,prompt_messages,function_call=["none"],voice_name="zh-CN-XiaoxiaoNeural"):
        tools = []
        # 从文件中读取已有的函数插件列表
        funnctionpluginlist_file_path = os.path.join(workdir,"functionplugin","functionpluginlist.json")
        with open(funnctionpluginlist_file_path, 'r' ,encoding="UTF-8") as f:
            functions = json.load(f)
            #print(functions)

        if function_call[0] == "none":
            # 如果function_call为none，那就调用一次简单的chatGPT函数，不带任何函数功能。
            # print("不需要调用任何的插件。简单请求一次GPT")
            response_message = openaibotsingleclass.chat(prompt_messages,voice_name)
            return response_message
        elif function_call[0] == "auto":
            # 如果function_call为auto，就使用全部的插件。一般不会使用。
            tool_choice="auto"
            # print("调用的函数：")
            # print(functions)
        else:
            # 如果function_call为具体名字，就使用具体的插件。并把这些插件，插入到tools列表中。
            functions = filter_dict_array(functions,"name",function_call)
            for function in functions:
                tools_item = {"type": "function","function": function}
                tools.append(tools_item)
            tool_choice="auto"
            # print("调用的函数：")
            # print(tools)

        prompt_messages[0]['content'] = "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous"
        # print("调用函数前的prompt_message")
        # print(prompt_messages)
        data = {
            "model": "gpt-3.5-turbo-1106",
            "messages": prompt_messages,
            "tools":tools,
            "tool_choice":tool_choice
        }
        response = requests.post(self.openai_api_url, headers=self.headers, data=json.dumps(data)) 
        # print(response.json())
        response_message = response.json()['choices'][0]['message']
        # print(response_message)

        if response_message.get("tool_calls"):
            # print("首次调用GPT，返回了JSON格式的数据。")
            prompt_messages.append(response_message)
            tool_calls = response_message['tool_calls']
            for tool_call in tool_calls:
                if tool_call['type'] == "function":
                    function_name = tool_call['function']['name']
                    function_args_str = tool_call['function']['arguments']
                    function_args = json.loads(function_args_str)

                    # 根据函数名称，加载同名模块下的同名函数。
                    module_name = function_name
                    module_path = os.path.join(workdir, 'functionplugin', module_name + '.py')
                    module = importlib.util.module_from_spec(spec:= importlib.util.spec_from_file_location(module_name, module_path)) # type: ignore
                    spec.loader.exec_module(module)
                    fuction_to_call = getattr(module, function_name)  # 获取函数对象

                    # 调用对应的函数，并将结果赋值给function_response
                    function_response_str = fuction_to_call(function_args)
                    function_response = function_response_str

                    prompt_messages.append(
                        {
                            "tool_call_id": tool_call["id"],
                            "role": "tool",
                            "name": function_name,
                            "content": function_response['details'],
                        }
                    )
            
            # print(prompt_messages)
            second_response = openaibotsingleclass.chat(prompt_messages,voice_name)
            # print("再次调用一次GPT返回的结果。")
            # print(second_response)
            return second_response

        else:
            # 虽然明确要求使用函数插件，但是因为信息不足等原因，还是直接返回了面向终端用户的信息。
            # print("虽然要求调用了插件，但是GPT还是返回了直接面向终端用户的信息，表示现有的信息不足以按插件要求返回JSON数据。")
            return response_message

if __name__ == '__main__':
    system_content = "你是一个有用的智能助手！"
    function_call_name_1 = input("请输入插件1的名称：") or "sendemail"
    function_call_name_2 = input("请输入插件2的名称：") or "posttoqw"
    function_call = [function_call_name_1,function_call_name_2]
    prompt = input("请输入你的问题：") or "将我中了500万大大奖这条消息,推送到企业微信。同时发邮件告诉任亚军，你可以躺平了。"
    messages=[{"role":"system","content":system_content},{"role": "user", "content":prompt}]
    openaibotfunction = OpenaiBotFunction()
    result = openaibotfunction.chat_with_funciton(messages,function_call)
    print(result['content'])