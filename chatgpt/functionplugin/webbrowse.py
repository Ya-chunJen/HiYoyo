import os
import json

def webbrowse(url):
    replyjsonjson = json.loads(url)
    url = replyjsonjson["url"]
    os.system(f'open {url}')
    plugin_res = {"request_gpt_again":False,"details":"WebBrowse插件已经打开该网站，请检查。"} 
    return plugin_res