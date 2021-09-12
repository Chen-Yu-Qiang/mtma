#!/usr/bin/env python
import os
import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import Empty
import time

rospy.init_node('sim_target', anonymous=True)
target51_pub = rospy.Publisher('target51', Twist, queue_size=1)
target52_pub = rospy.Publisher('target52', Twist, queue_size=1)

takeoff_pub = rospy.Publisher('tello/takeoff', Empty, queue_size=1)

rate = rospy.Rate(30)
t51=Twist()
t51.linear.x=0
t51.linear.y=0.65
t51.linear.z=0.9
t51.angular.z=1.5709

t52=Twist()
t52.linear.x=0
t52.linear.y=-0.65
t52.linear.z=0.9
t52.angular.z=1.5709
i=0
while  not rospy.is_shutdown():

    if i<=1:
        takeoff_pub.publish(Empty())
        rospy.loginfo("real takeoff!")

    # sim R
    # if i>0 and i<40:
    #     pass
    # elif i>40 and i<50:
    #     t52.linear.x=(i-40)/10
    # elif i>50 and i<55:
    #     t52.angular.z=1.5709+1.5709/5.0*(i-50)
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
    if i>0 and i<40:
        pass
    elif i>40 and i<80:
        t52.linear.y=-0.65-(i-40)/10


    target51_pub.publish(t51)
    target52_pub.publish(t52)
    i=i+1.0/30
    print(i)
    rate.sleep()

