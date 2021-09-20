#!/usr/bin/env python
import os
import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import Empty
import time
t=float(0)

is_takeoff=0
def cb_takeoff(data):
    global is_takeoff,t
    is_takeoff=1
    t=float(0)
rospy.init_node('sim_target', anonymous=True)
target51_pub = rospy.Publisher('target51', Twist, queue_size=1)
target52_pub = rospy.Publisher('target52', Twist, queue_size=1)
takeoff_sub = rospy.Subscriber('/drone1/tello/takeoff', Empty, cb_takeoff)

rate = rospy.Rate(30)
t51=Twist()
t51.linear.x=0
t51.linear.y=1
t51.linear.z=0.9
t51.angular.z=1.5708

t52=Twist()
t52.linear.x=0
t52.linear.y=-1
t52.linear.z=0.9
t52.angular.z=1.5708
i=0
while  not rospy.is_shutdown():

    if not is_takeoff:
        continue

    # sim R
    # if i>0 and i<15:
    #     pass
    # elif i>15 and i<30:
    #     t52.angular.z=1.5709+1.5709/5.0*(i-15)
    # elif i>55 and i<65:
    #     t52.angular.z=3.142-3.142/10.0*(i-55)
    # elif i>65 and i<70:
    #     t52.angular.z=1.5709/5.0*(i-65)

    # sim t
    # if i>0 and i<40:
    #     pass
    # elif i>40 and i<70:
    #     t52.linear.x=(i-40)/10

    # sim t
    if i>0 and i<15:
        pass
    elif i>15 and i<50:
        t52.linear.y=-1+(i-15)*0.1


    target51_pub.publish(t51)
    target52_pub.publish(t52)
    i=i+1.0/30
    # print(i)
    rate.sleep()

