import os
import sys
import json
import openai
import configparser
import importlib
import copy

config = configparser.ConfigParser()
config.read(os.path.join(os.getcwd(), "config.ini"),encoding="UTF-8")
configsection = config['Azureopenai']

openai.api_type = "azure"
openai.api_version = configsection['openai_api_version']
openai.api_key = configsection['openai_api_key']
openai.api_base = configsection['openai_api_base']
modelname = configsection['gpt35_deployment_name']

def chatGPT(prompt_messages,model=modelname):
    completion = openai.ChatCompletion.create(
        deployment_id = model,
        messages=prompt_messages,
        temperature=0.8
    )
    response_message = completion.choices[0].message  # type: ignore
    return response_message

funnctionpluginlist_file_path = os.path.join(os.getcwd(),"chatgpt","functionplugin","functionpluginlist.json")
with open(funnctionpluginlist_file_path, 'r' ,encoding="UTF-8") as f:
    functions = json.load(f)

def chatGPT_with_plugin(prompt_messages,model="GPT350613",function_call="auto"):
    completion = openai.ChatCompletion.create(
        deployment_id = model,
        messages = prompt_messages,
        functions = functions,
        function_call = function_call,  # auto is default, but we'll be explicit
    )
    # print(completion)
    response_message = completion['choices'][0]['message'] # type: ignore
    # print(response_message)
    call_function_name = response_message['function_call']['name']
    call_function_body = response_message['function_call']['arguments']

    module_name = call_function_name
    module_path = os.path.join(os.path.dirname(__file__), 'functionplugin', module_name + '.py')
    module = importlib.util.module_from_spec(spec:= importlib.util.spec_from_file_location(module_name, module_path)) # type: ignore
    spec.loader.exec_module(module)
    func = getattr(module, call_function_name)  # 获取函数对象

    callback_json = func(call_function_body)
    if callback_json['request_gpt_again']:
        # print(callback_json['details'])
        prompt_messages_second = copy.deepcopy(prompt_messages)
        # 将调用插件后的使用提示，追加在原始prompt_messages中user>content后。
        prompt_messages_second[-1]["content"] = prompt_messages_second [-1]["content"] + callback_json['details']
        # print(prompt_messages_second)
        response_second = chatGPT(prompt_messages_second)
        response_second["content"] = response_second["content"] + f"\n本次回复使用了插件：{call_function_name}"
    else:
        # print(callback_json['details'])
        response_second = {"role":"assistant","content":callback_json['details']}
    # print(response_second)
    return response_second

if __name__ == '__main__':
    if len(sys.argv) > 1:
        prompt = sys.argv[1]
        messages=[{"role":"system","content":"You are a helpful assistant"},{"role": "user", "content":prompt}]
        chatGPT_with_plugin(messages)