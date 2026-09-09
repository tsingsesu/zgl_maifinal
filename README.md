# 这是我的最终任务仓库 :smile:

## 自动化-张冠良-最终任务

### 文件/文件夹清单

#### src
`maicontrol_pkg`存放`chassisnode`底盘节点和`maincontrolnode`主控制节点
`map_config`用于存放地图数据

`launch`中的`robot.launch.py`文件，管理节点统一启动

`config`中的`params.yaml`统一管理所有参数，工程化同时方便调试

#### `Dockerfile`以及 `docker-compose`制造镜像与容器、管理容器

#### `.gitignore`

#### `README.md`

### 注意

<mark>我将日志中时间打印的形式从时间戳换成了时-分-秒，为使日志打印效果更好，请修改.bashrc

在该文件最后插入

```bash
export RCUTILS_CONSOLE_OUTPUT_FORMAT="[{severity}] [{name}]: {message}"
```
