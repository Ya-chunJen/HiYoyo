import os
import json

from speechmodules.speech2text import AzureASR
from speechmodules.text2speech import AzureTTS
from chatgpt.chatgptmult import ChatGptMult
import configparser

config = configparser.ConfigParser()
config.read(os.path.join(os.getcwd(), "config.ini"),encoding="UTF-8")
robot_info_file_path = os.path.join(os.getcwd(), "robot_info.json")
chatgptmult = ChatGptMult()

# 增加程序启动时的开机广告，并且告知用户智能音箱的唤醒词。
print(f"system:开机广告时间，广告位长期招商！我的唤醒词是：{config['Wakeword']['wakewordtext']}")
AzureTTS("zh-CN-XiaoxiaoNeural").text2speech_and_play(f"开机广告时间，广告位长期招商！我的唤醒词是：{config['Wakeword']['wakewordtext']}")

# 这是用于判断一个字符串中，是不是包含一个列表中的任意词，如果包含就会返回列表中的这个元素。
# 实际业务上，是判断语音转为文字的内容，是不是包含任意一个智能语音助手的激活关键词。
def find_robot_keyword(s,lst):
    for elem in lst:
        if elem in s:
            return elem
    return None

class Yoyo:
    def __init__(self):
        with open(robot_info_file_path , 'r' ,encoding="UTF-8") as f:
            # 导入智能助手的配置文件。
            self.robot_info = json.load(f)
            self.robot_id_list = [d['robot_id'] for d in self.robot_info]
            self.robot_keywords_list = [d['robot_keyword'] for d in self.robot_info]

    def robot_model(self,robot_id="xiaozhushou"):
        # 主要用于判断加载哪一个智能语音助手。
        try:
            robot_index = self.robot_id_list.index(robot_id)
        except ValueError:
            raise SystemExit("没有此配置的机器人！")

        self.robot_name = self.robot_info[robot_index ]['robot_name']
        self.robot_describe = self.robot_info[robot_index ]['robot_describe']
        self.robot_voice_name = self.robot_info[robot_index ]['robot_voice_name']
        self.robot_reply_word = self.robot_info[robot_index ]['robot_reply_word']
        self.robot_system_content = self.robot_info[robot_index ]['robot_system_content']
        self.username = self.robot_info[robot_index ]['username']  
        self.asr = AzureASR()
        self.tts = AzureTTS(self.robot_voice_name)
        self.stopword = config['Wakeword']['StopWord']
        if config['Wakeword']['WakeUpScheme'] == "Picovoice":            
            from picovoice.wakeword import PicoWakeWord
            self.wakeword = PicoWakeWord()      
        elif config['Wakeword']['WakeUpScheme'] == "Snowboy":
            from snowboy.wakeword import SnowboyWakeWord
            self.wakeword = SnowboyWakeWord()  
        else:
            raise SystemExit("config.ini配置文件中，WakeUpScheme可选值只有：Picovoice和 Snowboy")

    def run(self):
        while True:
            isdetected = self.wakeword.detect_wake_word() # 持续监测麦克风收录的声音是不是包含唤醒词，监测到后会返回大于0的整数。如果没有监测到就持续监测。
            if isdetected >= 0:
                # 唤醒后，打印和播放当前智能语音助手的打招呼语。
                print(f'{self.robot_name}:{self.robot_reply_word}')  
                self.tts.text2speech_and_play(self.robot_reply_word)
                keepawake = True # 用于控制智能语音助手是不是保持持续对话模式，为假的话会进入睡眠模式，睡眠模式下需要用唤醒词重新唤醒。
                while keepawake:         
                    q = self.asr.speech2text() # 获取用户输入的内容，由录音转为文字。
                    if q == None or self.stopword in q:
                        # 判断录入的内容是不是空值，或者录入的录入的内容是不是包含“停止词”。如果为空或者包含停止词，则进入睡眠模式。
                        print(f'{self.username}:{q}')
                        print(f"{self.robot_name}:拜拜，有事用唤醒词叫我。")
                        self.tts.text2speech_and_play(f"拜拜，有事用唤醒词叫我。")
                        print("system:已经进入睡眠模式！")                        
                        keepawake = False
                    else:
                        robot_keyword = find_robot_keyword(q,self.robot_keywords_list) #判断用户录入的内容是不是包含任意一个智能语音助手的激活关键词。如果不包含，就请求ChatGPT的结果。如果包含，就切换到对应的智能语音助手。
                        if robot_keyword == None:                          
                            print(f'{self.username}:{q}') # 打印用户录入的内容
                            res = chatgptmult.chatmult(self.username,q,self.robot_system_content) # 请求ChatGPT的接口。
                            print(f'{self.robot_name}(GPT)：{res}')   # 打印返回的结果。
                            self.tts.text2speech_and_play(res)   # 朗读返回的结果。
                        else:
                            switch_robot_index = self.robot_keywords_list.index(robot_keyword)
                            switch_robot_id = self.robot_info[switch_robot_index]["robot_id"] # 确定要切换到哪一个智能语音助手。
                            self.robot_model(switch_robot_id)   #切换智能语音助手。
                            print(f"system:已切换到「{robot_keyword}」。")
                            self.tts.text2speech_and_play(f"已切换到「{robot_keyword}」")
                            # keepawake = False #原本切换智能语音助手后需要重新唤醒，现在应该不需要了。                                           

    def loop(self,):
        while True:
            try:
                self.robot_model()
                self.run()
            except KeyboardInterrupt:
                break

if __name__ == '__main__':
    yoyo = Yoyo()
    yoyo.loop()