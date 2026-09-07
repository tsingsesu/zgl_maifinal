'''
主控制节点
'''

import rclpy
from rclpy.node import Node

class MaiMaincontrol(Node):
    def __init__(self):
        super().__init__('Mai_maincontrol')







def main():
    rclpy.init()
    node = MaiMaincontrol()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()