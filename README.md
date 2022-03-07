# xiaomi_radio
在HA使用的小米空调伴侣里的收音机

[![hacs_badge](https://img.shields.io/badge/Home-Assistant-%23049cdb)](https://www.home-assistant.io/)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)


![visit](https://visitor-badge.glitch.me/badge?page_id=shaonianzhentan.xiaomi_radio&left_text=visit)
![forks](https://img.shields.io/github/forks/shaonianzhentan/xiaomi_radio)
![stars](https://img.shields.io/github/stars/shaonianzhentan/xiaomi_radio)

## 使用方式

安装完成重启HA，刷新一下页面，在集成里搜索`小米电台`即可

[![Add Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=xiaomi_radio)

整点报时

[![导入蓝图](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fshaonianzhentan%2Fxiaomi_radio%2Fblob%2Fmain%2Fblueprints%2Ftime_reminder.yaml)

TTS服务
```yaml
service: xiaomi_radio.tts
data:
  text: >-
    现在的时间是 {%- if now().hour < 12 -%} 上午 {%- elif now().hour == 12 -%} 中午
    {%- elif now().hour <= 18 -%} 下午 {%- else -%} 晚上 {%- endif %} {{now().strftime("%I:%M")}}
```

## 更新日志

- 集成默认红外码文件
- 支持集成安装

## 如果这个项目对你有帮助，请我喝杯<del style="font-size: 14px;">咖啡</del>奶茶吧😘
|  |支付宝|微信|
|---|---|---|
奶茶= | <img src="https://cdn.jsdelivr.net/gh/shaonianzhentan/ha-docs@master/docs/img/alipay.png" align="left" height="160" width="160" alt="支付宝" title="支付宝">  |  <img src="https://cdn.jsdelivr.net/gh/shaonianzhentan/ha-docs@master/docs/img/wechat.png" height="160" width="160" alt="微信支付" title="微信">

## 关注我的微信订阅号，了解更多HomeAssistant相关知识
<img src="https://cdn.jsdelivr.net/gh/shaonianzhentan/ha-docs@master/docs/img/wechat-channel.png" height="160" alt="HomeAssistant家庭助理" title="HomeAssistant家庭助理">

---
**在使用的过程之中，如果遇到无法解决的问题，付费咨询请加Q`635147515`**