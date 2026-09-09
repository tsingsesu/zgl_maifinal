'''
底盘节点
'''
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from datetime import datetime

def now_str():
    return datetime.now().strftime('%H:%M:%S')


class MaiChassis(Node):
    def __init__(self):
        super().__init__('Mai_chassis')
        #以下两者配合，从yaml中读值
        self.declare_parameter('feedback_hz',100.0)
        self.declare_parameter('max_speed',2.0)
        self.feedback_hz = self.get_parameter('feedback_hz').value
        self.max_speed = self.get_parameter('max_speed').value

        #订阅主控速度指令
        self.cmd_sub = self.create_subscription(Twist , 'cmd_vel' , self.cmd_callback , 10)
        #创建发布器对象，以此格式发布实际执行的速度给主控，让主控据此做位置积分
        self.vel_pub = self.create_publisher(Twist , 'act_vel' , 10)
        #定时器执行定时发布实际速度信息给主控
        self.timer = self.create_timer( 1.0/self.feedback_hz , self.timer_callback)

        self.current = Twist()# 存放当前速度信息

        self.stopped = False #用于判断当前是否已经处于停止状态

    def cmd_callback(self , msg):
        if msg.linear.x == 0.0 and msg.linear.y == 0.0:
            
            self.current.linear.x = 0.0
            self.current.linear.y = 0.0

            if not self.stopped:#新增，防止停止日志不断刷屏
                self.stopped = True
                self.get_logger().info(f'[{now_str()}] 底盘收到运动停止指令，已停止')

        else:
            self.current.linear.x = max(-self.max_speed , min(self.max_speed , msg.linear.x))
            self.current.linear.y = max(-self.max_speed , min(self.max_speed , msg.linear.y))
            #主控发布的速度由底盘过滤后，返回真实执行速度，而且我认为在本题中，过滤不合理的速度是底盘的唯一实际物理功能

    #具体回调函数，将格式与定时联系
    def timer_callback(self):
        self.vel_pub.publish(self.current)




def main():
    rclpy.init()
    node = MaiChassis()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()