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

def find_values_by_index(list1, list2, index):
    # 两个元素数量一致的列表，列表元素均为字符串。已知一个列表的值，寻找另一个列表中，其下标一致的值。
    result = ""
    for i in range(len(list1)):
        if list1[i] == index:
            result = list2[i]
    return result

# 不能函数功能时，仅简单调用。
def chatGPT(prompt_messages):
    completion = openai.ChatCompletion.create(
        deployment_id = modelname,
        messages=prompt_messages,
        temperature=0.8
    )
    response_message = completion.choices[0].message  # type: ignore
    return response_message

# 从文件中读取已有的函数插件列表
funnctionpluginlist_file_path = os.path.join(os.getcwd(),"chatgpt","functionplugin","functionpluginlist.json")
with open(funnctionpluginlist_file_path, 'r' ,encoding="UTF-8") as f:
    functions = json.load(f)  
    function_name_list = [function['name'] for function in functions] # 读取所有的函数插件的名称，形成一个列表。
    function_name_list = [{'name': item} for item in function_name_list] # 将函数名称变为{'name': '***'}的示例。
    function_name_list.append("auto") # 追加一个特殊的auto模式，auto模式是一个字符串。

    function_keyword_list = [function['keyword'] for function in functions]  #读取所有函数的激活关键词，形成一个列表。
    function_keyword_list.append("全部插件") # 追加一个auto特殊的模式。
    # print(function_name_list)
    # print(function_keyword_list)

def chatGPT_with_plugin(prompt_messages,function_call="none"):
    # 根据prompt_messages中包含的关键词，决定调用具体哪一个函数插件。全部插件是一个特殊的模式。
    for function_keyword in function_keyword_list:
        if function_keyword in prompt_messages[-1]["content"] or function_keyword in prompt_messages[-2]["content"]:
            function_name = find_values_by_index(function_keyword_list,function_name_list,function_keyword)
            function_call = function_name
            prompt_messages[-1]["content"] = prompt_messages[-1]["content"].replace(function_keyword, "")
            prompt_messages[-2]["content"] = prompt_messages[-2]["content"].replace(function_keyword, "")
            prompt_messages[0]["content"] = "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."
            break
    
    if function_call == "none" :
        # 如果function_call还是为none，那就调用一次简单的chatGPT函数，不带任何函数功能。
        response_message = chatGPT(prompt_messages)
        return response_message
    
    print(prompt_messages)
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
        response_message['function_call'] = response_message['function_call'].to_dict()
        function_name = response_message['function_call']['name']
        function_args_str = response_message['function_call']['arguments']
        function_args = json.loads(function_args_str)

        # 根据函数名称，加载同名模块下的同名函数。
        module_name = function_name
        module_path = os.path.join(os.path.dirname(__file__), 'functionplugin', module_name + '.py')
        module = importlib.util.module_from_spec(spec:= importlib.util.spec_from_file_location(module_name, module_path)) # type: ignore
        spec.loader.exec_module(module)
        fuction_to_call = getattr(module, function_name)  # 获取函数对象

        # 调用对应的函数，并将结果赋值给function_response
        function_response_str = fuction_to_call(function_args)
        function_response = json.loads(function_response_str)
        
        if function_response['request_gpt_again']:
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
            print(prompt_messages)
            second_response = chatGPT(prompt_messages) #再次请求一次无函数调用功能的chatGPT
            print(second_response)
            return second_response
        else:
            # 调用函数后，函数会返回是否再调用一次的字段，以下部分是不需要再次调用GPT的场景，在这种条件下，可以将函数返回的内容直接返回给终端用户。
            second_response= {"role":"assistant","content":function_response['details']}
            return second_response
    else:
        # 虽然明确要求使用函数插件，但是因为信息不足等原因，还是直接返回了面向终端用户的信息。
        response_message['content'] = function_keyword + response_message['content']
        return response_message

if __name__ == '__main__':
    # prompt = input("请输入你的问题：")
    prompt = "请问现在几点了。"
    # prompt = "querytime插件 打开百度首页。"
    # prompt = "auto插件 请给任亚军发一封邮件，主题是「谢谢你的款待」，正文是「真的非常感谢」"
    # prompt = "auto插件 请发一封邮件。"
    system_content = "你是一个有用的智能助手。"
    messages=[{"role":"system","content":system_content},{"role": "user", "content":prompt}]
    result = chatGPT_with_plugin(messages)
    print(result['content'])


    