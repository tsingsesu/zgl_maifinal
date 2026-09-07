FROM ros:humble
WORKDIR /final_app
#WORKDIR 相当于给该项目容器配置专属终端
COPY src/ ./src
#只将src中的内容复制到容器内
RUN bash -c "source /opt/ros/humble/setup.bash && colcon build --symlink-install"
CMD ["bash", "-c", "source /opt/ros/humble/setup.bash && source /final_app/install/setup.bash && ros2 launch maicontrol_pkg robot.launch.py"]
