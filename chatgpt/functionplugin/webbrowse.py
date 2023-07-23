import os
import json

def webbrowse(function_args):
    # replyjsonjson = json.loads(url)
    url = function_args["url"]
    os.system(f'open {url}')
    callback_json = {"request_gpt_again":False,"details":"WebBrowse插件已经打开该网站，请检查。"} 
    return json.dumps(callback_json)