'''
主控制节点
'''

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from maicontrol_pkg.map_config import WAYPOINTS, NEXT
import time
import math
from datetime import datetime

def now_str():#我发现时间戳不利于人观察机器人运动时间状态，虽然可能利于机器阅读，所以所有的日志都换成日常时间，顺便修改.bashrc隐藏时间戳
    return datetime.now().strftime('%H:%M:%S')

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
        self.declare_parameter('brake_dist',3.0)
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

        self.actual_vel = Twist()#创建消息类型，接收底盘发送的实际速度，统一格式
        self.last_time = time.time()#定义前一时刻
        self.current_target = NEXT[self.start]#字典，利用键值映射来表示“下一个”的概念，self.current_target即当前目标节点
        self.steps = 0 #已走段数
        self.finished = False#完成记号，指示任务已完成用于终止速度发布，即小车停止运动

        #以下日志只在初始化时打印，不会刷屏
        if self.mode == "patrol": 
            self.get_logger().info(f'[{now_str()}] 任务一启动 从起点={self.start}  绕一圈巡航')
        else:
            self.get_logger().info(f'[{now_str()}] 任务二启动  起点={self.start}  终点={self.goal}  行驶')

        self.timer = self.create_timer(1.0/self.hz, self.control_callback)#在默认值中 T = 1/20 = 0.05s 视作极小时间，调用回调函数，处理运动相关信息

    def vel_callback(self, msg):#负责接听的函数是不需要扔到定时执行器的，只需要订阅
        self.actual_vel = msg

    def control_callback(self):#维护位置、发布速度指令
        now = time.time()#定义此时时刻
        dt = now - self.last_time
        self.x += self.actual_vel.linear.x *dt#位置要用实际传回的速度*dt
        self.y += self.actual_vel.linear.y *dt
        self.last_time = now #更新上一时刻时间
        
        tx, ty = WAYPOINTS[self.current_target]# tx ==target x 当前目标位置横坐标
        delta_x = tx - self.x#delta_x距离差(横坐标)
        delta_y = ty - self.y
        dist =  math.sqrt(delta_x**2 + delta_y**2)#距离目标长度

        if dist < self.tol and not self.finished :#判断是否到达目的地，not self.finish防止到达终点后重复发送坐标

            self.steps = self.steps +1#任务一中要求绕一整圈，共8段，以steps来判断段数
            self.get_logger().info(f'[{now_str()}] 已到达 {self.current_target} 节点')

            #判断完成
            if self.mode == 'point_to_point' and self.current_target == self.goal:#任务二判断完成
                self.finished = True
                self.get_logger().info(f'[{now_str()}] 任务完成！已到达指定目的地，目的地编号: {self.goal} ，最终位置 {self.x:.2f}, {self.y:.2f},已经足够接近，可以认为到达')

            elif self.mode == 'patrol' and self.steps == 8 :#任务一判断完成
                self.finished = True
                self.get_logger().info(f'[{now_str()}] 任务完成！已环行一圈，最终位置 {self.x:.2f}, {self.y:.2f},已经足够接近，可以认为到达')
            else:
                self.current_target = NEXT[self.current_target]  #只是到达了目标节点，未到达最终节点，更新最终节点     
 
        cmd = Twist()#创建消息类型，发送速度指令给底盘，统一格式
        if self.finished != True:#只有还未完成时才需要发布速度指令，利用self.finished判断是否完成
            '必须要在self.current_target = NEXT[self.current_target]后重新定义一遍目标位置，因为每次到达一个节点时会更新目标，如果使用旧位置信息会出问题'
            tx, ty = WAYPOINTS[self.current_target]
            delta_x = tx - self.x
            delta_y = ty - self.y   
            dist = math.sqrt(delta_x**2 + delta_y**2)

            if dist > 1e-6:#防止除0报错
                '''
                借鉴PythonRobotics/PathTracking/move_to_pose/move_to_pose.py中的比例减速策略
                实际应用中机器人不可能做到速度立即突变  会损伤底盘器件经过节点时需要转弯时需要减速  需要主控制端积极做出减速策略 
                '''
                speed = self.v_cruise * min(1.0 , dist/self.brake_dist)
                #将速度分解到x,y方向即可得到两个方向速度
                cosx = delta_x/dist
                cosy = delta_y/dist
                cmd.linear.x = speed * cosx
                cmd.linear.y = speed * cosy
        else :
            cmd.linear.x = 0.0
            cmd.linear.y = 0.0                 
        #每一个0.05s发布一次速度指令
        self.cmd_pub.publish(cmd)



def main():
    rclpy.init()
    node = MaiMaincontrol()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()