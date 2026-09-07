FROM ros:humble
WORKDIR /final_terminal
#WORKDIR 相当于给该项目容器配置专属终端
COPY src/ /final_ws_in_docker/src
#只将src中的内容复制到容器内
RUN bash -c "source /opt/ros/humble/setup.bash" && colcon build 
CMD ["bash", "-c", "source /opt/ros/humble/setup.bash && source /final_ws_in_docker/install/setup.bash && ros2 launch maicontrol_pkg maincontrolnode.launch.py"]
