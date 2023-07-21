from encodings import utf_8
import os
import smtplib
import sys
import time
import json
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
import markdown
import configparser
config = configparser.ConfigParser()
config.read(os.path.join(os.getcwd(), "config.ini"),encoding="UTF-8")
configsection = config['QQsmtp']


def send(mail_to,mail_subject,message):
    # 这是一个封装后的公共函数，第一个参数是发送的目标对象，第二个对象是邮件主题，第三参数邮件纯文本、html格式、附件等格式邮件在各自函数封装后传递的值，所以在本函数中值定义From\to\Subject即可
    # sender = configsection['sender'] #邮件发送者
    # password = configsection['password'] #秘钥
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

def sendemail(mailcontent):
    mailcontent = json.loads(mailcontent)
    mail_to = mailcontent['mail_to']
    mail_subject = mailcontent['mail_subject']
    mail_body_text = mailcontent['mail_body_text']
    # 定义发送纯文本的邮件
    message = MIMEText(mail_body_text, 'plain', 'utf-8')  #构建纯文本邮件的内容
    send(mail_to,mail_subject,message) # 调用公共发送函数
    callback_json =  {"request_gpt_again":False,"details":f"已将主题为《{mail_subject}》的邮件发送给{mail_to}。"}
    return callback_json