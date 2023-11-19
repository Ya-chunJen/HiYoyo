# -*- coding: utf-8 -*-
import os,json,sys,configparser
import oss2

workdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(workdir)

config = configparser.ConfigParser()
config.read(os.path.join(workdir, "config.ini"),encoding="UTF-8")
configsection = config['aliyunoss']

# 从配置文件中读取信息
AccessKey = configsection["AccessKey"]
AccessScret = configsection["AccessScret"]
bucketname = configsection["bucketname"]
bucketdomain = configsection["bucketdomain"]

# 阿里云账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM用户进行API访问或日常运维，请登录RAM控制台创建RAM用户。
auth = oss2.Auth(AccessKey, AccessScret)

# yourEndpoint填写Bucket所在地域对应的Endpoint。以华东1（杭州）为例，Endpoint填写为https://oss-cn-hangzhou.aliyuncs.com。
# 填写Bucket名称。
bucket = oss2.Bucket(auth, 'https://oss-cn-hangzhou.aliyuncs.com', bucketname)

# 必须以二进制的方式打开文件。
# 填写本地文件的完整路径。如果未指定本地路径，则默认从示例程序所属项目对应本地路径中上传文件。

def upfile(file_path,file_dir):
    with open(file_path, 'rb') as fileobj:
        # Seek方法用于指定从第1000个字节位置开始读写。上传时会从您指定的第1000个字节位置开始上传，直到文件结束。
        fileobj.seek(0, os.SEEK_SET)
        # Tell方法用于返回当前位置。
        current = fileobj.tell()
        file_name = file_path.split("/", )[-1]  #根据文件路径获取文件名和后缀，仅适用于Mac

        # 填写Object完整路径。Object完整路径中不能包含Bucket名称。
        bucket.put_object(file_dir+'/'+file_name,fileobj)
        return bucketdomain + file_dir + '/' + file_name

if __name__ == '__main__':
    if len(sys.argv) > 1:
        print(upfile(sys.argv[1],sys.argv[2]))