#!/usr/bin/env python
import os
import rospy
from geometry_msgs.msg import Point
from geometry_msgs.msg import Twist
from std_msgs.msg import Empty
from tello_driver.msg import TelloStatus
import threading
import time
Tello_list=[1,2]


class aTello_takeoff:
    def __init__(self,i):
        self.sub_state=rospy.Subscriber("drone"+str(i)+'/tello/status', TelloStatus,self.cb_state)
        self.sub_full_image=rospy.Subscriber("drone"+str(i)+"/tello_raw",Image,self.cb_full_image)
        self.pub_mtake=rospy.Publisher("drone"+str(i)+'/tello/manual_takeoff', Empty, queue_size=1)
        self.pub_cmd=rospy.Publisher("drone"+str(i)+'/tello/cmd_vel', Twist, queue_size=1)
        self.is_on=0
        self.is_ready=0
        self.is_mtake=0
        self.state=None
    def cb_state(self,data):
        self.state=data
        if not self.is_on:
            time.sleep(1)
            self.is_on=1
            self.pub_mtake.publish(Empty())

    def cb_full_image(self,data):
        self.is_ready=1

    def takeoff(self,z_cmd):
        up_msg=Twist()
        up_msg.linear.z=z_cmd
        up_msg.linear.y=0
        up_msg.linear.x=0
        up_msg.angular.z=0
        self.pub_cmd.publish(up_msg)


rospy.init_node('control_op_node', anonymous=True)
takeoff_pub_list = [rospy.Publisher("drone"+str(i)+'/tello/takeoff', Empty, queue_size=1) for i in Tello_list]
land_pub_list = [rospy.Publisher("drone"+str(i)+'/tello/land', Empty, queue_size=1) for i in Tello_list]
aTello_takeoff_list=[aTello_takeoff(i) for i in Tello_list]
isSIM=rospy.get_param('isSIM')
while 1:
    print("t=takeoff\nl=land\n>>>")
    op=raw_input()
    if op == "t":
        rospy.loginfo("takeoff!")
        if isSIM==0:
            # for i in range(len(takeoff_pub_list)):
            #     takeoff_pub_list[i].publish(Empty())
            #     rospy.loginfo("drone"+str(Tello_list[i])+" real takeoff!")

            all_ready=1
            for i in range(len(aTello_takeoff_list)):
                if aTello_takeoff_list[i].is_ready==0:
                    rospy.logerr("drone"+str(Tello_list[i])+"  not ready!!!")
                    all_ready=0
            
            if all_ready==0:
                continue

            target_height=1.1
            kp=1.0
            t=time.time()
            for i in range(len(aTello_takeoff_list)):
                rospy.loginfo("drone"+str(Tello_list[i])+" start takeoff!")

            while (time.time()-t)<4:
                for i in range(len(aTello_takeoff_list)):
                    aTello_takeoff_list[i].takeoff(kp*(target_height-aTello_takeoff_list[i].state.height_m))
                time.sleep(0.1)
            
            for i in range(len(aTello_takeoff_list)):
                aTello_takeoff_list[i].takeoff(0)
                rospy.loginfo("drone"+str(Tello_list[i])+" finish takeoff!")

            
    else:
        rospy.loginfo("land!!!")
        if isSIM==0:
            for i in range(len(land_pub_list)):
                land_pub_list[i].publish(Empty())
                rospy.loginfo("drone"+str(Tello_list[i])+"real land!!!")

