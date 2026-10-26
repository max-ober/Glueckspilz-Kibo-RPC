#!/usr/bin/env python3
import rospy
import subprocess
from std_msgs.msg import String
from ib2_msgs.msg import Navigation

class Maestro:
    def __init__(self):
            rospy.init_node('maestro')
            print("Maestro started")

            rospy.Subscriber("/sensor_fusion/navigation", Navigation, self.print_pos)

            rospy.spin()
    
    def print_pos(self, data):
         print(data)


def summon_maestro():
    subprocess.Popen(["rosrun", "krpc_user" ,"maestro.py"])

if __name__ == '__main__':
    m = Maestro()