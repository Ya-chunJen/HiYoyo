# Hiyoyo基于LLM的智能音箱
一个基于OpenAI等LLM（Chatgpt或文心一言）的智能音箱项目，可以运行在主流操作系统上（如Windows、MacOS、Linux甚至树莓派、香橙派这些单板机上），不同操作系统的唤醒词方案可能不尽相同。

本项目的灵感来源于以下项目，并在初期核心参考了次项目：

https://github.com/MedalCollector/Orator

本项目同以上项目的不同点在于：
1. 唤醒词方案兼容了[snowboy的方案](https://github.com/Kitt-AI/snowboy/blob/master/README_ZH_CN.md)；
2. 支持多个「智能语音角色」并且支持平顺切换，对话时只需要说出包含 robot_info.json 中不同「智能语音角色」的关键词就可以，如：占卜算命模式、儿童陪伴模式、英语口语学习模式；
3. 本项目通过LLM的Function的功能，支持为「智能语音角色」配置一个或多个函数功能，让「智能语音角色」不仅有回答问题的能力，还能让其通过调用函数「动」起来，如发送邮件、驱动电机等。


## 项目待办
- ~~接入Edge-TTS~~
- ~~函数调用支持调用硬件~~

## 特别注意
- snowboy方案有点复杂，对环境要求高，所以推荐用picovoice方案，其无需自己训练自己唤醒词，直接用picovoice提供的默认唤醒词就可以，比如：'picovoice', 'hey barista', 'ok google', 'porcupine', 'pico clock', 'blueberry', 'terminator', 'hey siri', 'grapefruit', 'hey google', 'jarvis', 'computer', 'alexa', 'grasshopper', 'americano', 'bumblebee'。
- Windows环境不需要关注任何snowboy相关的内容，做好picovoice的配置即可。
- 其他操作系统可以在 picovoice或snowboy 两个方案之前进行选择，推荐使用picovoice方案。

## 视频演示
- 暂无

## 基本实现原理
1. 使用picovoice或snowboy方案，调用音频输入设备持续进行关键词的监听；
2. 监听到唤醒词后，调用Azure的语音转文字接口，将听到的内容转为文字；
3. 将获取到的文字，调用LLM的接口，获取返回结果；
4. 调用Azure的文字转语音接口，将LLM的文字结果转为音频进行输出；
5. 如果持续进行对话，从第3点开始循环，如没有监听到任何内容，进入睡眠状态等待唤醒词。

## 安装部署要求
#### 1、硬件要求
- 在Windows、M1芯片的Mac上、X86的Linux上、香橙派上均测试成功。
- 目前程序还不支持分开指定音频输入和输出设备，所以最好配备一个同时支持麦克风和扬声器的音频设备（带麦克风的耳机也是可以的），并且最好是USB的连接方式而不是蓝牙的连接方式。——如果遇到奇奇怪怪的错误，最好先检查一下音频输入和输出设备。

#### 2、软件要求
- Python3环境。
- 安装pyaudio。
- 使用snowboy项目编译「_ snowboydetect.so」文件时,需要安装比较的软件，请按snowboy项目的说明操作。——这一点可能是最大的障碍点。（Windows环境不需要。）

#### 3、账号需求
- Openai的Api或者Azure版本Openai的Api，或者文心一言的Api
- Azure的语音相关Api
- Picovoice的KEY，在 https://picovoice.ai/ 注册登录后获取。（建议全部用次方案，Windows环境必须。）

## 使用步骤
#### 1. clone本项目到本地


#### 2. 安装依赖包和依赖软件
在项目根目录下执行：pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

#### 3、创建config.ini配置文件的信息补齐
- 复制 config_example.ini 文件，并将文件名改为config.ini。
- [AI] 目前下的「aimanufacturer」表示使用哪家厂商的LLM，openai表示OpenAi（包含AuzreOpenai）,erniebot表示百度的文心一言，目前只支持此两家。
- OpenAI官方的API接口和Azure版本的OpenAI接口均支持，如果均配置会优先使用OpenAI官方的接口。
- [Openai]目录下 openai_api_key 配置为从OpenAI获取的Key，必须以sk-开头。
- [Azureopenai] 目录下的 openai_api_base 为Azure下的终结点，如：https://********.openai.azure.com/
- [Azureopenai] 目录下的 openai_api_key 为Azure下Openai的秘钥。
- [Azureopenai] 目录下的 gpt35_deployment_name 为Azure下Openai的gpt3部署名称。
- [AzureSpeech] 目录下的 AZURE_API_KEY 为 Azure 语音服务的key。
- [AzureSpeech] 目录下的 AZURE_REGION  为Azure 语音服务的区域，如：eastasia。
- [baiduernie] 目录下的 AppID、ApiKey 、keySecret分别为百度文心一言的应用信息。
- [baiduernie] 目录下的 ErnieApiVersion 为百度文心一言的的版本。
- [AzureSpeech] 目录下的 AZURE_API_KEY、AZURE_REGION分别为微软语音服务的key和区域。
- [Wakeword] 目录下的 WakeUpScheme 为唤醒词的方案配置，Windows只能采用Picovoice的方案，MacOS和Linux系统可以用Picovoice和Snowboy两种方案，默认为Picovoice方案。WakeUpScheme可选值有：Picovoice和 Snowboy
- [Wakeword] 目录下的 Picovoice_Api_Key在Windows下为必选，在 https://picovoice.ai/ 注册登录获取。
- [Wakeword] 目录下的 Picovoice_Model_Path 为在picovoice官网训练并下载到的唤醒词文件名，将其放在picovoice目录下。Picovoice_Model_Path 可留空。留空时可以用以下词汇唤醒：'picovoice', 'hey barista', 'ok google', 'porcupine', 'pico clock', 'blueberry', 'terminator', 'hey siri', 'grapefruit', 'hey google', 'jarvis', 'computer', 'alexa', 'grasshopper', 'americano', 'bumblebee'。
- [Wakeword] 目录下的 Snowboy_Model_Path 为snowboy唤醒词模型的文件路径，如：resources/models/snowboy.umdl。
- [Wakeword] 目录下的 Sensitivity 为唤醒词的灵敏度，同时适用于Picovoice和Snowboy两种方案。
- 其他配置项，用于插件之中，非必须。

## 文件目录说明及用途
#### 1、主目录的文件及用途
- main.py，程序的主文件。
- main_text.py,另一个程序的主文件，可以在终端中以文本的形式进行对话（不需要声音的输入和输出）。
- config_example.ini，配置文件信息，用于存放需要调用一些接口的key信息，完成配置后，需要将文件名改为config.ini
- robot_info.json，「智能语音角色」的配置信息，理论上可以配置无限多个，相当于你有无限多个「智能语音角色」。下文详述。

#### 2、「智能语音角色」robot_info.json文件配置说明
- 本项目的支持多个身份的「智能语音角色」，只需要在robot_info.json文件中配置即可，默认的智能助理是xiaozhushou，如需修改默认的「智能语音角色」，可以在main.py中的 robot_model(self,robot_id="xiaozhushou") 函数中修改。
- "username":"You",——和「智能语音角色」会话人的名称或姓名，用于以此来呈现和保存会话记录。
- "robot_id":"xiaozhushou",——「智能语音角色」的id，用于进行「智能语音角色」的配置和切换，不能为中文字符。
- "robot_name":"小助手",——「智能语音角色」的名称，用于以此来显示会话记录。
- "robot_keyword":"小助手模式模式",——切换到此「智能语音角色」的关键词，在会话过程中识别到的语音如果包含此关键词，就会切换到此「智能语音角色」。
- "robot_describe":"默认模式，一个智能小助手",——「智能语音角色」的描述，切换到此「智能语音角色」时，显示此「智能语音角色」的简单介绍。
- "robot_voice_name":"zh-CN-XiaochenNeural",——「智能语音角色」的嗓音名称，嗓音是「智能语音角色」最外显的一个特征，使用的是Azure的接口，可用嗓音见[链接1](https://learn.microsoft.com/zh-cn/azure/cognitive-services/speech-service/language-support?tabs=tts) ,[链接2](https://speech.azure.cn/portal/voicegallery)。
- "robot_reply_word":"嗯，你好！",——唤醒「智能语音角色」后的，「智能语音角色」打招呼的内容。
- "robot_system_content":"你的名字叫Yoyo，是一个语音智能助手。和我对话时，回答字数控制在100个字以内。"——作为一个有身份的「智能语音角色」，这里是请求LLM接口时，定义的system。更多身份的prompt可以见[此项目](https://github.com/PlexPt/awesome-chatgpt-prompts-zh/blob/main/prompts-zh-TW.json)
- "robot_function_model":"["none"]"，——这个「智能语音角色」可以使用的插件，插件是在functonplugin/functionpluginlist.json文件中定义的。["none"]表示不使用任何插件，["auto"]是使用全部插件（不推荐使用，所有插件在一起的内容太多），想使用哪一个插件，就写插件的name。支持一个「智能语音角色」同时调用多个插件，以["sendemail","posttoqw"] 数组的形式提供提供插件的name即可。

#### 3、chatgpt目录文件及用途
- chatgpt/chatgptsingle.py，不论Openai官方版本还是Azrue版本的单轮请求程序。
- chatgpt/chatgptfunction.py，用于执行chatgpt的函数调用。
- chatgpt/chatgptmult.py，用于存储保留多轮会话的chatgpt程序。

#### 4、erniebot目录文件及用途
- 同chatgpt目录文件及用途相似，仅是更换为百度文心一言的接口。
- erniebot/erniebotsingle.py，单轮会话请求程序。
- erniebot/erniebotfunction.py，用于执行函数调用的程序。
- erniebot/erniebotmult.py，用于存储保留多轮会话的程序。

#### 5、functionplugin目录文件及用途
- functionpluginlist.json是插件的配置文件，参数要求可参考openai的官方文档：[关于Function Call](https://platform.openai.com/docs/guides/gpt/function-calling) 。
- 百度文心一言的插件格式和openai的插件格式，基本一样。
- 开发的插件，应该放在unctionplugin目录下；
- 插件应该返回标准额JSON格式数据，如{"request_gpt_again":False,"details":f"已将消息推送到企业微信群。"}，其中：request_gpt_again代表，是否在插件执行完后，再请求一次LLM，为布尔型数据。details代表，插件返回的详细信息，如需要再请求一次LLM就是给LLM传递的信息，如不需要再请求一次LLM，就是直接给终端用户的信息；
- 插件名称、插件对应的程序模块、程序模块中的函数都必须使用完全一致的名称。（这是为了方便的调用模块）
- 插件程序模块中的函数只能接受function_args这一个参数，且这个参数是json类型，更多参数可以写在字典内部。

#### 6、log目录文件及用途
- log文件夹，用于存储多轮会话的文件，每个会话人就是一个json文件，会话人的名称就是robot_info.json配置信息中的username。

#### 7、picovoice目录文件及用途
- picovoice/wakeword.py，picovoice方案的唤醒词程序。
- picovoice/**********.ppn ，如采用picovoice方案训练自己的唤醒词，需要将训练后的ppn文件，放在picovoice文件夹下，并在config.ini配置文件中，正确引用。

#### 8、snowboy目录文件及用途
- snowboy方案较为复杂，需要进行编译：按照[snowboy官方项目](https://github.com/Kitt-AI/snowboy/blob/master/README_ZH_CN.md)中的说明，编译生成 _ snowboydetect.so 文件后，将此文件复制粘贴到本项目的 snowboy 文件夹下。
- snowboy/wakeword.py，snowboy唤醒词程序
- snowboy/snowboydecoder.py，snowboy相关程序，不需要修改
- snowboy/snowboydetect.py，snowboy相关程序，不需要修改
- snowboy/_ snowboydetect.so，这个程序需要自己编译，这个文件非常重要，请按照下面的步骤一步步操作
- snowboy/resources/common.res，snowboy的资源文件，不要修改就可以
- snowboy/resources/models，文件下的umdl文件和pmdl文件，是唤醒词模型文件，需要使用哪个唤醒词就需要在config.ini中引用哪一个文件

> snowboy自定义唤醒词
> - snowboy/resources/models，文件下包含所有的snowboy官方的唤醒词模型。
> - 如果你想训练自己的唤醒词，可以在[此网站](https://snowboy.jolanrensen.nl/)训练生成。训练过程也很简单，录制三段录音并上传，训练成功后，会生成一个pmdl文件， 将此文件放在snowboy/resources/models目录下。
> - 在config.ini配置文件的[Snowboy]部分，Snowboy_Model_Path为唤醒词模型文件的路径，修改此处就可以修改为不同的唤醒词模式。
> - Sensitivity 值为唤醒词的灵敏度，取值范围为0到1，越接近0越需要准确的读取唤醒词，太低可能会比较难唤醒。越接近1越容易被唤醒，但是太高可能会误唤醒。

#### 9、speechmodules目录文件及用途
- speechmodules/speech2text.py，语音转文字功能程序
- speechmodules/text2speech.py，文字转语音功能程序
- speechmodules/text2speechedge.py，文字转语音功能程序，采用Edge_tts的方案，不需要API。此语音方案，需要先把生成的语音文件保存为文件，然后在读取文件并播放。
- speechmodules/text2speechedgev2.py，文字转语音功能程序，采用Edge_tts的方案，不需要API。此方案，不需要讲生成的语音保存为文件，而是可以直接讲音频字节流，进行播放，但是每段音频开头都有一个爆破音。
- speechmodules/tepfile ,存放临时语音文件的文件夹。但是程序再播放语音文件后，会自动删除语音文件。

> 提示：Windows环境使用Azure的语音接口需要安装 Microsoft Visual C++ ，在[此页面](https://learn.microsoft.com/zh-cn/cpp/windows/latest-supported-vc-redist?view=msvc-170&preserve-view=true)下载并安装，可能需要重启。

## 部署
1. 在Windows环境，可以将程序启动放在一个bat文件中，bat文件中有如下内容：
```
@echo off
cd /d D:\gitee\HiYoyo
rem 「D:\gitee\HiYoyo」为项目文件目录，需要根据你的目录进行修改
python3 main.py
```

2. 在MacOS环境，可以将程序放在一个sh文件中，并可更改为双击启动：
```
#!/bin/bash
cd /Users/renyajun/gitee/HiYoyo && python3 main.py  # /Users/renyajun/gitee/HiYoyos是项目目录，需要根据你的目录进行修改
```
（1）将此.sh文件的后缀修改为.command
（2）给这个.command授予权限：sudo chmod 777 "文件路径"
（2）右键「制作替身」，把创建的替身文件放在桌面，并可重命名
（3）双击桌面的替身文件，即可启动程序。

3. Linux环境，可以将程序制作成一个开机启动的服务：
```
(1)创建一个.service文件：
sudo nano /etc/systemd/system/hiyoyo.service
(2)在打开的文件中，输入以下内容：
[Unit]
Description= kaijiqidonghiyoyo
After=multi-user.target
[Service]
Type=simple
WorkingDirectory=/home/orangepi/HiYoyo
ExecStart=/usr/bin/python3 /home/orangepi/HiYoyo/main.py
Restart=on-abort
[Install]
WantedBy=multi-user.target
（3）、注意，在上面的代码中需要修改以下内容：
- Description：服务的描述
- WorkingDirectory：项目文件目录，需要根据你的目录进行修改
- ExecStart：main.py所在的绝对路径
- WantedBy：服务所依赖的multi-user.target
（4）使用命令
# 保存文件并刷新systemd：
sudo systemctl daemon-reload
# 启用服务：
sudo systemctl enable hiyoyo.service
# 启动服务
sudo systemctl start hiyoyo.service
# 查看服务状态：
sudo systemctl status hiyoyo.service
# 停止服务：
sudo systemctl stop hiyoyo.service
```