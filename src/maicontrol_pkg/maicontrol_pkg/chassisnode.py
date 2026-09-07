'''
底盘节点
'''
import rclpy
from rclpy.node import Node

class MaiChassis(Node):
    def __init__(self):
        super().__init__('Mai_chassis')











def main():
    rclpy.init()
    node = MaiChassis()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()