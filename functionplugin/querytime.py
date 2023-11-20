import os
import datetime
import pytz
import json

def querytime(function_args):
    current_time = datetime.datetime.now()
    tz = pytz.timezone('Asia/Shanghai')
    # 获取周几
    weekday_dict = {0: '星期一',1: '星期二',2: '星期三',3: '星期四',4: '星期五',5: '星期六',6: '星期天',}
    weekday = weekday_dict[current_time.weekday()]
    # 返回当前时间的文本格式
    nowtime = '{} {} {}'.format(current_time.strftime('%Y-%m-%d %H:%M:%S'), weekday, tz.tzname(current_time))
    # print(nowtime)
    callback_json =  {"request_gpt_again":True,"details":f"<参考信息>：现在的详细时间是：{nowtime}"}
    return callback_json