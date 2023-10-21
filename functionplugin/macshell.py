import os
import json

def macshell(function_args):
    commands = function_args["commands"]
    print(commands)
    os.system(f'{commands}')
    callback_json = {"request_gpt_again":False,"details":"终端命令已执行。"} 
    return json.dumps(callback_json)