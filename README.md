# xiaomi_radio
在HA使用的小米空调伴侣里的收音机

[![hacs_badge](https://img.shields.io/badge/Home-Assistant-%23049cdb)](https://www.home-assistant.io/)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

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
|支付宝|微信|
|---|---|
<img src="https://github.com/shaonianzhentan/ha-docs/raw/master/docs/img/alipay.png" align="left" height="160" width="160" alt="支付宝" title="支付宝">  |  <img src="https://github.com/shaonianzhentan/ha-docs/raw/master/docs/img/wechat.png" align="left" height="160" width="160" alt="微信支付" title="微信">