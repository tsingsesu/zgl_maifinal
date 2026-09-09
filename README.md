# 这是我的最终任务仓库 :smile:

## 自动化-张冠良-最终任务

>我个人认为完成了所有基本要求和加分点，欢迎老师/学长/学姐检阅

### 使用方法

#### 1. Docker 一键运行
```bash
cd final_ws
sudo service docker start
docker compose up
docker compose down
```

#### 2.不使用docker 直接运行

```bash
export RCUTILS_CONSOLE_OUTPUT_FORMAT="[{severity}] [{name}]: {message}"   #隐藏日志时间戳，改用日常使用时间
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch maicontrol_pkg robot.launch.py
```
最后 `Ctrl+C` 退出

#### 3.修改参数
所有的参数均在`src/maicontrol_pkg/config/params.yaml`，内有非常详细的说明，可任意修改

修改完后记得`colcon build --packages-select maicontrol`或者记得`docker compose restart`

#### 4.切换任务一/任务二运行模式

目前src已挂载，<mark>以下为切换任务一/二模式的方式</mark>

<mark>改 `src/maicontrol_pkg/config/params.yaml` 后 docker compose restart(若项目运行中) 或 docker compose up(项目未运行)

### 文件/文件夹清单

#### src
`maicontrol_pkg`存放`chassisnode`底盘节点和`maincontrolnode`主控制节点
`map_config`用于存放地图数据

`launch`中的`robot.launch.py`文件，管理两个ros2节点统一启动

`config`中的`params.yaml`统一管理所有参数，工程化同时方便调试

#### `Dockerfile`以及 `docker-compose`制造镜像与容器、管理容器、一键启动两个节点

#### `.gitignore`

#### `.dockerignore`

#### `README.md`


### 注意

<mark>我将日志中时间打印的形式从时间戳换成了时-分-秒，为使日志打印效果更好，若不使用`docker-compose`一键启动，请修改.bashrc

在该文件最后插入

```bash
export RCUTILS_CONSOLE_OUTPUT_FORMAT="[{severity}] [{name}]: {message}"
```
