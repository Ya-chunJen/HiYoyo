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

def find_robot_keyword(s,lst):
    for elem in lst:
        if elem in s:
            return elem
    return None

class Yoyo:
    def __init__(self):
        with open(robot_info_file_path , 'r' ,encoding="UTF-8") as f:
            self.robot_info = json.load(f)
            self.robot_id_list = [d['robot_id'] for d in self.robot_info]
            self.robot_keywords_list = [d['robot_keyword'] for d in self.robot_info]

    def robot_model(self,robot_id="yoyo"):
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
        self.tts.text2speech_and_play(f"开机广告时间，广告位长期招商！")
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
            isdetected = self.wakeword.detect_wake_word()
            if isdetected >= 0:
                print(f'{self.robot_name}:{self.robot_reply_word}')
                self.tts.text2speech_and_play(self.robot_reply_word)
                sleep = True            
                while sleep:         
                    q = self.asr.speech2text()
                    if q == None or self.stopword in q:
                        print("system:已经进入睡眠模式！")
                        self.tts.text2speech_and_play(f"拜拜，有事用唤醒词叫我。")
                        sleep = False
                    else:
                        robot_keyword = find_robot_keyword(q,self.robot_keywords_list)
                        if robot_keyword == None:
                            print(f'{self.username}:{q}')
                            res = chatgptmult.chatmult(self.username,q,self.robot_system_content)
                            print(f'{self.robot_name}(GPT)：{res}')
                            self.tts.text2speech_and_play(res)   
                        else:
                            switch_robot_index = self.robot_keywords_list.index(robot_keyword)
                            switch_robot_id = self.robot_info[switch_robot_index]["robot_id"]
                            self.robot_model(switch_robot_id)  
                            print(f"已切换到「{robot_keyword}」,请用唤醒词重新唤醒。")
                            self.tts.text2speech_and_play(f"已切换到「{robot_keyword}」,请用唤醒词重新唤醒我。")
                            sleep = False                                                

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