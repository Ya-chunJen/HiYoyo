import os
import json
import openai
import configparser
import importlib
from . import chatgptsingle
from . import text2speech
chatgptsingleclass = chatgptsingle.ChatGptSingle()

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.ini"),encoding="UTF-8")
configsection = config['Azureopenai']

openai.api_type = "azure"
openai.api_version = configsection['openai_api_version']
openai.api_key = configsection['openai_api_key']
openai.api_base = configsection['openai_api_base']
modelname = configsection['gpt35_deployment_name']

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


class ChatGptFunction:
    def __init__(self):
        pass
    def chat_with_funciton(self,prompt_messages,function_call=["none"],voice_name="zh-CN-XiaoxiaoNeural"):
    # 从文件中读取已有的函数插件列表
        funnctionpluginlist_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),"functionplugin","functionpluginlist.json")
        with open(funnctionpluginlist_file_path, 'r' ,encoding="UTF-8") as f:
            functions = json.load(f)  

        if function_call[0] == "none":
            # 如果function_call为none，那就调用一次简单的chatGPT函数，不带任何函数功能。
            # print("不需要调用任何的插件。简单请求一次GPT")
            response_message = chatgptsingleclass.chat(prompt_messages,voice_name)
            return response_message
        elif function_call[0] == "auto":
            # 如果function_call为auto，就使用全部的插件。一般不会使用。
            function_call = "auto"
            # print("调用的函数：")
            # print(functions)
        else:
            # 如果function_call为具体名字，就使用具体的插件。
            functions = filter_dict_array(functions,"name",function_call)
            function_call = "auto"
            # print("调用的函数：")
            # print(functions)

        # print("调用函数前的prompt_message")
        # print(prompt_messages)
        completion = openai.ChatCompletion.create(
            deployment_id = modelname,
            messages = prompt_messages,
            functions = functions,
            function_call = function_call,
        )
        response_message = completion['choices'][0]['message'].to_dict() # type: ignore
        response_message.setdefault('content', None) # 如果调用了函数，返回值是没有content的。但是随后再次提交，还需要content值。所以需要插入一个空值。
        # print(response_message)

        if response_message.get("function_call"):
            # print("首次调用GPT，返回了JSON格式的数据。")
            response_message['function_call'] = response_message['function_call'].to_dict()
            function_name = response_message['function_call']['name']
            function_args_str = response_message['function_call']['arguments']
            function_args = json.loads(function_args_str)

            # 根据函数名称，加载同名模块下的同名函数。
            module_name = function_name
            module_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'functionplugin', module_name + '.py')
            module = importlib.util.module_from_spec(spec:= importlib.util.spec_from_file_location(module_name, module_path)) # type: ignore
            spec.loader.exec_module(module)
            fuction_to_call = getattr(module, function_name)  # 获取函数对象

            # 调用对应的函数，并将结果赋值给function_response
            function_response_str = fuction_to_call(function_args)
            function_response = json.loads(function_response_str)
            
            if function_response['request_gpt_again']:
                # print("调用插件后，插件要求再调用一次GPT。")
                # 调用函数后，函数会返回是否再调用一次的字段，以下部分是需要再次调用GPT的场景。
                # print(function_response['details'])
                prompt_messages.append(response_message)
                prompt_messages.append(
                    {
                        "role": "function",
                        "name": function_name,
                        "content": function_response_str,
                    }
                )
                # print("再次调用插件时的，prompt_messages")
                prompt_messages[0]["content"] = "你是一个有用的智能助手。"
                # print(prompt_messages)
                # second_response = chatGPT(prompt_messages) #再次请求一次无函数调用功能的chatGPT
                second_response = chatgptsingleclass.chat(prompt_messages,voice_name) #再次请求一次无函数调用功能的chatGPT
                # print("再次调用一次GPT返回的结果。")
                # print(second_response)
                return second_response
            else:
                # 调用函数后，函数会返回是否再调用一次的字段，以下部分是不需要再次调用GPT的场景，在这种条件下，可以将函数返回的内容直接返回给终端用户。
                # print("调用插件后，插件不要求再次调用GPT，插件直接返回了结果。")
                tts = text2speech.AzureTTS(voice_name)
                tts.text2speech_and_play(function_response['details'])
                second_response= {"role":"assistant","content":function_response['details']}
                return second_response
        else:
            # 虽然明确要求使用函数插件，但是因为信息不足等原因，还是直接返回了面向终端用户的信息。
            # print("虽然要求调用了插件，但是GPT还是返回了直接面向终端用户的信息，表示现有的信息不足以按插件要求返回JSON数据。")
            return response_message

if __name__ == '__main__':
    system_content = "你是一个有用的智能助手。"
    function_call = input("请输入插件的名称：")
    prompt = input("请输入你的问题：")
    messages=[{"role":"system","content":system_content},{"role": "user", "content":prompt}]
    chatgptfunction = ChatGptFunction()
    result = chatgptfunction.chat_with_funciton(messages,function_call)
    print(result['content'])