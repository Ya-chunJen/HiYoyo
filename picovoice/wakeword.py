import pvporcupine
import pyaudio
import struct
import os
import configparser

config = configparser.ConfigParser()
config.read(f"{os.getcwd()}/config.ini")


class PicoWakeWord:
    def __init__(self):
        self.PICOVOICE_API_KEY = config['Wakeword']['Picovoice_Api_Key']
        self.keyword_path = os.path.join(os.getcwd(),config['Wakeword']['Picovoice_Model_Path'])
        self.model_path = None
        self.porcupine = pvporcupine.create(
            access_key=self.PICOVOICE_API_KEY,
            keywords= ['porcupine', 'ok google', "picovoice", "blueberry"]
            # keyword_paths=[self.keyword_path],           
            # model_path=self.model_path
        )
        self.myaudio = pyaudio.PyAudio()
        self.stream = self.myaudio.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length
        )

    def detect_wake_word(self):
        print('正在检测唤醒词... 按 Ctrl+C 退出') 
        audio_obj = self.stream.read(self.porcupine.frame_length, exception_on_overflow=False)
        audio_obj_unpacked = struct.unpack_from("h" * self.porcupine.frame_length, audio_obj)
        keyword_idx = self.porcupine.process(audio_obj_unpacked)
        return keyword_idx


if __name__ == '__main__':
    picowakeword = PicoWakeWord()
    while True:
        audio_obj = picowakeword.stream.read(picowakeword.porcupine.frame_length, exception_on_overflow=False)
        audio_obj_unpacked = struct.unpack_from("h" * picowakeword.porcupine.frame_length, audio_obj)

        keyword_idx = picowakeword.porcupine.process(audio_obj_unpacked)
        if keyword_idx >= 0:
            print("我听到了！")