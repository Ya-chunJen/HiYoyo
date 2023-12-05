# 通过URL请求OpanAI的接口，主要用于函数调用。
import os,json,sys,configparser,requests
workdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(workdir)

import importlib

# 读取openai的配置参数文件。
config = configparser.ConfigParser()
config.read(os.path.join(workdir, "config.ini"),encoding="UTF-8")
configsection = config['Openai']

from speechmodules import text2speech
from openaibot import openaibotsingle
openaibotsingleclass = openaibotsingle.OpenaiBotSingle()

def find_values_by_index(list1, list2, index):
    # 两个元素数量一致的列表，列表元素均为字符串。已知一个列表的值，寻找另一个列表中，其下标一致的值。
    result = ""
    for i in range(len(list1)):
        if list1[i] == index:
            result = list2[i]
    return result

def filter_dict_array(dict_array,key,key_array):
    # 一个列表dict_array（其每个元素都为字典），另外一个列表key_array（其每个元素都是一个字典的值），通过此函数可以过滤dict_array中指定key为指定值的字典元素，形成一个新的列表。
    # functions = filter_dict_array(functions,"name",function_call)
    result = []
    for d in dict_array:
        for k in  key_array:
            if d.get(key) == k: # 精准匹配
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

        if function_call[0] == "none":
            # 如果function_call为["none"]，那就调用一次简单的chatGPT函数，不带任何函数功能。
            # print("不需要调用任何的插件。简单请求一次GPT")
            ai_response_dict = openaibotsingleclass.chat(prompt_messages,voice_name)
            return ai_response_dict
        elif function_call[0] == "auto":
            # 如果function_call为["auto"]，就使用全部的插件。一般不会使用，因为带的内容太多了。
            functions = functions
        else:
            # 如果function_call为具体函数名字的列表，就使用具体的插件。并把这些插件，插入到tools列表中。
            functions = filter_dict_array(functions,"name",function_call)

        # 组装tools字段类型，给tool_choice变量赋值。
        for function in functions:
            tools_item = {"type": "function","function": function}
            tools.append(tools_item)
        tool_choice="auto"
        # print(f"调用的函数：\n {tools}")

        # 组装调用ChatgptFunction的messages。
        function_prompt_messages = [{"role": "system","content":"Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous"}]
        function_prompt_messages.append(prompt_messages[-1])
        # print("调用函数前的function_prompt_messages")
        # print(function_prompt_messages)

        # 组装请求ChatgptFunction的data
        data = {
            "model": "gpt-3.5-turbo-1106",
            "messages": function_prompt_messages,
            "tools":tools,
            "tool_choice":tool_choice
        }

        # 发起ChatgptFunction的请求
        ai_function_response = requests.post(self.openai_api_url, headers=self.headers, data=json.dumps(data))
        # print(ai_function_response.text)

        ai_function_response_dict = ai_function_response.json()['choices'][0]['message']
        # print(ai_function_response_dict)
        return_message = []
        # return_message.append(ai_function_response_dict) #不将ChatGPT function和function本身的结果放入到聊天记录中。

        if ai_function_response_dict.get("tool_calls"):
            # 判断ai_function_response_dict中是不是有名为tool_calls的键。
            # print("首次调用GPT，返回了JSON格式的数据。")
            function_prompt_messages.append(ai_function_response_dict) # 将首次请求结果放入到prompt_message中，准备第二次请求。
            tool_calls = ai_function_response_dict['tool_calls'] # 获取首次请求返回的函数调用信息。
            for tool_call in tool_calls:
                # 函数可能会需要调用多个函数，循环每个需要调用的函数。
                if tool_call['type'] == "function":
                    # tool_call中可能还是其他工具，需要判断一下，是不是fuction
                    function_name = tool_call['function']['name']  # 获取要调用函数的名称
                    function_args_str = tool_call['function']['arguments'] # 获取调用函数的参数信息
                    function_args = json.loads(function_args_str) # 参数信息原来是字符串要转为json

                    # 根据函数名称，加载同名模块下的同名函数。
                    module_name = function_name
                    module_path = os.path.join(workdir, 'functionplugin', module_name + '.py')
                    module = importlib.util.module_from_spec(spec:= importlib.util.spec_from_file_location(module_name, module_path)) # type: ignore
                    spec.loader.exec_module(module)
                    fuction_to_call = getattr(module, function_name)  # 获取函数对象
                    # 调用执行对应的函数，并将结果赋值给function_response，function_response为固定的json格式。
                    function_response = fuction_to_call(function_args)
                    # print(function_response)

                    # 组装二次调用的message
                    function_message = {
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": function_name,
                        "content": function_response["details"],
                    }
                    function_prompt_messages.append(function_message)
                    # return_message.append(function_message) # 不将ChatGPT function和function本身的结果放入到聊天记录中。
            
            # print(f"二次调用时的prompt message：{function_prompt_messages}")
            second_ai_response_dict = openaibotsingleclass.chat(function_prompt_messages,voice_name)
            # print(f"再次调用一次GPT返回的结果:{second_ai_response_dict}")
            return_message.append(second_ai_response_dict)
            return return_message

        else:
            # 虽然明确要求使用函数插件，但是因为信息不足等原因，还是直接返回了面向终端用户的信息。
            # print("虽然要求调用了插件，但是GPT还是返回了直接面向终端用户的信息，表示现有的信息不足以按插件要求返回JSON数据。")
            return return_message

if __name__ == '__main__':
    system_content = "你是一个有用的智能助手！"
    function_call_name_1 = input("请输入插件1的名称：") or "sendemail"
    function_call_name_2 = input("请输入插件2的名称：") or "posttoqw"
    function_call = [function_call_name_1,function_call_name_2]
    prompt = input("请输入你的问题：") or "将我中了500万大大奖这条消息,推送到企业微信。同时发邮件告诉任亚军，你可以躺平了。"
    messages=[{"role":"system","content":system_content},{"role": "user", "content":prompt}]
    openaibotfunction = OpenaiBotFunction()
    result = openaibotfunction.chat_with_funciton(messages,function_call)
    if isinstance(result, list):
        response_content = result[-1]["content"]
    else:
        response_content = result["content"]
    print(response_content)