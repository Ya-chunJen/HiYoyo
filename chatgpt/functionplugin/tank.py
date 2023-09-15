import wiringpi
import time
import json

wiringpi.wiringPiSetupPhys()   #设置GPIO编号为物理编码方式。
# wiringpi.wiringPiSetup()        #设置GPIO编号为wPi方式。

def left_motor(direction=0,speed=100):
	# direction为0是停转，为1是正转，为2是反转。
	B_ENA,B_IN3,B_IN4 = 22,24,26
	wiringpi.pinMode(B_ENA,1)
	wiringpi.softPwmCreate(B_ENA, 0, 100) 
	wiringpi.pinMode(B_IN3,1) 
	wiringpi.pinMode(B_IN4,1)   
	if direction == 0:
		wiringpi.digitalWrite(B_IN3,0)
		wiringpi.digitalWrite(B_IN4,0)
	elif direction == 1:
		wiringpi.softPwmWrite(B_ENA, speed)
		wiringpi.digitalWrite(B_IN3,0)
		wiringpi.digitalWrite(B_IN4,1)
	elif direction == 2:
		wiringpi.softPwmWrite(B_ENA, speed)
		wiringpi.digitalWrite(B_IN3,1)
		wiringpi.digitalWrite(B_IN4,0)

def right_motor(direction=0,speed=100):
	A_ENA,A_IN1,A_IN2 = 19,21,23
	wiringpi.pinMode(A_ENA,1)
	wiringpi.softPwmCreate(A_ENA, 0, 100)
	wiringpi.pinMode(A_IN1,1) 
	wiringpi.pinMode(A_IN2,1)
	if direction == 0:
		wiringpi.digitalWrite(A_IN1,0)
		wiringpi.digitalWrite(A_IN2,0)
	elif direction == 1:
		wiringpi.softPwmWrite(A_ENA, speed)
		wiringpi.digitalWrite(A_IN1,1)
		wiringpi.digitalWrite(A_IN2,0)
	elif direction == 2 :
		wiringpi.softPwmWrite(A_ENA, speed)
		wiringpi.digitalWrite(A_IN1,0)
		wiringpi.digitalWrite(A_IN2,1)

def stop():
	left_motor(0)
	right_motor(0)

def forward(speed=100,duration=2):
	left_motor(1,speed)
	right_motor(1,speed)
	time.sleep(duration)
	stop()

def backup(speed=100,duration=2):
	left_motor(2,speed)
	right_motor(2,speed)
	time.sleep(duration)
	stop()
	
def turnleft(speed=100,duration=0.3):
	left_motor(0)
	right_motor(1,speed)
	time.sleep(duration)
	stop()
	
def turnright(speed=100,duration=0.3):
	left_motor(1,speed)
	right_motor(0)
	time.sleep(duration)
	stop()
	
def circle(speed=100,duration=1):
	left_motor(1)
	right_motor(2)
	time.sleep(duration)
	stop()

def tank(function_args):
    action = function_args["action"]
    duration = function_args["duration"]
	#print(action)
    exec(f"{action}(duration={duration})")
    callback_json = {"request_gpt_again":False,"details":"OK"} 
    return json.dumps(callback_json)

def loop():
	while True:
		print("1为前进，2为后退，3为左转，4为右转，5为转圈，6为停止。")
		actionstr = input("要执行的动作：")
		actionindex = int(actionstr)
		#speed = int(input("速度百分比："))
		speed = 100
		duration = float(input("运行时间"))
		action = ''
		if actionindex == 1:
			action = "forward"
		elif actionindex == 2:
			action = "backup"
		elif actionindex == 3:
			action = "turnleft"
		elif actionindex == 4:
			action = "turnright"
		elif actionindex == 5:
			action = "circle"
		elif actionindex == 6:
			action = "stop"
		else:
			action = actionstr

		exec(f"{action}({speed},{duration})")

if __name__ == '__main__':
    # left_motor(1)
    # right_motor(1)
    #time.sleep(3)
    # stop()
    loop()