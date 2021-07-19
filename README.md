# xiaomi_radio
在HA使用的小米空调伴侣里的收音机

配置
```yaml
# 小米空调伴侣收音机
media_player:
  - platform: xiaomi_radio
    host: 192.168.1.106
    token: 空调伴侣密钥
```

TTS服务
```yaml
service: xiaomi_radio.tts
data:
  text: >-
    现在的时间是 {%- if now().hour < 12 -%} 上午 {%- elif now().hour == 12 -%} 中午
    {%- elif now().hour <= 18 -%} 下午 {%- else -%} 晚上 {%- endif %} {{now().strftime("%I:%M")}}
```


## 如果这个项目对你有帮助，请我喝杯<del style="font-size: 14px;">咖啡</del>奶茶吧😘
|支付宝|微信|
|---|---|
<img src="https://ha.jiluxinqing.com/img/alipay.png" align="left" height="160" width="160" alt="支付宝" title="支付宝">  |  <img src="https://ha.jiluxinqing.com/img/wechat.png" align="left" height="160" width="160" alt="微信支付" title="微信">
