import pyaudio

pa = pyaudio.PyAudio()

# 获取设备数量
device_count = pa.get_device_count()
print(f"总设备数：{device_count}")

# 遍历所有设备
for i in range(device_count):
    device_info = pa.get_device_info_by_index(i)
    print(f"设备{i}：{device_info['name']}, 支持{device_info['maxInputChannels']}个输入通道，支持{device_info['maxOutputChannels']}个输出通道。")

pa.terminate()
