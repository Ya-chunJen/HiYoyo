import wiringpi
import time
import json

wiringpi.wiringPiSetupPhys()   #设置GPIO编号为物理编码方式。
# wiringpi.wiringPiSetup()        #设置GPIO编号为wPi方式。

A_ENA = 22
A_IN1 = 24
A_IN2 = 26

B_ENA = 19
B_IN3 = 21
B_IN4 = 23

wiringpi.pinMode(A_ENA,1) 
wiringpi.pinMode(A_IN1,1) 
wiringpi.pinMode(A_IN2,1) 

wiringpi.pinMode(B_ENA,1) 
wiringpi.pinMode(B_IN3,1) 
wiringpi.pinMode(B_IN4,1)

def stop():
	wiringpi.digitalWrite(A_IN1,0)
	wiringpi.digitalWrite(A_IN2,0)
	wiringpi.digitalWrite(B_IN3,0)
	wiringpi.digitalWrite(B_IN4,0)

def forward(speed=60,duration=5):
	wiringpi.softPwmCreate(A_ENA,0,speed)
	wiringpi.softPwmCreate(B_ENA,0,speed)
	wiringpi.digitalWrite(A_IN1,0)
	wiringpi.digitalWrite(A_IN2,1)
	wiringpi.digitalWrite(B_IN3,0)
	wiringpi.digitalWrite(B_IN4,1)
	time.sleep(duration)
	stop()

def backup(speed=60,duration=5):
	wiringpi.softPwmCreate(A_ENA,0,speed)
	wiringpi.softPwmCreate(B_ENA,0,speed)
	wiringpi.digitalWrite(A_IN1,1)
	wiringpi.digitalWrite(A_IN2,0)
	wiringpi.digitalWrite(B_IN3,1)
	wiringpi.digitalWrite(B_IN4,0)
	time.sleep(duration)
	stop()
	
def turnleft(speed=60,duration=2):
	wiringpi.softPwmCreate(A_ENA,0,speed)
	wiringpi.softPwmCreate(B_ENA,0,speed)
	wiringpi.digitalWrite(A_IN1,0)
	wiringpi.digitalWrite(A_IN2,0)
	wiringpi.digitalWrite(B_IN3,0)
	wiringpi.digitalWrite(B_IN4,1)
	time.sleep(duration)
	stop()
	
def turnright(speed=60,duration=2):
	wiringpi.softPwmCreate(A_ENA,0,speed)
	wiringpi.softPwmCreate(B_ENA,0,speed)
	wiringpi.digitalWrite(A_IN1,0)
	wiringpi.digitalWrite(A_IN2,1)
	wiringpi.digitalWrite(B_IN3,0)
	wiringpi.digitalWrite(B_IN4,0)
	time.sleep(duration)
	stop()
	
def circle(speed=60,duration=5):
	wiringpi.softPwmCreate(A_ENA,0,speed)
	wiringpi.softPwmCreate(B_ENA,0,speed)
	wiringpi.digitalWrite(A_IN1,1)
	wiringpi.digitalWrite(A_IN2,0)
	wiringpi.digitalWrite(B_IN3,0)
	wiringpi.digitalWrite(B_IN4,1)
	time.sleep(duration)
	stop()

def tanktest(function_args):
    action = function_args["action"]
    print(action)
    exec(f"{action}()")
    callback_json = {"request_gpt_again":False,"details":"已执行。"} 
    return json.dumps(callback_json)

if __name__ == '__main__':
    action = input("要执行的动作：")
    exec(f"{action}()")