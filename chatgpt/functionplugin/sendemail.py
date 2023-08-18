import os
import smtplib
import json
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
import configparser

config = configparser.ConfigParser()
config.read(os.path.join(os.getcwd(), "config.ini"),encoding="UTF-8")
configsection = config['QQsmtp']

def send(mail_to,mail_subject,message):
    # 这是一个封装后的公共函数，第一个参数是发送的目标对象，第二个对象是邮件主题，第三参数邮件纯文本、html格式、附件等格式邮件在各自函数封装后传递的值，所以在本函数中值定义From\to\Subject即可
    sender = configsection['sender']
    password = configsection['password']
    message['From'] = Header(sender) #定义邮件发送者的显示信息
    message['To'] =  Header(mail_to)  #定义邮件接受者的显示信息
    message['Subject'] = Header(mail_subject, 'utf-8') #定义邮件的主题

    smtpobj = smtplib.SMTP_SSL("smtp.qq.com",465) #链接邮件服务器
    smtpobj.ehlo()
    smtpobj.login(sender,password) # type: ignore #登录邮箱
    smtpobj.sendmail(sender,mail_to,message.as_string()) #发送邮件
    smtpobj.quit() #退出邮箱

contacts = [
    {'name':"张三",'email':"zhangsan@qq.cn"},
    {'name':"李四",'email':"lisi@qq.cn"}
]

def sendemail(function_args):
    # mailcontent = json.loads(mailcontent)
    mail_to_name = function_args['mail_to_name']

    contact_names = [contact['name'] for contact in contacts]
    if mail_to_name not in contact_names:
        callback_json =  {"request_gpt_again":False,"details":f"在你的联系人列表中没有找到{mail_to_name}"}
        return json.dumps(callback_json)
    else:
        for contact in contacts:
            if contact['name'] == mail_to_name:
                mail_to_address  = contact['email']
                break

    mail_subject = function_args['mail_subject']
    mail_body_text = function_args['mail_body_text']

    # 定义发送纯文本的邮件
    message = MIMEText(mail_body_text, 'plain', 'utf-8')  #构建纯文本邮件的内容
    send(mail_to_address,mail_subject,message) # 调用公共发送函数
    callback_json =  {"request_gpt_again":False,"details":f"已将主题为《{mail_subject}》的邮件发送给了：{mail_to_name}。"}
    return json.dumps(callback_json)

if __name__ == '__main__':
    message_body = """{
        "mail_to_name":"张三",
        "mail_subject":"我已安全到家！",
        "mail_body_text":"我已安全到家，勿念。"
    }
    """
    sendemail(message_body)