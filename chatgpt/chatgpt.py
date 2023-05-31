import os
import openai
import sys
import configparser

config = configparser.ConfigParser()
config.read(os.path.join(os.getcwd(), "config.ini"))

class OpenAiChatGPT:
    def __init__(self):
        openai.api_key = config['Openai']['openai_api_key']
        if openai.api_key == "sk-":
            openai.api_type = "azure"
            openai.api_version = "2023-03-15-preview"
            openai.api_base = config['Azureopenai']['openai_api_base']
            openai.api_key = config['Azureopenai']['openai_api_key']
            self.gpt35_model = config['Azureopenai']['gpt35_deployment_name']
        else:
            self.gpt35_model = "gpt-3.5-turbo"

    def chat(self,prompt_messages,model=None):
        if model is None:
            model = self.gpt35_model
        try:
            completion = openai.ChatCompletion.create(
                engine = model,
                messages=prompt_messages,
                temperature=0.8
                )
            response_message = completion.choices[0].message
            # print(response_message)
            return response_message
        except openai.error.RateLimitError:
            response_message = {
                "role": "assistant",
                "content": "抱歉，服务器繁忙，请稍后重试!"
                }
            # print(response_message)
            return response_message

if __name__ == '__main__':
    if len(sys.argv) > 1:
        prompt = sys.argv[1]
        if len(sys.argv) == 2:
            system = "You are a helpful assistant"
        if len(sys.argv) == 3:
            system = sys.argv[2]
        messages=[{"role":"system","content": system},{"role": "user", "content":prompt}]
        azure_openai = OpenAiChatGPT()
        post_message = azure_openai.chat(messages)["content"]
        print(post_message)