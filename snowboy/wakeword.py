import os,json,sys,configparser
import pyaudio

workdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(workdir)

from snowboy import snowboydecoder
import configparser

config = configparser.ConfigParser()
config.read(os.path.join(workdir, "config.ini"),encoding="UTF-8")

class SnowboyWakeWord:
    def __init__(self):
        self.model_path = os.path.join(workdir,"snowboy",config['Wakeword']['Snowboy_Model_Path'])
        self.sensitivity = float(config['Wakeword']['Sensitivity'])
        self.wake_word_detected = False
        self.detector = snowboydecoder.HotwordDetector(self.model_path, sensitivity=self.sensitivity)

    def detected(self):
        self.wake_word_detected = True   
        self.detector.terminate()

    def detect_wake_word(self):
        print('正在检测唤醒词... 按 Ctrl+C 退出')
        self.detector.start(detected_callback=self.detected, 
                      sleep_time=0.03)
        keyword_num = self.detector.num_hotwords
        # print('唤醒词已检测到')
        return keyword_num
    
    def audiodevice(self):
        p = pyaudio.PyAudio()
        print("可用的输入设备：")
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if dev['maxInputChannels'] > 0:
                print(f"  设备 {i}: {dev['name']}")

        print("可用的输出设备：")
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if dev['maxOutputChannels'] > 0:
                print(f"  设备 {i}: {dev['name']}")


if __name__ == "__mian__":
    snowboywakeword = SnowboyWakeWord()
    snowboywakeword.detect_wake_word()