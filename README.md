# 概述

本项目应用主要用来监测Apple Store线下直营店货源情况，主要使用Python实现。

首先感谢[iPhone-Pickup-Monitor](https://github.com/greatcodeeer/iPhone-Pickup-Monitor)项目带来的灵感，同时有些实现也直接使用了该项目的一些代码。

本项目在iPhone-Pickup-Monitor原有功能的基础上去掉了声音通知，但添加了多货源同时监控以及钉钉消息通知功能。

# 安装

```bash
# 拉取代码 
git clone https://github.com/LennonChin/AppleStore-Monitor.git

# 进入目录
cd AppleStore-Monitor

# 安装依赖
pip install -r requirements.txt
```

# 申请钉钉群机器人

【强烈建议配置】如不配置则没有通知功能。

本监控提供了钉钉监控的功能，可以在监控到有货源时将消息发送到钉钉群。如要启用该功能，首先需要创建一个钉钉群，并添加群机器人，详细可参考文档：

[自定义机器人接入](https://developers.dingtalk.com/document/robots/custom-robot-access?spm=ding_open_doc.document.0.0.62846573euH8Cn#topic-2026027)

机器人配置完毕后，记下相关的Access Token和Secret Key，后面配置时需要用到。

# 开始配置

可以配置多个监控商品：

```bash
$> python /User/LennonChin/Codes/AppleStore-Monitor/monitor.py config
--------------------
[0] AirPods
[1] iPhone 13
选择要监控的产品：0
--------------------
[0] AirPods
[1] AirPods Max
选择要监控的产品子类：1
--------------------
[0] AirPods Max - 银色
选择要监控的产品型号：0
--------------------
是否添加更多产品[Enter继续添加，非Enter键退出]：
--------------------
[0] AirPods
[1] iPhone 13
选择要监控的产品：1
--------------------
...
[3] iPhone 13 Pro Max
选择要监控的产品子类：3
--------------------
...
[11] 512GB 远峰蓝色
...
选择要监控的产品型号：11
--------------------
是否添加更多产品[Enter继续添加，非Enter键退出]：n
选择计划预约的地址：
请稍后...1/3
--------------------
[0] 北京
[1] 上海
...
请选择序号：1
请稍后...2/3
请稍后...3/3
--------------------
[0] 黄浦区
...
请选择序号：0
正在加载网络资源...
--------------------
输入钉钉机器人Access Token[如不配置直接回车即可]：# 此处如不配置，就没有通知功能
输入钉钉机器人Secret Key[如不配置直接回车即可]：# 此处如不配置，就没有通知功能
--------------------
输入扫描间隔时间[以秒为单位，默认为15秒，如不配置直接回车即可]：30 # 不建议太短，以免扫描过于频繁导致IP被封
扫描配置已生成，并已写入到apple_store_monitor_configs.json文件中
请使用 python /User/LennonChin/Codes/AppleStore-Monitor/monitor.py start 命令启动监控
```

配置完成后，会在当前目录下生成一个[apple_store_monitor_configs.json](https://github.com/LennonChin/AppleStore-Monitor/blob/main/apple_store_monitor_configs.json)文件：

```json
{
  "selected_products": {
    "MGYJ3CH/A": [
      "AirPods Max",
      "AirPods Max - \u94f6\u8272"
    ],
    "MLHG3CH/A": [
      "iPhone 13 Pro Max",
      "512GB \u8fdc\u5cf0\u84dd\u8272"
    ]
  },
  "selected_area": "\u4e0a\u6d77 \u4e0a\u6d77 \u9ec4\u6d66\u533a",
  "dingtalk_configs": {
    "access_token": "",
    "secret_key": ""
  },
  "scan_interval": 30
}
```

如果你明白每项的意思，也可以手动填写该JSON文件，不过一定要按照上面例子中的层级，尤其是`selected_products`部分。

另外欢迎各位补充本项目的[products.json](https://github.com/LennonChin/AppleStore-Monitor/blob/main/products.json)文件，添加更多产品信息。

# 启动监控

接下来只需要用下面的命令启动监控即可：

比如前台启动：

```bash
$> python /User/LennonChin/Codes/AppleStore-Monitor/monitor.py start
```

或者后台启动：

```bash
$> nohup python -u monitor.py start > monitor.log 2>&1 &
```

# 通知效果

4种情况会通知：

1. 启动时通知，以确认相关信息是否正确，启动是否成功。
2. 扫描到有货源时会通知。
3. 每天6:00 ~ 23:00整点报时，以确保程序还正常运行。
4. 程序异常时会通知，如不是致命异常，不用理会。

相关通知截图：

![NotificationExample.png](https://github.com/LennonChin/AppleStore-Monitor/blob/main/NotificationExample.png)