# 概述

本项目应用主要用来监测Apple Store线下直营店货源情况，主要使用Python实现。

首先感谢[iPhone-Pickup-Monitor](https://github.com/greatcodeeer/iPhone-Pickup-Monitor)项目带来的灵感，同时有些实现也直接使用了该项目的一些代码。

本项目在iPhone-Pickup-Monitor原有功能的基础上去掉了声音通知，但添加了多货源同时监控以及钉钉消息通知功能。

# 最近更新

- [x] 增加Telegram bot机器人群发功能，感谢[zsm1703](https://github.com/zsm1703)。[【PR #1】](https://github.com/LennonChin/AppleStore-Monitor/pull/1)
- [x] 将异常事件的提醒限制在6:00 ~ 23:00期间。
- [x] 可配置想要排除的直营店。
- [x] 可配置在程序发生异常时是否发送通知。
- [x] 增加Bark推送【仅iOS】，感谢[zh616110538](https://github.com/zh616110538)。[【PR #2】](https://github.com/LennonChin/AppleStore-Monitor/pull/2)
- [x] 修复未选择排除的直营店时出现的异常。

# 安装

```bash
# 拉取代码 
git clone https://github.com/LennonChin/AppleStore-Monitor.git

# 进入目录
cd AppleStore-Monitor

# 安装依赖
pip install -r requirements.txt
```

# 使用钉钉群机器人推送通知

【强烈建议配置】如不配置则没有通知功能。

本监控提供了钉钉监控的功能，可以在监控到有货源时将消息发送到钉钉群。如要启用该功能，首先需要创建一个钉钉群，并添加群机器人，详细可参考文档：

[自定义机器人接入](https://developers.dingtalk.com/document/robots/custom-robot-access?spm=ding_open_doc.document.0.0.62846573euH8Cn#topic-2026027)

机器人配置完毕后，记下相关的Access Token和Secret Key，后面配置时需要用到。

# 使用Telegram群机器人推送通知

Telegram bot群发功能已添加了，文档暂空。留给有需求的同学自己补充。

# 使用Bark推送通知

Bark仅针对iOS平台的推送，使用比较简单，下载Bark App，在下面的配置过程中输入携带了Key的URL即可。

# 开始配置

使用`python monitor.py config`命令进行配置，可以配置多个监控商品：

```bash
$> python monitor.py config
--------------------
[0] Apple Watch
[1] AirPods
[2] iPhone 13
选择要监控的产品：1
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
[0] Apple Watch
[1] AirPods
[2] iPhone 13
选择要监控的产品：2
--------------------
[0] iPhone 13 Mini
[1] iPhone 13
[2] iPhone 13 Pro
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
请选择地区序号：1
请稍后...2/3
请稍后...3/3
--------------------
[0] 黄浦区
...
请选择地区序号：0
正在加载网络资源...
--------------------
选择的计划预约的地址是：上海 上海 黄浦区，加载预约地址周围的直营店...
[0] 香港广场，地址：上海市黄浦区淮海中路 282 号
[1] 南京东路，地址：上海市黄浦区南京东路 300 号
[2] 上海环贸 iapm ，地址：上海市徐汇区淮海中路 999 号
[3] 浦东，地址：上海市浦东新区陆家嘴世纪大道 8 号
[4] 环球港，地址：上海市普陀区中山北路 3300 号
[5] 五角场，地址：上海市杨浦区翔殷路 1099 号
[6] 七宝，地址：上海市闵行区漕宝路 3366 号 
[7] 苏州，地址：苏州市苏州工业园区
[8] 无锡恒隆广场，地址：无锡市梁溪区
[9] 天一广场，地址：宁波市海曙区碶闸街 155 号
[10] 杭州万象城，地址：杭州市江干区富春路 701 号
[11] 西湖，地址：杭州市上城区平海路 100 号
排除无需监测的直营店，输入序号[直接回车代表全部监测，多个店的序号以空格分隔]：7 8 9 10 11
已选择的无需监测的直营店：苏州，无锡恒隆广场，天一广场，杭州万象城，西湖
--------------------
输入钉钉机器人Access Token[如不配置直接回车即可]：
输入钉钉机器人Secret Key[如不配置直接回车即可]：
--------------------
输入Telegram机器人Token[如不配置直接回车即可]：
输入Telegram机器人Chat ID[如不配置直接回车即可]：
输入Telegram HTTP代理地址[如不配置直接回车即可]：
--------------------
输入Bark URL[如不配置直接回车即可]：
--------------------
输入扫描间隔时间[以秒为单位，默认为30秒，如不配置直接回车即可]：
--------------------
是否在程序异常时发送通知[Y/n，默认为n]：
--------------------
扫描配置已生成，并已写入到apple_store_monitor_configs.json文件中
请使用 python monitor.py start 命令启动监控
```

配置完成后，会在当前目录下生成一个[apple_store_monitor_configs.json](https://github.com/LennonChin/AppleStore-Monitor/blob/main/apple_store_monitor_configs.json)文件：

```json
{
  "selected_products": {
    "MGYJ3CH/A": [
      "AirPods Max",
      "AirPods Max - 银色"
    ],
    "MLHG3CH/A": [
      "iPhone 13 Pro Max",
      "512GB 远峰蓝色"
    ]
  },
  "selected_area": "上海 上海 黄浦区",
  "exclude_stores": [
    "R688",
    "R574",
    "R531",
    "R532",
    "R471"
  ],
  "notification_configs": {
    "dingtalk": {
      "access_token": "",
      "secret_key": ""
    },
    "telegram": {
      "chat_id": "",
      "bot_token": "",
      "http_proxy": ""
    },
    "bark": {
      "url": "",
      "query_parameters": {
        "url": null,
        "isArchive": null,
        "group": null,
        "icon": null,
        "automaticallyCopy": null,
        "copy": null
      }
    }
  },
  "scan_interval": 30,
  "alert_exception": false
}
```

如果你明白每项的意思，也可以手动填写该JSON文件，不过一定要按照上面例子中的层级，尤其是`selected_products`部分。

另外欢迎各位补充本项目的[products.json](https://github.com/LennonChin/AppleStore-Monitor/blob/main/products.json)文件，添加更多产品信息。

# 启动监控

接下来只需要用下面的命令启动监控即可：

比如前台启动：

```bash
python monitor.py start
```

或者后台启动：

```bash
nohup python -u monitor.py start > monitor.log 2>&1 &
```

# 通知效果

4种情况会通知：

1. 启动时通知，以确认相关信息是否正确，启动是否成功。
2. 扫描到有货源时会通知。
3. 每天6:00 ~ 23:00整点报时，以确保程序还正常运行。
4. 程序异常时会通知，如不是致命异常，不用理会。

相关通知截图：

钉钉：

![DingTalkNotification](https://github.com/LennonChin/AppleStore-Monitor/blob/main/docs/DingTalkNotification.png)

Telegram：

![TelegramNotification](https://github.com/LennonChin/AppleStore-Monitor/blob/main/docs/TelegramNotification.png)

Bark：

![BarkNotification](https://github.com/LennonChin/AppleStore-Monitor/blob/main/docs/BarkNotification.png)