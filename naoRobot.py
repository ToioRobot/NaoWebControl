import sys
import time
import socket
import sys
import math
import almath
import thread
import time
from optparse import OptionParser

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

from unicode_tools import *
from avoidance_module import *
from MP3_Player import *
from touch_password import *
from leds import *
from video_module import *
from ChatRobot import *

# <----------------- socket port ---------------->
LISTEN_PORT = 8001
VIDEO_SERVER_PORT = 8003
# <-------------------------------------------------------------> Command

COMMAND_WAKEUP = 'WAKEUP'
COMMAND_REST = 'REST'
COMMAND_FORWARD = 'FORWARD'
COMMAND_BACK = 'BACK'
COMMAND_LEFT = 'LEFT'
COMMAND_RIGHT = 'RIGHT'
COMMAND_STOP = 'STOP'
COMMAND_TURNLEFT = 'TURNLEFT'
COMMAND_TURNRIGHT = 'TURNRIGHT'
COMMAND_DISCONNECT = 'DISCONNECT'

COMMAND_HEADYAW = 'HEADYAW'
COMMAND_HEADPITCH = 'HEADPITCH'

COMMAND_SENSOR = 'SENSOR'

COMMAND_ARMREST = 'ARMREST'
COMMAND_LARMOPEN = 'LARMOPEN'
COMMAND_LARMCLOSE = 'LARMCLOSE'
COMMAND_LARMUP = 'LARMUP'
COMMAND_LARMDOWN = 'LARMDOWN'
COMMAND_RARMOPEN = 'RARMOPEN'
COMMAND_RARMCLOSE = 'RARMCLOSE'
COMMAND_RARMUP = 'RARMUP'
COMMAND_RARMDOWN = 'RARMDOWN'

COMMAND_SAY = 'SAY'

COMMAND_POSTURE_STAND = 'POSTURE_STADN'
COMMAND_POSTURE_MOVEINIT = 'POSTURE_STADNINIT'
COMMAND_POSTURE_STANDZERO = 'POSTURE_STADNZERO'
COMMAND_POSTURE_CROUCH = 'POSTURE_CROUCH'
COMMAND_POSTURE_SIT = 'POSTURE_SIT'
COMMAND_POSTURE_SITRELAX = 'POSTURE_SITRELAX'
COMMAND_POSTURE_LYINGBELLY = 'POSTURE_LYINGBELLY'
COMMAND_POSTURE_LYINGBACK = 'POSTURE_LYINGBACK'

COMMAND_POSTURE_RECORD = 'POSTURE_RECORD'
COMMAND_POSTURE_RECORD_STOP = 'POSTURE_RECORD_STOP'
COMMAND_POSTURE_CUSTOMER = 'POSTURE_CUSTOMER'
COMMAND_POSTURE_DELETE = 'POSTURE_DELETE'

COMMAND_OBSTACLE = 'OBSTACLE'

COMMAND_MUSIC_ON 	= 'MUSIC_ON'
COMMAND_MUSIC_OFF 	= 'MUSIC_OFF'
COMMAND_MUSIC_NEXT 	= 'MUSIC_NEXT'
COMMAND_MUSIC_PREVIOUS = 'MUSIC_PREVIOUS'
COMMAND_MUSIC_PLAY	=	'MUSIC_PLAY'
COMMAND_MUSIC_PAUSE =	'MUSIC_PAUSE'
COMMAND_MUSIC_UP	=	'MUSIC_UP'
COMMAND_MUSIC_DOWN	=	'MUSIC_DOWN'
COMMAND_MUSIC_FORWARD = 'MUSIC_FORWARD'
COMMAND_MUSIC_REWIND=	'MUSIC_REWIND'
COMMAND_MUSIC_URL	=	'MUSIC_URL'

COMMAND_VIDEO_SWITCH_CAMARA = 'SWITCH_CAMERA'


class naoRobot:
    def __init__(self,ip='127.0.0.1',port=9559):
        # <------------------------------------------------------------->
        # flag
        self.CONNECT_FLAG = False
        self.SENSOR_FLAG  = False
        self.POSTURE_RECORD_FLAG = False
        # <------------------------------------------------------------->
        self.ROBOT_IP = ip
        self.ROBOT_PORT = port

        self.connection = None
        self.POSTURE_CHANGE_SPEED = 0.8

        # naoqi proxy module
        self.tts = self.motion = self.memory = self.battery = self.autonomous = self.posture = self.sonar = None

        self.avoid = None
        self.mp3player = None
        self.touch = None
        self.video = None
        self.chatrobot = None
        self.POSTURE_CHANGE_SPEED = 0.8
        self.posture_list = {}
        self.posture_value = {}
        self.Init()
    def Init(self):
        # We need this broker to be able to construct
        # NAOqi modules and subscribe to other modules
        # The broker must stay alive until the program exists
        self.myBroker = ALBroker("myBroker",
            "0.0.0.0",   # listen to anyone
            0,           # find a free port and use it
            self.ROBOT_IP,         # parent broker IP
            self.ROBOT_PORT)       # parent broker port
        self.tts = ALProxy("ALTextToSpeech")
        try:
            self.tts.setLanguage("Italian")
        except:
            self.tts.setLanguage("English")
            print("set lang to: English")
        self.motion = ALProxy("ALMotion")
        self.posture = ALProxy("ALRobotPosture")
        self.memory = ALProxy("ALMemory")
        self.battery = ALProxy("ALBattery")
        self.sonar = ALProxy("ALSonar")
        self.leds = ALProxy("ALLeds")
        # turn ALAutonomousLife off
        try:
            self.autonomous = ALProxy("ALAutonomousLife")
            self.autonomous.setState("disabled")
        except:
            print('No Autonomous Life..')

        self.avoid = avoidance(self.ROBOT_IP, self.ROBOT_PORT)
        self.mp3player = MP3player(self.ROBOT_IP, self.ROBOT_PORT)

        #self.touch = touchPasswd("touch")
        #self.touch.setPassword('132312')
        #self.video = VideoSend(self.ROBOT_IP, self.ROBOT_PORT)
        # TopCamera:0 	/	BottomCamera:1
        # XtionCamera: 2 (optional)
        #video.addXtionCamera()
        #self.video.setCamera(0)
        #self.video.setFPS(30)
        #self.video.start()

        self.chatrobot = ChatRobot()						# Chat robot
        #chatrobot.setRobot('SIMSIMI')
        self.chatrobot.setRobot('TULING')
    def passVerify(self):
        self.touch.skipVerify()

    def stop(self):
         self.Operation(COMMAND_STOP)
         self.avoid.stop()
         #self.video.stop()
         self.mp3player.stop()
         self.myBroker.shutdown()

    def Operation(self, command, arg=''):
        ok=''
        if command == COMMAND_WAKEUP:							# wakeup
            ok=self.motion.post.wakeUp()
        elif command == COMMAND_REST:							# rest
            ok=self.motion.post.rest()
        elif command == COMMAND_FORWARD:						# forward
            ok=self.mymoveinit()
            ok=self.motion.move(0.1, 0, 0)
        elif command == COMMAND_BACK:							# back
            ok=self.mymoveinit()
            ok=self.motion.move(-0.1, 0, 0)
        elif command == COMMAND_LEFT:							# left
            ok=self.mymoveinit()
            ok=self.motion.move(0, 0.1, 0)
        elif command == COMMAND_RIGHT:							# right
            ok=self.mymoveinit()
            ok=self.motion.move(0, -0.1, 0)
        elif command == COMMAND_STOP:							# stop
            ok=self.motion.stopMove()
        elif command == COMMAND_TURNLEFT:						# turn left
            ok=self.mymoveinit()
            ok=self.motion.move(0, 0, 0.3)
        elif command == COMMAND_TURNRIGHT:						# turn right
            ok=self.mymoveinit()
            ok=self.motion.move(0, 0, -0.3)
        elif command == COMMAND_DISCONNECT:						# disconnect
            ok=self.motion.rest()
        elif command == COMMAND_HEADYAW:						# head yaw
            angles = math.radians(int(arg[0]))
            self.motion.setStiffnesses("Head", 1.0)
            ok = self.motion.setAngles("HeadYaw", angles, 0.2)
            #angles = (int(arg) - 50) * 2
            #self.motion.setStiffnesses("Head", 1.0)
            #ok = self.motion.setAngles("HeadYaw", angles * almath.TO_RAD, 0.2)
        elif command == COMMAND_HEADPITCH:						# head pitch
            angles = math.radians(int(arg[0]))
            self.motion.setStiffnesses("Head", 1.0)
            ok = self.motion.setAngles("HeadPitch", angles, 0.2)
            #angles = (int(arg) - 50)
            #self.motion.setStiffnesses("Head", 1.0)
            #ok = self.motion.setAngles("HeadPitch", angles * almath.TO_RAD, 0.2)
        elif command == COMMAND_SENSOR:							# sensor
            global SENSOR_FLAG
            if SENSOR_FLAG == False:
                SENSOR_FLAG = True
                thread.start_new_thread(self.sensor, (0.5,))    # 2nd arg must be a tuple
            else:
                SENSOR_FLAG = False
        elif command == COMMAND_ARMREST:						# arm rest
            ok=self.LArmMoveInit()
            ok=self.RArmMoveInit()
        elif command == COMMAND_LARMOPEN:						# left hand open
            ok=self.motion.post.openHand("LHand")
        elif command == COMMAND_LARMCLOSE:						# left hand close
            ok=self.motion.post.closeHand("LHand")
        elif command == COMMAND_RARMOPEN:						# Right hand open
            ok=self.motion.post.openHand("RHand")
        elif command == COMMAND_RARMCLOSE:						# Right hand close
            ok=self.motion.post.closeHand("RHand")
        elif command == COMMAND_LARMUP:							# left arm up
            self.LArmUp()
        elif command == COMMAND_LARMDOWN:						# left arm down
            self.LArmMoveInit()
        elif command == COMMAND_RARMUP:							# right arm up
            ok=self.RArmUp()
        elif command == COMMAND_RARMDOWN:						# right arm down
            ok=self.RArmMoveInit()
        elif command == COMMAND_SAY:							# say
            message=' '.join(arg)
            print('say ' + message)
            if message[0] == 'n' and message[2] == 'o' and message[4] == 'n' and message[6] == 'e':
                message = ''
            self.tts.say(message)
            ok = True
            #ok=thread.start_new_thread(self.mysay, (messages,))
        elif command == COMMAND_POSTURE_STAND:					# posture - stand
            ok=self.posture.post.goToPosture("Stand", 1.0)
            #goToPosture()
        elif command == COMMAND_POSTURE_STANDZERO:				# posture - stand zero
            ok=self.posture.post.goToPosture("StandZero", self.POSTURE_CHANGE_SPEED)
        elif command == COMMAND_POSTURE_MOVEINIT:				# posture - move init / stand init
            ok=self.posture.post.goToPosture("StandInit", self.POSTURE_CHANGE_SPEED)
        elif command == COMMAND_POSTURE_CROUCH:					# posture - Crouch
            ok=self.posture.post.goToPosture("Crouch", self.POSTURE_CHANGE_SPEED)
        elif command == COMMAND_POSTURE_SIT:					# posture - sit
            ok=self.posture.post.goToPosture("Sit", self.POSTURE_CHANGE_SPEED)
        elif command == COMMAND_POSTURE_SITRELAX:				# posture - sit relax
            ok=self.posture.post.goToPosture("SitRelax", self.POSTURE_CHANGE_SPEED)
        elif command == COMMAND_POSTURE_LYINGBELLY:				# posture - lying belly
            ok=self.posture.post.goToPosture("LyingBelly", self.POSTURE_CHANGE_SPEED)
        elif command == COMMAND_POSTURE_LYINGBACK:				# posture - lying back
            ok=self.posture.post.goToPosture("LyingBack", self.POSTURE_CHANGE_SPEED)
        elif command == COMMAND_POSTURE_RECORD:					# posture - record
            global POSTURE_RECORD_FLAG
            global posture_list
            if POSTURE_RECORD_FLAG == False:
                POSTURE_RECORD_FLAG = True
                self.record_on()
            else:
                POSTURE_RECORD_FLAG = False
                posture_name = arg
                self.record_off()
                print "Record Over:", posture_name
                posture_list[posture_name] = posture_value
        elif command == COMMAND_POSTURE_RECORD_STOP:			# posture record stop
            POSTURE_RECORD_FLAG = False
            self.motion.setStiffnesses("Body", 1.0)
            self.tts.post.say('stop record')
            self.motion.wakeUp()
            self.motion.rest()
        elif command == COMMAND_POSTURE_CUSTOMER:				# posture - customer
            posture_name = arg
            print "Posture Customer:", posture_name
            self.reappear(posture_name)
        elif command == COMMAND_POSTURE_DELETE:					# posture - record
            posture_name = arg
            print "Posture delete:", posture_name
            if posture_name in posture_list:
                del posture_list[posture_name]
                self.tts.post.say('delete customer posture.')
            else:
                self.tts.post.say('wrong posture name.')
        elif command == COMMAND_OBSTACLE:						# avoid obstacle
            global avoid
            if avoid.getflag() == False:
                self.tts.post.say('Start avoid obstacles.')
                self.avoid.start()
            else:
                self.avoid.stop()
                self.avoid = avoidance(self.ROBOT_IP, self.ROBOT_PORT)
                self.tts.post.say('Stop avoid obstacles.')
        elif command == COMMAND_MUSIC_ON:
            if self.mp3player.getFlag() == True:
                pass
            else:
                self.tts.post.say("Music!")
        elif command == COMMAND_MUSIC_OFF:
            self.mp3player.stop()
            self.tts.post.say("Stop Music!")
        elif command == COMMAND_MUSIC_PLAY:						# music play
            self.mp3player.play()
        elif command == COMMAND_MUSIC_PAUSE:					# music pause
            self.mp3player.pause()
        elif command == COMMAND_MUSIC_NEXT:						# music next song
            self.mp3player.nextSong()
        elif command == COMMAND_MUSIC_PREVIOUS:					# music previous song
            self.mp3player.previousSong()
        elif command == COMMAND_MUSIC_UP:						# music volume up
            volume = arg
            volume = int(volume) / 100.0
            if volume >= 0 and volume <= 1.00:
                self.mp3player.setVolume(volume)
        elif command == COMMAND_MUSIC_URL:						# download mp3 file
            buf = arg
            index = buf.find('http')
            filename = buf[:index]
            url = buf[index:]
            self.tts.post.say("Downloading music")
            self.mp3player.downloadMP3(filename, url)
        elif command == COMMAND_VIDEO_SWITCH_CAMARA:			# switch camera
            self.video.switchCamera()
            print 'switch Camera'
        else:														# error
            print 'Error Command'
        print ok
        if ok==True:
            return 'Success'
        else:
            return 'Error'

    def mymoveinit(self):
        if self.motion.robotIsWakeUp() == False:
            self.motion.post.wakeUp()
            self.motion.post.moveInit()
        else:
            pass

    def sensor(self,interval):
        self.sonar.subscribe("xpserver")
        while SENSOR_FLAG == True:
            connection.send("BATTERY" + "#" + str(battery.getBatteryCharge()) + "\r")
            connection.send("SONAR1" + "#" + str(memory.getData("Device/SubDeviceList/US/Left/Sensor/Value")) + "\r")
            connection.send("SONAR2" + "#" + str(memory.getData("Device/SubDeviceList/US/Right/Sensor/Value")) + "\r")
            time.sleep(interval)
        # SENSOR_FLAG == False
        sonar.unsubscribe("xpserver")
        thread.exit_thread()

    def LArmInit(self):
        self.motion.setAngles('LShoulderPitch', 0, 0.2)
        self.motion.setAngles('LShoulderRoll', 0, 0.2)
        self.motion.setAngles('LElbowYaw', 0, 0.2)
        self.motion.setAngles('LElbowRoll', 0, 0.2)
        self.motion.setAngles('LWristYaw', 0, 0.2)
        self.motion.setAngles('LHand', 0, 0.2)
    def RArmInit(self):
        self.motion.setAngles('RShoulderPitch', 0, 0.2)
        self.motion.setAngles('RShoulderRoll', 0, 0.2)
        self.motion.setAngles('RElbowYaw', 0, 0.2)
        self.motion.setAngles('RElbowRoll', 0, 0.2)
        self.motion.setAngles('RWristYaw', 0, 0.2)
        self.motion.setAngles('RHand', 0, 0.2)
    def LArmUp(self):
        self.motion.setAngles('LShoulderPitch', 0.7, 0.2)
        self.motion.setAngles('LShoulderRoll', 0.3, 0.2)
        self.motion.setAngles('LElbowYaw', -1.5, 0.2)
        self.motion.setAngles('LElbowRoll', -0.5, 0.2)
        self.motion.setAngles('LWristYaw', -1.7, 0.2)
    def RArmUp(self):
        self.motion.setAngles('RShoulderPitch', 0.7, 0.2)
        self.motion.setAngles('RShoulderRoll', -0.3, 0.2)
        self.motion.setAngles('RElbowYaw', 1.5, 0.2)
        self.motion.setAngles('RElbowRoll', 0.5, 0.2)
        self.motion.setAngles('RWristYaw', 1.7, 0.2)
    def ArmUp2(self):
        self.motion.rest()
        self.motion.wakeUp()
        self.motion.setAngles('RShoulderPitch', 0.7, 0.2)
        self.motion.setAngles('RWristYaw', 1.5, 0.2)
        self.motion.setAngles('LShoulderPitch', 0.7, 0.2)
        self.motion.setAngles('LWristYaw', -1.5, 0.2)
    def LArmMoveInit(self):
        self.motion.setAngles('LShoulderPitch', 1, 0.2)
        self.motion.setAngles('LShoulderRoll', 0.3, 0.2)
        self.motion.setAngles('LElbowYaw', -1.3, 0.2)
        self.motion.setAngles('LElbowRoll', -0.5, 0.2)
        self.motion.setAngles('LWristYaw', 0, 0.2)
        self.motion.setAngles('LHand', 0, 0.2)
    def RArmMoveInit(self):
        self.motion.setAngles('RShoulderPitch', 1, 0.2)
        self.motion.setAngles('RShoulderRoll', -0.3, 0.2)
        self.motion.setAngles('RElbowYaw', 1.3, 0.2)
        self.motion.setAngles('RElbowRoll', 0.5, 0.2)
        self.motion.setAngles('RWristYaw', 0, 0.2)
        self.motion.setAngles('RHand', 0, 0.2)

    def mysay(self,messages):
        #mesg = messages.encode('utf-8')
        messages=messages.encode('utf-8')
        print 'mesager is: '+messages
        self.tts.say(messages)
        #self.tts.say(chatrobot.chat(messages, lang))			# Chat Robot Talk
        #self.tts.setLanguage("English")
        thread.exit_thread()

    def record_on(self):
        global motion, tts
        self.motion.rest()
        #motion.wakeUp()
        self.tts.say("rest all joints")
        self.motion.setStiffnesses("Body", 0.0)

    def record_off(self):
        global motion, tts
        self.tts.say("lock all joints")
        self.motion.setStiffnesses("Body", 1.0)
        self.tts.say('recording')
        namelist = motion.getBodyNames('Body')
        anglelist = motion.getAngles('Body', True)
        global posture_value
        posture_value = {}
        for i in range(len(namelist)):
            posture_value[namelist[i]] = anglelist[i]
        self.tts.say('ok, recorded.')
        self.motion.rest()

    def reappear(self,posture_name):
        global posture_list
        global motion, tts
        if posture_name in posture_list:
            posture_value = posture_list[posture_name]
            self.motion.rest()
            self.motion.setStiffnesses("Body", 1.0)
            self.tts.post.say("reappear recorded posture")
            for name, angle in posture_value.items():
                self.motion.post.setAngles(name, angle, 0.1)
            time.sleep(3)
        else:
            self.tts.post.say('wrong posture name.')
