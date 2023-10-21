import os
import json
import requests
import configparser
import importlib
from . import erniebotsingle
from . import text2speech
erniebotsingleclass = erniebotsingle.ErnieBotSingle()

config = configparser.ConfigParser()
config.read(os.path.join(os.getcwd(), "config.ini"),encoding="UTF-8")
configsection = config['baiduernie']
ErnieApiVersion = configsection["ErnieApiVersion"]

def get_access_token():
    """
    使用 API Key，Secret Key 获取access_token，替换下列示例中的应用API Key、应用Secret Key
    """
    ApiKey = configsection['ApiKey']
    keySecret = configsection['keySecret']
    url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={ApiKey}&client_secret={keySecret}"
    
    payload = json.dumps("")
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get("access_token")

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

class ErnieBotFunction:
    def __init__(self):
        pass
    def chat_with_funciton(self,prompt_messages,function_call=["none"],voice_name="zh-CN-XiaoxiaoNeural"):
    # 从文件中读取已有的函数插件列表
        funnctionpluginlist_file_path = os.path.join(os.getcwd(),"functionplugin","functionpluginlist.json")
        with open(funnctionpluginlist_file_path, 'r' ,encoding="UTF-8") as f:
            functions = json.load(f)  

        if function_call[0] == "none":
            # 如果function_call为none，那就调用一次简单的erniebot函数，不带任何函数功能。
            # print("不需要调用任何的插件。简单请求一次GPT")
            response_message = erniebotsingleclass.chat(prompt_messages,voice_name)
            return response_message
        elif function_call[0] == "auto":
            # 如果function_call为auto，就使用全部的插件。
            pass
            # print("调用的函数：")
            # print(functions)
        else:
            # 如果function_call为具体名字，就使用具体的插件。
            functions = filter_dict_array(functions,"name",function_call)
            # print("调用的函数：")
            # print(functions)

        requesturl = ErnieApiVersion + "?access_token=" + get_access_token()
        headers = {'Content-Type': 'application/json'}
        system = prompt_messages[0]["content"] # 文心一言的system不再messages中。需要从messages中获取。
        prompt_messages.pop(0)  # 文心一言的system不再messages中。需要从messages中删除。
        # print("调用函数前的prompt_message")
        # print(prompt_messages)

        if len(prompt_messages) % 2 == 0:
            # 文心一言的messages长度必须为奇数
            prompt_messages.pop(0)
        payload = json.dumps({
            "functions":functions,
            "messages": prompt_messages
        })
        response = requests.request("POST", requesturl, headers=headers, data=payload)
        response_json = json.loads(response.text)

        if "error_code" in response_json:
            responseresult = f'服务出错，错误码：{response_json["error_code"]}'
            print(responseresult)
            response_message = {"role": "assistant","content": responseresult}
            return response_message
        elif "function_call" in response_json:
            print("首次调用reniebot，返回了JSON格式的数据。")
            print(response_json["function_call"])
            function_name = response_json['function_call']['name']
            function_args_str = response_json['function_call']['arguments']
            function_args = json.loads(function_args_str)
            function_thoughts = response_json['function_call']['thoughts']

            # 组装第二次请求时的message
            response_message = {"role": "assistant", "content": response_json["result"], "function_call": {"name": function_name, "arguments": function_args_str}}
            prompt_messages.append(response_message)

            # 根据函数名称，加载同名模块下的同名函数。
            module_name = function_name
            module_path = os.path.join(os.getcwd(),'functionplugin', module_name + '.py')
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
                prompt_messages.append(
                    {
                        "role": "function",
                        "name": function_name,
                        "content": function_response_str,
                    }
                )
                # print("再次调用插件时的，prompt_messages")
                # print(prompt_messages)
                second_response = erniebotsingleclass.chat(prompt_messages,voice_name) #再次请求一次无函数调用功能的reniebot
                # print("再次调用一次reniebot返回的结果。")
                print(second_response["content"])
                return second_response
            else:
                # 调用函数后，函数会返回是否再调用一次的字段，以下部分是不需要再次调用GPT的场景，在这种条件下，可以将函数返回的内容直接返回给终端用户。
                # print("调用插件后，插件不要求再次调用GPT，插件直接返回了结果。")
                print(function_response['details'])
                tts = text2speech.AzureTTS(voice_name)
                tts.text2speech_and_play(function_response['details'])
                second_response= {"role":"assistant","content":function_response['details']}
                return second_response
        else:
            # 虽然明确要求使用函数插件，但是因为信息不足等原因，还是直接返回了面向终端用户的信息。
            # print("虽然要求调用了插件，但是GPT还是返回了直接面向终端用户的信息，表示现有的信息不足以按插件要求返回JSON数据。")
            responseresult = response_json["result"]
            print(responseresult)
            response_message = {"role": "assistant","content": responseresult}
            return response_message

if __name__ == '__main__':
    system_content = "你是一个有用的智能助手。"
    function_call = input("请输入插件的名称：")
    prompt = input("请输入你的问题：")
    messages=[{"role":"system","content":system_content},{"role": "user", "content":prompt}]
    erniebotfunction = ErnieBotFunction()
    result = erniebotfunction.chat_with_funciton(messages,function_call)
    print(result['content'])