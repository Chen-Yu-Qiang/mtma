#!/usr/bin/env python
import os
import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import Empty
import time
from gazebo_msgs.msg import ModelState
import numpy as np
import positioning_board
t=float(0)

is_takeoff=0
def cb_takeoff(data):
    global is_takeoff,t
    is_takeoff=1
    t=float(0)
rospy.init_node('sim_target', anonymous=True)
target51_pub = rospy.Publisher('target51', Twist, queue_size=1)
target52_pub = rospy.Publisher('target52', Twist, queue_size=1)
pose_pub = rospy.Publisher('gazebo/set_model_state', ModelState, queue_size=10)
takeoff_sub = rospy.Subscriber('/drone1/tello/takeoff', Empty, cb_takeoff)

rate = rospy.Rate(30)
t51=Twist()
t51.linear.x=-5.0
t51.linear.y=2.5
t51.linear.z=0.9
t51.angular.z=1.5708

t52=Twist()
t52.linear.x=5.0
t52.linear.y=-1.0
t52.linear.z=0.9
t52.angular.z=3.1416
i=0.0

def twist2model(t):
    m=ModelState()
    m.pose.position.x=t.linear.x
    m.pose.position.y=t.linear.y
    m.pose.position.z=t.linear.z
    m.pose.orientation.z=np.sin((t.angular.z+np.pi/2)/2)
    m.pose.orientation.w=np.cos((t.angular.z+np.pi/2)/2)
    return m

while  not rospy.is_shutdown():

    if not is_takeoff:
        continue

    # sim R
    if i>0 and i<15:
        pass
    elif i>15 and i<45:
        t52.angular.z=1.5709+3.14159*(i-15.0)/30.0
    # sim t
    # if i>0 and i<40:
    #     pass
    # elif i>40 and i<70:
    #     t52.linear.x=(i-40)/10

    # sim t
    # if i>0 and i<15:
    #     pass
    # elif i>15 and i<45:
    #     t51.linear.x=-5.0+(i-15)/3.0
    #     t52.linear.x=5.0-(i-15)/3.0


    target51_pub.publish(t51)
    m51=twist2model(t51)
    m51.model_name="Target1"
    pose_pub.publish(m51)



    target52_pub.publish(t52)
    m52=twist2model(t52)
    m52.model_name="Target2"
    pose_pub.publish(m52)


    p1=positioning_board.data[0]
    m1=twist2model(p1)
    m1.model_name='Positioning1'
    pose_pub.publish(m1)
    i=i+1.0/30
    # print(i)
    rate.sleep()

