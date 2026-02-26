#!/usr/bin/env python3
"""
每日天气推送（微信公众号模板消息）
使用心知天气 API + 微信测试号模板消息
"""

import requests
import datetime
import os
import sys

# ---------- 从环境变量读取配置 ----------
APP_ID = os.environ.get("APP_ID")
APP_SECRET = os.environ.get("APP_SECRET")
OPEN_ID = os.environ.get("OPEN_ID")
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")
TEMPLATE_ID = os.environ.get("TEMPLATE_ID")
CITY = os.environ.get("CITY", "岳阳")  # 默认岳阳，可通过环境变量修改
# -------------------------------------

def get_weather():
    """从心知天气获取实时天气"""
    url = "https://api.seniverse.com/v3/weather/now.json"
    params = {
        "key": WEATHER_API_KEY,
        "location": CITY,
        "language": "zh-Hans",
        "unit": "c"
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if "results" in data:
            now = data["results"][0]["now"]
            # 返回格式：天气 温度°C，例如 "晴 15°C"
            return f"{now['text']} {now['temperature']}°C"
        else:
            print("天气 API 返回异常:", data)
            return "获取天气失败"
    except Exception as e:
        print("天气 API 请求出错:", e)
        return "天气未知"

def get_access_token():
    """获取微信全局 access_token"""
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APP_ID}&secret={APP_SECRET}"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        return data.get("access_token")
    except Exception as e:
        print("获取 access_token 失败:", e)
        return None

def send_template_message(access_token, openid, template_id, data):
    """发送模板消息"""
    url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"
    payload = {
        "touser": openid,
        "template_id": template_id,
        "data": data
    }
    headers = {"Content-Type": "application/json"}
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        return resp.json()
    except Exception as e:
        print("发送模板消息失败:", e)
        return {"errcode": -1, "errmsg": str(e)}

def main():
    # 1. 确定发送时段（通过环境变量传入，避免时区问题）
    time_of_day = os.environ.get("TIME_OF_DAY")
    if not time_of_day:
        # 本地调试时自动判断（按中国时区）
        hour = datetime.datetime.now().hour
        if 5 <= hour < 12:
            time_of_day = "morning"
        elif 18 <= hour < 24:
            time_of_day = "evening"
        else:
            print("当前不在发送时段，退出")
            return
        print(f"自动判断时段: {time_of_day}")

    # 2. 根据时段准备文案
    if time_of_day == "morning":
        greeting = "早安啦~~"
        extra = "今天也是美好的一天哦"
    else:  # evening
        greeting = "晚安啦~~"
        extra = "不要给自己太大的压力"
    special = "今日特别推送"
    today = datetime.date.today().strftime("%Y-%m-%d")
    weather = get_weather()

    # 3. 构造模板消息数据（与模板中的变量对应）
    data = {
        "greeting": {"value": greeting},
        "special": {"value": special},
        "date": {"value": today},
        "weather": {"value": weather},
        "extra": {"value": extra}
    }

    # 4. 获取 access_token 并发送
    token = get_access_token()
    if not token:
        print("无法获取 access_token，程序退出")
        return

    result = send_template_message(token, OPEN_ID, TEMPLATE_ID, data)
    if result.get("errcode") == 0:
        print(f"{time_of_day} 消息发送成功！")
    else:
        print(f"发送失败: {result}")

if __name__ == "__main__":
    main()