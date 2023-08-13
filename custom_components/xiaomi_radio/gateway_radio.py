import requests, asyncio, logging
from miio import Gateway, DeviceException


_LOGGER = logging.getLogger(__name__)

class GatewayRadio():

  def __init__(self, host, token):
    self.device = Gateway(host, token)
    self.current_info = {}

  def get_radio_info(self):
    ''' 获取当前信息 '''
    result = self.device.radio.get_radio_info()
    radio_id = result.get('current_program')
    if radio_id is not None and self.current_info.get('id') != radio_id:
      res = requests.get(f'https://live.ximalaya.com/live-web/v1/radio?radioId={radio_id}')
      res_data = res.json()
      data = res_data['data']
      artist = data.get('name', '小米电台')
      program = data.get('programName', artist)

      self.current_info = {
        'id': radio_id,
        'program': program,
        'artist': artist,
        'image': data.get('coverLarge', 'https://www.home-assistant.io/images/favicon-192x192-full.png')
      }

    return {
      'volume': result.get('current_volume', 100),
      'status': result.get('current_status'),
      **self.current_info
    }

  def get_mute(self):
    return self.device.radio.get_mute()

  def play(self):
    ''' 播放 '''
    return self.device.send('play_fm', ["on"])

  def pause(self):
    ''' 暂停 '''
    return self.device.send('play_fm', ["off"])

  def set_volume_level(self, volume_level):
    ''' 设置音量 
    volume_level: 1 ~ 100
    '''
    return self.device.send('volume_ctrl_fm', [str(volume_level)])

  def play_fm(self, fm):
    ''' 播放收藏 '''
    return self.device.send('play_specify_fm', {'id': fm['id'], 'type': fm['type']})

  def play_alarm(self, sound, volume):
      ''' 播放警报声
      声音 sound: 1 ~ 29
      音量 volume: 1 ~ 100
      '''
      return self.device.send('play_music_new',  [str(sound), volume])

  def play_music(self, mid):
    '''播放音乐
    '''
    return self.device.send('play_music', [mid, 100])

  def get_channels(self):
    ''' 获取电台收藏列表 '''
    _list = []
    start = 0
    while True:
        result = self.device.send('get_channels', {"start": start * 10})
        chs = result.get('chs')
        if chs is not None:
          start = start + 1
          _list.extend(chs)

        if chs is None or len(chs) < 10:
            break

    for item in _list:
      radio_id = item['id']
      res = requests.get(f'https://live.ximalaya.com/live-web/v1/radio?radioId={radio_id}')
      res_data = res.json()
      data = res_data['data']
      artist = data.get('name', '小米电台')
      program = data.get('programName', artist)
      item.update({
        'program': program,
        'artist': artist,
        'image': data.get('coverLarge', 'https://www.home-assistant.io/images/favicon-192x192-full.png')
      })

    return _list

  async def async_download_music(self, url):
    ''' 下载音乐 '''
    self.device.send("delete_user_music", ['99999'])
    self.device.send("download_user_music", ["99999", url])
    index = 0
    while index < 10:
        progess = self.device.send("get_download_progress", [])
        _LOGGER.debug(progess)
        if str(progess) == "['99999:100']":
            break
        index += 1
        await asyncio.sleep(1)
    if (index >= 10):
        _LOGGER.error("download tts file [" + url + "] to gateway failed.")
        return False
    await asyncio.sleep(1)
    return True
    # self.play_music(99999)

  def get_music_list(self, category):
    ''' 获取音乐信息
    0: alarm
    1: alarm
    2: chord
    3: custom
    '''
    result = self.device.send("get_music_info", [category])
    print(result)
    return result['list']