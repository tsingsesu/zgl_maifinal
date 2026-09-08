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
        self.v_cruise = self.get_parameter('cruise_speed').value
        self.brake_dist = self.get_parameter('brake_dist').value
        self.tol = self.get_parameter('arrival_tolerance').value

        #通信 对应chassisnode中的相应部分 
        self.cmd_pub = self.create_publisher(Twist, 'cmd_vel', 10)#主控制向底盘发布建议速度
        self.vel_sub = self.create_subscription(Twist, 'act_vel', self.vel_callback, 10)#底盘向主控返回实际速度

        self.x = WAYPOINTS[self.start][0]#先检索编号，然后取出字典右侧元组的第一个值当作x坐标
        self.y = WAYPOINTS[self.start][1]

        self.actual_vel = Twist()
        self.last_time = time.time()
        self.current_target = NEXT[self.start]#字典，利用键值映射来表示“下一个”的概念
        self.steps = 0 #已走段数
        self.finished = False#完成记号，指示任务已完成用于终止速度发布，即小车停止运动

        #以下日志只在初始化时打印，不会刷屏
        if self.mode == "patrol": 
            self.get_logger().info(f'任务一启动 从起点={self.start}  绕一圈巡航')
        else:
            self.get_logger().info(f'任务二启动  起点={self.start}  终点={self.goal}  行驶')

        self.timer = self.create_timer(1.0/self.hz, self.control_callback)

    def vel_callback(self, msg):#负责接听的函数是不需要扔到定时执行器的，只需要订阅
        self.actual_vel = msg

    def control_callback(self):
        now = time.time()
        dt = now - self.last_time
        self.x += self.actual_vel.linear.x *dt
        self.y += self.actual_vel.linear.y *dt
        self.last_time = now 
        
        tx, ty = WAYPOINTS[self.current_target]
        delta_x = self.x - tx
        delta_y = self.y - ty
        dist =  math.sqrt(delta_x**2 + delta_y**2)

        if dist < self.tol :

            arrived = self.current_target
            self.steps = self.steps +1
            self.get_logger().info(f'已到达 {arrived} 节点')

            #判断完成
            if self.mode == 'point_to_point' and arrived == self.goal:
                self.finished = True
                self.get_logger().info(f'任务完成！已到达指定目的地，目的地编号: {self.goal} ，最终位置 ({self.x:.2f}, {self.y:.2f}),已经足够接近，可以认为到达')

            elif self.mode == 'patrol' and self.steps == 8 :
                self.finished == True
                self.get_logger().info(f'任务完成！已环行一圈，最终位置 ({self.x:.2f}, {self.y:.2f},已经足够接近，可以认为到达')
            else:
                self.current_target = NEXT[arrived]       
 



def main():
    rclpy.init()
    node = MaiMaincontrol()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()