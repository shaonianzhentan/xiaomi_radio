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