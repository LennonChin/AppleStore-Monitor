# -*- coding: UTF-8 –*-
"""
@Author: LennonChin
@Contact: i@coderap.com
@Date: 2021-10-19
"""
import re
import sys
import os
import random
import datetime
import requests
import json
import time
import hmac
import hashlib
import base64
import urllib.parse
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Utils:

    @staticmethod
    def time_title(message):
        return "[{}] {}".format(datetime.datetime.now().strftime('%H:%M:%S'), message)

    @staticmethod
    def subject_title(subject, message):
        return "<{}>\n[{}] {}".format(subject, datetime.datetime.now().strftime('%H:%M:%S'), message)

    @staticmethod
    def log(message):
        print(Utils.time_title(message))

    @staticmethod
    def send_message(notification_configs, message, **kwargs):
        if len(message) == 0:
            return

        # Wrapper for exception caught
        def invoke(func, configs):
            try:
                func(configs, message, **kwargs)
            except Exception as err:
                Utils.log(err)

        # DingTalk message
        invoke(Utils.send_dingtalk_message, notification_configs["dingtalk"])

        # Bark message
        invoke(Utils.send_bark_message, notification_configs["bark"])

        # Telegram message
        invoke(Utils.send_telegram_message, notification_configs["telegram"])

        # Email message
        invoke(Utils.send_email_message, notification_configs["email"])

    @staticmethod
    def send_dingtalk_message(dingtalk_configs, message, **kwargs):
        if len(dingtalk_configs["access_token"]) == 0 or len(dingtalk_configs["secret_key"]) == 0:
            return

        timestamp = str(round(time.time() * 1000))
        secret_enc = dingtalk_configs["secret_key"].encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, dingtalk_configs["secret_key"])
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

        headers = {
            'Content-Type': 'application/json'
        }

        params = {
            "access_token": dingtalk_configs["access_token"],
            "timestamp": timestamp,
            "sign": sign
        }

        content = {
            "msgtype": "text" if "message_type" not in kwargs else kwargs["message_type"],
            "text": {
                "content": message
            }
        }

        response = requests.post("https://oapi.dingtalk.com/robot/send", headers=headers, params=params, json=content)
        Utils.log("Dingtalk发送消息状态码：{}".format(response.status_code))

    @staticmethod
    def send_email_message(configs, message, **kwargs):
        if configs["to_email"]:
            try:
                # 创建一个MIMEMultipart对象来表示邮件
                msg = MIMEMultipart()
                msg['From'] = configs["smtp_username"]
                msg['To'] = configs["to_email"]
                title_parse = re.search(r"\<(.*?)>([\S\s]*)", message)
                msg['Subject'] = title_parse and title_parse.group(1) or "Apple Store监控通知"
                message = title_parse and title_parse.group(2) or ""
                # 添加邮件正文
                msg.attach(MIMEText(message, 'plain'))

                # 创建SMTP客户端
                server = smtplib.SMTP(configs["smtp_server"], configs["smtp_port"])
                server.starttls()  # 启用TLS加密，如果需要的话

                # 登录到SMTP服务器
                server.login(configs["smtp_username"], configs["smtp_password"])

                # 发送邮件
                server.sendmail(configs["smtp_username"], configs["to_email"], msg.as_string())

                # 关闭SMTP客户端连接
                server.quit()

                Utils.log("邮件发送成功！")
            except Exception as e:
                Utils.log("邮件发送失败:{}".format(str(e)))

    @staticmethod
    def send_telegram_message(telegram_configs, message, **kwargs):
        if len(telegram_configs["bot_token"]) == 0 or len(telegram_configs["chat_id"]) == 0:
            return

        headers = {
            'Content-Type': 'application/json'
        }

        proxies = {
            "https": telegram_configs["http_proxy"],
        }

        content = {
            "chat_id": telegram_configs["chat_id"],
            "text": message
        }

        url = "https://api.telegram.org/bot{}/sendMessage".format(telegram_configs["bot_token"])
        response = requests.post(url, headers=headers, proxies=proxies, json=content)
        Utils.log("Telegram发送消息状态码：{}".format(response.status_code))

    @staticmethod
    def send_bark_message(bark_configs, message, **kwargs):
        if len(bark_configs["url"]) == 0:
            return

        url = "{}/{}".format(bark_configs["url"].strip("/"), urllib.parse.quote(message, safe=""))
        response = requests.post(url, params=bark_configs["query_parameters"])
        Utils.log("Bark发送消息状态码：{}".format(response.status_code))


class AppleStoreMonitor:
    headers = {
        'sec-ch-ua': '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
        'Referer': 'https://www.apple.com.cn/shop/buy-iphone/',
        'DNT': '1',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
        'sec-ch-ua-platform': '"macOS"',
    }

    def __init__(self):
        self.count = 1
        self.timeout = 10
        self.history = []
        self.alter_swc = True

    @staticmethod
    def config():
        """
        进行各类配置操作
        """
        products = json.load(open('products.json', encoding='utf-8'))

        configs = {
            "selected_products": {},
            "selected_area": "",
            "exclude_stores": [],
            "notification_configs": {
                "dingtalk": {
                    "access_token": "",
                    "secret_key": ""
                },
                "telegram": {
                    "bot_token": "",
                    "chat_id": "",
                    "http_proxy": ""
                },
                "bark": {
                    "url": "",
                    "query_parameters": {
                        "url": None,
                        "isArchive": None,
                        "group": None,
                        "icon": None,
                        "automaticallyCopy": None,
                        "copy": None
                    }
                },
                "email": {
                    "to_email": "",
                    "smtp_server": "",
                    "smtp_port": "",
                    "smtp_username": "",
                    "smtp_password": ""
                }
            },
            "scan_interval": 30,
            "alert_exception": False,
            "always_alert": False
        }

        while True:
            # chose product type
            print('--------------------')
            for index, item in enumerate(products):
                print('[{}] {}'.format(index, item))
            product_type = list(products)[int(input('选择要监控的产品：'))]

            # chose product classification
            print('--------------------')
            for index, (key, value) in enumerate(products[product_type].items()):
                print('[{}] {}'.format(index, key))
            product_classification = list(products[product_type])[int(input('选择要监控的产品子类：'))]

            # chose product classification
            print('--------------------')
            for index, (key, value) in enumerate(products[product_type][product_classification].items()):
                print('[{}] {}'.format(index, value))
            product_model = list(products[product_type][product_classification])[int(input('选择要监控的产品型号：'))]

            configs["selected_products"][product_model] = (
                product_classification, products[product_type][product_classification][product_model])

            print('--------------------')
            if len(input('是否添加更多产品[Enter继续添加，非Enter键退出]：')) != 0:
                break

        # config area
        print('选择计划预约的地址：')
        url_param = ['state', 'city', 'district']
        choice_params = {}
        param_dict = {}
        for step, param in enumerate(url_param):
            print('请稍后...{}/{}'.format(step + 1, len(url_param)))
            response = requests.get("https://www.apple.com.cn/shop/address-lookup", headers=AppleStoreMonitor.headers,
                                    params=choice_params)
            result_param = json.loads(response.text)['body'][param]
            if type(result_param) is dict:
                result_data = result_param['data']
                print('--------------------')
                for index, item in enumerate(result_data):
                    print('[{}] {}'.format(index, item['value']))
                input_index = int(input('请选择地区序号：'))
                choice_result = result_data[input_index]['value']
                param_dict[param] = choice_result
                choice_params[param] = param_dict[param]
            else:
                choice_params[param] = result_param

        print('正在加载网络资源...')
        response = requests.get("https://www.apple.com.cn/shop/address-lookup", headers=AppleStoreMonitor.headers,
                                params=choice_params)
        selected_area = json.loads(response.text)['body']['provinceCityDistrict']
        configs["selected_area"] = selected_area

        print('--------------------')
        print("选择的计划预约的地址是：{}，加载预约地址周围的直营店...".format(selected_area))

        store_params = {
            "location": selected_area,
            "parts.0": list(configs["selected_products"].keys())[0]
        }
        response = requests.get("https://www.apple.com.cn/shop/fulfillment-messages",
                                headers=AppleStoreMonitor.headers, params=store_params)

        stores = json.loads(response.text)['body']["content"]["pickupMessage"]["stores"]
        for index, store in enumerate(stores):
            print("[{}] {}，地址：{}".format(index, store["storeName"], store["retailStore"]["address"]["street"]))

        exclude_stores_indexes = input('排除无需监测的直营店，输入序号[直接回车代表全部监测，多个店的序号以空格分隔]：').strip().split()
        if len(exclude_stores_indexes) != 0:
            print("已选择的无需监测的直营店：{}".format("，".join(list(map(lambda i: stores[int(i)]["storeName"], exclude_stores_indexes)))))
            configs["exclude_stores"] = list(map(lambda i: stores[int(i)]["storeNumber"], exclude_stores_indexes))

        print('--------------------')
        # config notification configurations
        notification_configs = configs["notification_configs"]

        # config dingtalk notification
        dingtalk_access_token = input('输入钉钉机器人Access Token[如不配置直接回车即可]：')
        dingtalk_secret_key = input('输入钉钉机器人Secret Key[如不配置直接回车即可]：')

        # write dingtalk configs
        notification_configs["dingtalk"]["access_token"] = dingtalk_access_token
        notification_configs["dingtalk"]["secret_key"] = dingtalk_secret_key

        # config telegram notification
        print('--------------------')
        telegram_chat_id = input('输入Telegram机器人Chat ID[如不配置直接回车即可]：')
        telegram_bot_token = input('输入Telegram机器人Token[如不配置直接回车即可]：')
        telegram_http_proxy = input('输入Telegram HTTP代理地址[如不配置直接回车即可]：')

        # write telegram configs
        notification_configs["telegram"]["chat_id"] = telegram_chat_id
        notification_configs["telegram"]["bot_token"] = telegram_bot_token
        notification_configs["telegram"]["http_proxy"] = telegram_http_proxy

        # config bark notification
        print('--------------------')
        bark_url = input('输入Bark URL[如不配置直接回车即可]：')

        # write dingtalk configs
        notification_configs["bark"]["url"] = bark_url

        # config email notification
        print('--------------------')
        to_email = input('输入邮件接收地址[如不配置直接回车即可]：')
        if to_email is not None:
            smtp_server = input('输入邮件服务器[如不清楚建议百度]：')
            smtp_port = input('输入邮件服务器端口号：')
            smtp_username = input('输入发件人用户名：')
            smtp_password = input('输入发件人密码：')

            # write email configs
            notification_configs["email"]["to_email"] = to_email
            notification_configs["email"]["smtp_server"] = smtp_server
            notification_configs["email"]["smtp_port"] = smtp_port
            notification_configs["email"]["smtp_username"] = smtp_username
            notification_configs["email"]["smtp_password"] = smtp_password

        # 输入扫描间隔时间
        print('--------------------')
        configs["scan_interval"] = int(input('输入扫描间隔时间[以秒为单位，默认为30秒，如不配置直接回车即可]：') or 30)

        # 有货时是否重复提醒
        print('--------------------')
        configs["always_alert"] = (input('有货时是否重复提醒[Y/n，默认为n]：').lower().strip() or "n") == "y"

        # 是否对异常进行告警
        print('--------------------')
        configs["alert_exception"] = (input('是否在程序异常时发送通知[Y/n，默认为n]：').lower().strip() or "n") == "y"

        with open('apple_store_monitor_configs.json', 'w') as file:
            json.dump(configs, file, indent=2)
            print('--------------------')
            print("扫描配置已生成，并已写入到{}文件中\n请使用 python {} start 命令启动监控".format(file.name, os.path.abspath(__file__)))

    def start(self):
        """
        开始监控
        """
        configs = json.load(open('apple_store_monitor_configs.json', encoding='utf-8'))
        selected_products = configs["selected_products"]
        selected_area = configs["selected_area"]
        exclude_stores = configs["exclude_stores"]
        notification_configs = configs["notification_configs"]
        scan_interval = configs["scan_interval"]
        alert_exception = configs["alert_exception"]
        always_alert = configs["always_alert"]

        products_info = []
        for index, product_info in enumerate(selected_products.items()):
            products_info.append("【{}】{}".format(index, " ".join(product_info[1])))
        message = Utils.subject_title("Apple Store监控开始通知",
                                      "准备开始监测，商品信息如下：\n{}\n取货区域：{}\n扫描频次：{}秒/次".format(
                                          "\n".join(products_info), selected_area,
                                          scan_interval))
        Utils.log(message)
        Utils.send_message(notification_configs, message)

        params = {
            "location": selected_area,
            "mt": "regular",
        }

        code_index = 0
        product_codes = selected_products.keys()
        for product_code in product_codes:
            params["parts.{}".format(code_index)] = product_code
            code_index += 1

        # 上次整点通知时间
        last_exactly_time = -1
        while True:
            available_list = []
            tm_hour = time.localtime(time.time()).tm_hour
            try:
                # 更新请求时间
                params["_"] = int(time.time() * 1000)

                response = requests.get("https://www.apple.com.cn/shop/fulfillment-messages",
                                        headers=AppleStoreMonitor.headers,
                                        params=params,
                                        timeout=self.timeout)

                json_result = json.loads(response.text)
                stores = json_result['body']['content']['pickupMessage']['stores']
                Utils.log(
                    '-------------------- 第{}次扫描 --------------------'.format(
                        self.count + 1))
                for item in stores:
                    store_name = item['storeName']
                    if item["storeNumber"] in exclude_stores:
                        print("【{}：已排除】".format(store_name))
                        continue
                    print("{:-<100}".format("【{}】".format(store_name)))
                    for product_code in product_codes:
                        pickup_search_quote = item['partsAvailability'][product_code]['pickupSearchQuote']
                        pickup_display = item['partsAvailability'][product_code]['pickupDisplay']
                        store_pickup_product_title = item['partsAvailability'][product_code]['messageTypes']['regular']['storePickupProductTitle']
                        print('\t【{}】{}'.format(pickup_search_quote, store_pickup_product_title))
                        if pickup_search_quote == '今天可取货' or pickup_display != 'unavailable':
                            available_list.append((store_name, product_code, store_pickup_product_title))
                if len(available_list) > 0:
                    messages = []
                    print("命中货源，请注意 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                    Utils.log("以下直营店预约可用：")
                    available_stores = []
                    for item in available_list:
                        messages.append("【{}】 {}".format(item[0], item[2]))
                        available_stores.append(item[0])
                        print("【{}】{}".format(item[0], item[2]))
                    print(
                        "命中货源，请注意 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                    if always_alert or self.alter_swc:
                        Utils.send_message(notification_configs,
                                           Utils.subject_title(
                                               "{}有货通知".format(available_stores),
                                               "第{}次扫描到直营店有货，信息如下：\n{}".format(self.count,
                                                                                             "\n".join(messages))))
                    self.alter_swc = False
                    self.history.append(datetime.datetime.now())
                else:
                    if not self.alter_swc:
                        not_available_time = datetime.datetime.now()
                        time_diff = not_available_time - self.history[-1]
                        hours = time_diff.seconds // 3600
                        minutes = (time_diff.seconds % 3600) // 60
                        seconds = time_diff.seconds % 60
                        Utils.send_message(notification_configs,
                                           Utils.subject_title(
                                               "监测的货物已售罄！",
                                               "本次放货时间:{}\n售罄时间:{}\n共持续:{}{}{}"
                                               .format(available_time.strftime("%Y年%m月%d日 %H:%M:%S"), not_available_time.strftime("%Y年%m月%d日 %H:%M:%S"),
                                                       hours and str(hours) + "小时" or "", minutes and str(minutes) + "分" or "", seconds and str(seconds) + "秒" or "")))
                    self.alter_swc = True

            except Exception as err:
                Utils.log(err)
                # 6:00 ~ 23:00才发送异常消息
                if alert_exception and 6 <= tm_hour <= 23:
                    Utils.send_message(notification_configs,
                                       Utils.subject_title("Apple Store监控异常通知",
                                                           "第{}次扫描出现异常：{}".format(self.count, repr(err))))

            if len(available_list) == 0:
                interval = max(random.randint(int(scan_interval / 2), scan_interval * 2), 5)
                Utils.log('{}秒后进行第{}次尝试...'.format(interval, self.count))

                # 整点通知，用于阶段性检测应用是否正常
                if last_exactly_time != tm_hour and (6 <= tm_hour <= 23):
                    Utils.send_message(notification_configs,
                                       Utils.subject_title("Apple Store监控运行通知",
                                                           "已扫描{}次，扫描程序运行正常，目前所检测的商品{}".format(
                                                               self.count,
                                                               self.alter_swc and "无货" or "有货，请尽快前往下单")))
                    last_exactly_time = tm_hour
                time.sleep(interval)
            else:
                time.sleep(5)

            # 次数自增
            self.count += 1


if __name__ == '__main__':
    args = sys.argv

    if len(args) != 2:
        print("""
        Usage: python {} <option>
        option can be:
        \tconfig: pre config of products or notification
        \tstart: start to monitor
        """.format(args[0]))
        exit(1)

    if args[1] == "config":
        AppleStoreMonitor.config()

    if args[1] == "start":
        AppleStoreMonitor().start()
