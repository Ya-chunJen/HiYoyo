import os
import datetime
import pytz
import json
import requests
import configparser

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.ini"),encoding="UTF-8")
configsection = config['serpapi']

def search(function_args):
    q = function_args['q']
    params = {
        "q": q ,
        "engine":"baidu",
        "api_key": configsection["key"]
    }
    url = f"https://serpapi.com/search.json?engine=baidu&q={q}"
    response = requests.get(url, params=params)
    if response.status_code == 200:
        first_res = response.json()['organic_results'][0]
        snippet = first_res.get("snippet","")
        title = first_res.get("title","")
        link = first_res.get("link","")
        for i in range(5):
            first_res = response.json()['organic_results'][i]
            snippet = first_res.get("snippet","")
            if snippet != "":
                title = first_res.get("title","")
                link = first_res.get("link","")
                break
        final_res = {"title":title,"snippet":snippet,"link":link}
        # print(final_res)
    else:
        print("Error: ", response.status_code)

    callback_json =  {"request_gpt_again":True,"details":final_res}
    return json.dumps(callback_json)

if __name__ == '__main__':
    q = input("要搜索的关键词：")
    function_args = {"q":q}
    search(function_args)





