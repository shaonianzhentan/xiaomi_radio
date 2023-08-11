import time, asyncio
from miio import Gateway, DeviceException

device = Gateway('192.168.0.105', 'e7d17baf8f9e05103b502afa163ee0a7')
print(device.info())
print(device.radio.get_radio_info())


# 警报声
def play_alarm(sound, volume):
    '''
    声音 sound: 1 ~ 29
    音量 volume: 1 ~ 100
    '''
    return device.send('play_music_new',  [str(sound), volume])


# print(play_alarm(29, 50))

# 发码
def send_code():
  ir_command = 'FE00000000000000000000000004009622BA003600A601D4138822010001010000010000010000010100010101010000000001000000010101010000000000000100000101010101000101022201000101000001000001000001010001010001010101010100010000000000000000010000000000010100010101010102220100010100000100000100000101000101000101010101010001000000000000000001000000000001010001010101010301'
  state = device.status()
  air_condition_model = state.air_condition_model.hex()
  if air_condition_model is not None:
      device.send_ir_code(air_condition_model, ir_command)


'''
https://mobile.ximalaya.com/radio-first-page-app/search?locationId=0&locationTypeId=0&categoryId=0&pageNum=1&pageSize=100
'''
# 添加电台
def play_radio(program_id):
    return device.send('play_specify_fm', {'id': program_id, 'type': 0, 'url': "http://live.ximalaya.com/radio-first-page-app/live/58/64.m3u8"})

'''
print()
'''


#print(play_radio(58))

def remove_channels(chs):
    return device.send('add_channels', {'chs': chs})

# print(remove_channels([{'id': 93, 'type': 0, 'url': ''}]))

def add_channels(chs):
    return device.send('add_channels', {'chs': chs})

# 没啥用，url无法添加
#add_channels([{"id": 93, "type": 0, "url": "http://live.ximalaya.com/radio-first-page-app/live/635/64.m3u8"} ])

def get_channels():
    ''' 获取电台收藏列表 '''
    _list = []
    start = 0
    while True:
        result = device.send('get_channels', {"start": start * 10})
        chs = result.get('chs')
        if chs is None or len(chs) < 10:
            break
        start = start + 1
        _list.extend(chs)
    return _list

print(get_channels())


print(device.radio.get_radio_info())
