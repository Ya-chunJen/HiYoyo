# Hiyoyo智能音箱
一个基于ChatGPT的智能音箱项目，可以运行在主流操作系统上，不同操作系统的唤醒词方案可能不尽相同。

本项目参考了以下项目：

https://github.com/MedalCollector/Orator

项目以上项目的不同点在于：
1. 唤醒词方案兼容了[snowboy的方案](https://github.com/Kitt-AI/snowboy/blob/master/README_ZH_CN.md)；
2. 支持多个智能语音角色并且支持平顺切换，对话时只需要说包含 robot_info.json 中不同智能助手的关键词就可以，如：占卜算命模式、儿童陪伴模式、英语口语学习模式。

## 特别注意
- Windows环境不需要关注任何snowboy相关的内容，做好picovoice的配置即可。
- 其他操作系统可以在 picovoice或snowboy 两个方案之前进行选择，推荐使用picovoice方案。

## 视频演示


## 实现原理
1. 使用picovoice或snowboy方案，调用音频输入设备持续进行关键词的监听；
2. 监听到唤醒词后，调用Azure的语音转文字接口，将听到的内容转为文字；
3. 将获取到的文字，调用ChatGPT的接口，获取返回结果；
4. 调用Azure的文字转语音接口，将ChatGPT的文字结果转为音频进行输出；
5. 如果持续进行对话，从第3点开始循环，如没有监听到任何内容，进入睡眠状态等待唤醒词。

## 安装部署要求
#### 1、硬件要求
- 在Windows、M1芯片的Mac上、X86的Linux上、香橙派上均测试成功。
- 目前程序还不支持分开指定输入和输出设备，所以最好配备一个同时支持麦克风和扬声器的设备，并且最好是USB的连接方式而不是蓝牙的连接方式。——如果遇到奇奇怪怪的错误，最好先检查一下音频输入和输出设备。

#### 2、软件要求
- Python3环境。
- 安装pyaudio。
- 使用snowboy项目编译「_ snowboydetect.so」文件时,需要安装比较的软件，请按snowboy项目的说明操作。——这一点可能是最大的障碍点。（Windows环境不需要。）

#### 3、账号需求
- Openai的Api
- 或者Azure版本Openai的Api
- Azure的语音相关Api
- Picovoice的KEY，在 https://picovoice.ai/ 注册登录后获取。（Windows环境必须。）

## 使用步骤
#### 1、clone本项目到本地
- main.py，程序的主文件
- config_example.ini，配置文件信息，用于存放需要调用一些接口的key信息，完全配置后，需要将文件名改为config.ini
- robot_info.json，智能助手的配置信息，理论上可以配置无限多个，相当于你有无限多个智能助手
- requirements.txt，项目需要安装的依赖
- speechmodules/speech2text.py，语音转文字功能程序
- speechmodules/text2speech.py，文字转语音功能程序
- chatgpt/chatgpt.py，不论Openai官方版本还是Azrue版本的单轮请求程序
- chatgpt/chatgptmult.py，用于存储保留多轮规划的chatgpt程序
- log文件夹，用于存储多轮会话的文件，每个会话人就是一个json文件
- snowboy/wakeword.py，snowboy唤醒词程序
- snowboy/snowboydecoder.py，snowboy相关程序，不需要修改
- snowboy/snowboydetect.py，snowboy相关程序，不需要修改
- snowboy/_ snowboydetect.so，这个程序需要自己编译，这个文件非常重要，请按照下面的步骤一步步操作
- snowboy/resources/common.res，snowboy的资源文件，不要修改就可以
- snowboy/resources/models，文件下的umdl文件和pmdl文件，是唤醒词模型文件，需要使用哪个唤醒词就需要在config.ini中引用哪一个文件
- picovoice/wakeword.py，picovoice方案的唤醒词程序
- picovoice/**********.ppn ，如采用picovoice方案训练自己的唤醒词，需要将训练后的ppn文件，放在picovoice文件夹下，并在config.ini配置文件中，正确引用。

#### 2、安装依赖包和依赖软件
- 在项目根目录下执行：pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

#### 3、把config.ini配置文件的信息补齐
- OpenAI官方的API接口和Azure版本的OpenAI接口均支持，如果均由配置会优先使用OpenAI官方的接口。
- Openai目录下 openai_api_key 配置为从OpenAI获取的Key，必须以sk-开头。
- Azureopenai 目录下的 openai_api_base 为Azure下的终结点，如：https://********.openai.azure.com/
- Azureopenai 目录下的 openai_api_key 为Azure下Openai的秘钥。
- Azureopenai 目录下的 gpt35_deployment_name 为Azure下Openai的gpt3部署名称。
- AzureSpeech 目录下的 AZURE_API_KEY 为 Azure 语音服务的key。
- AzureSpeech 目录下的 AZURE_REGION  为Azure 语音服务的区域，如：eastasia。
- Wakeword 目录下的 WakeUpScheme 为唤醒词的方案配置，Windows只能采用Picovoice的方案，MacOS和Linux系统可以用Picovoice和Snowboy两种方案，默认为Picovoice方案。WakeUpScheme可选值有：Picovoice和 Snowboy
- Wakeword 目录下的 Picovoice_Api_Key在Windows下为必选，在 https://picovoice.ai/ 注册登录获取。
- Wakeword 目录下的 Picovoice_Model_Path 为在picovoice官网训练下载到的唤醒词文件相对路径，可留空。留空时可以用以下词汇唤醒：'picovoice', 'hey barista', 'ok google', 'porcupine', 'pico clock', 'blueberry', 'terminator', 'hey siri', 'grapefruit', 'hey google', 'jarvis', 'computer', 'alexa', 'grasshopper', 'americano', 'bumblebee'.
- Wakeword 目录下的 Snowboy_Model_Path 为snowboy唤醒词模型的文件路径，如：snowboy/resources/models/snowboy.umdl，这里是相对路径。
- Wakeword 目录下的 Sensitivity 为唤醒词的灵敏度，同时适用于Picovoice和Snowboy两种方案。。

#### 4、Windows环境使用Azure的语音接口
Windows环境使用Azure的语音接口需要安装 Microsoft Visual C++ ，在[此页面](https://learn.microsoft.com/zh-cn/cpp/windows/latest-supported-vc-redist?view=msvc-170&preserve-view=true)下载并安装，可能需要重启。

#### 5、编译snowboy的文件（Windows环境不需要）
这一步非常重要，请按照[snowboy官方项目](https://github.com/Kitt-AI/snowboy/blob/master/README_ZH_CN.md)中的说明，编译生成 _ snowboydetect.so 文件后，将此文件复制粘贴到本项目的 snowboy 文件夹下。

#### 6、snowboy自定义唤醒词（Windows环境不需要）
- snowboy/resources/models，文件下包含所有的snowboy官方的唤醒词模型。
- 如果你想训练自己的唤醒词，可以在[此网站](https://snowboy.jolanrensen.nl/)训练生成。训练过程也很简单，录制三段录音并上传，训练成功后，会生成一个pmdl文件， 将此文件放在snowboy/resources/models目录下。
- 在config.ini配置文件的[Snowboy]部分，Snowboy_Model_Path为唤醒词模型文件的路径，修改此处就可以修改为不同的唤醒词模式。
- Sensitivity 值为唤醒词的灵敏度，取值范围为0到1，越接近0越需要准确的读取唤醒词，太低可能会比较难唤醒。越接近1越容易被唤醒，但是太高可能会误唤醒。


#### 7、完善robot_info.json配置文件
- 本项目的支持多个身份的智能助手，只需要在robot_info.json文件中配置即可，默认的智能助理是xiaozhushou，如需修改默认的智能助手，可以在main.py中的 robot_model(self,robot_id="xiaozhushou") 函数中修改。
- "username":"You",——和智能助手会话人的名称或姓名，用于以此来呈现和保存会话记录。
- "robot_id":"xiaozhushou",——智能助手的id，用于进行智能助手的配置和切换。
- "robot_name":"小助手",——智能助手的名称，用于以此来显示会话记录。
- "robot_keyword":"智能助手模式",——切换到此智能助手的关键词，在会话过程中如果包含此关键词，就会切换到此智能助手。
- "robot_describe":"一个智能助手",——智能助手的描述，切换到此智能助手时，显示此智能助手的简单介绍。
- "robot_voice_name":"zh-CN-XiaochenNeural",——智能助手的嗓音名称，嗓音是智能助手最外显的一个特征，使用的是Azure的接口，可用嗓音见[链接1](https://learn.microsoft.com/zh-cn/azure/cognitive-services/speech-service/language-support?tabs=tts) ,[链接2](https://speech.azure.cn/portal/voicegallery)。
- "robot_reply_word":"嗯，你好！",——唤醒智能助手后的，智能助手打招呼的内容。
- "robot_system_content":"你是一个有用的智能助手"——作为一个有身份的智能助手，这里是请求ChatGPT接口时，定义的system。更多身份的prompt可以见[此项目](https://github.com/PlexPt/awesome-chatgpt-prompts-zh/blob/main/prompts-zh-TW.json)

## 项目待办

