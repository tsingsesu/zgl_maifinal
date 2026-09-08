'''
底盘节点
'''
import rclpy
from rclpy.node import Node
from geometry_msgs import Twist


MAX_SPEED = 2

class MaiChassis(Node):
    def __init__(self):
        super().__init__('Mai_chassis')
        self.declare_parameter('feedback',100)
        self.feedback_hz = self.get_parameter('feedback_hz').value

        #订阅主控速度指令
        self.cmd_sub = self.create_subscription(Twist , 'cmd_vel' , self.cmd_callback , 10)
        #创建发布器对象，以发布实际执行的速度给主控，让主控据此做位置积分
        self.vel_pub = self.create_publisher(Twist , 'act_vel' , 10)

        self.current = Twist()# 存放当前速度信息

        self.timer = self.create_timer( 1/self.feedback_hz ,self.timer_callback)



        def cmd_callback(self , msg):
            self.current.linear.x = max(-MAX_SPEED , min(MAX_SPEED , msg.linear.x))

        def timer_callback(self):
            self.vel_pub.publish(self.current)




def main():
    rclpy.init()
    node = MaiChassis()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()