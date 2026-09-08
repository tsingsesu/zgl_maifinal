'''
主控制节点
'''

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from maicontrol_pkg.map_config import WAYPOINTS, NEXT
import time
import math

class MaiMaincontrol(Node):
    def __init__(self):
        super().__init__('Mai_maincontrol')
        #从yaml中读取一系列参数
        self.declare_parameter('mode', 'patrol')
        self.declare_parameter('start_point', 1)
        self.declare_parameter('goal_point', 4)
        self.declare_parameter('control_hz', 20.0)
        self.declare_parameter('cruise_speed',2.5)
        self.declare_parameter('arrival_tolerance', 0.05)
        self.mode = self.get_parameter('mode').value
        self.start = self.get_parameter('start_point').value
        self.goal = self.get_parameter('goal_point').value
        self.hz = self.get_parameter('control_hz').value
        self.v_cruise = self.get_parameter('curise_speed').value
        self.tol = self.get_parameter('arrival_tolerance').value

        #通信 对应chassisnode中的相应部分 
        self.cmd_pub = self.create_publisher(Twist, 'cmd_vel', 10)#主控制向底盘发布建议速度
        self.vel_pub = self.create_subscription(Twist, 'act_vel', 10)#底盘向主控返回实际速度

        self.x = WAYPOINTS[self.start][0]#先检索编号，然后取出字典右侧元组的第一个值当作x坐标
        self.y = WAYPOINTS[self.start][1]

        self.actual_vel = Twist()
        self.last_time = time.time()
        self.current_target = NEXT[self.start]
        self.steps = 0 #已走段数
        self.finished = False

        if self.mode == "patrol": 
            self.get_logger().info(f'任务一启动 从起点={self.start}  绕一圈巡航')
        else:
            self.get_logger().info(f'任务二启动  起点={self.start}  终点={self.goal}  行驶')

        self.timer = self.create_timer(1.0/self.hz, self.control_callback)

    def vel_callback(self, msg):
        self.actual_vel = msg


    def control_callback(self):
        now = time.time()
        dt = now - self.last_time
        self.x += self.actual_vel.linear.x *dt
        self.y += self.actual_vel.linear.y *dt
        self.last_time = now 
        




        delta_x = abs(abs(self.x)-abs(WAYPOINTS[NEXT[self.start + self.steps]][0]))
        delta_y = abs(abs(self.y)-abs(WAYPOINTS[NEXT[self.start + self.steps]][1]))
        dist =  math.sqrt(delta_x**2 + delta_y**2)

        if dist < self.tol :
            self.get_logger(f'已到达 {NEXT[self.start+self.steps]} 节点')        
            self.steps = self.steps +1



def main():
    rclpy.init()
    node = MaiMaincontrol()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()