import os
import pyaudio
from . import snowboydecoder
import configparser

config = configparser.ConfigParser()
config.read(f"{os.getcwd()}/config.ini")

class SnowboyWakeWord:
    def __init__(self):
        self.model_path = os.path.join(os.getcwd(),config['Wakeword']['Snowboy_Model_Path'])
        self.sensitivity = float(config['Wakeword']['Sensitivity'])
        self.wake_word_detected = False
        self.detector = snowboydecoder.HotwordDetector(self.model_path, sensitivity=self.sensitivity)

    def detected(self):
        self.wake_word_detected = True
        # snowboydecoder.play_audio_file(os.path.join(os.getcwd(),config['Wakeword']['Wake_Sound']))    
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