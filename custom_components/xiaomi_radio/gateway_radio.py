from miio import Gateway, DeviceException

class GatewayRadio():

  def __init__(self, host, token):
    self.device = Gateway(host, token)
    self.current_info = {}

  def get_radio_info(self):
    ''' 获取当前信息 '''
    result = self.device.radio.get_radio_info()
    radio_id = result.get('current_program')
    if self.current_info.get('id') != radio_id:
      res = requests.get(f'https://live.ximalaya.com/live-web/v1/radio?radioId={radio_id}')
      res_data = res.json()
      data = res_data['data']
      artist = data.get('name', '小米电台')
      program = data.get('programName', artist)

      self.current_info = {
        'id': radio_id,
        'program': program,
        'artist': artist
      }

    return {
      'volume': result.get('current_volume', 100),
      'status': result.get('current_status'),
      ***self.current_info
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
    ''' 设置音量 '''
    return self.device.send('volume_ctrl_fm', [str(volume_level * 100)])

  def play_fm(self, fm):
    ''' 播放收藏 '''
    return self.device.send('play_specify_fm', {'id': fm['id'], 'type': fm['type']})

  def play_alarm(self, sound, volume):
      ''' 播放警报声
      声音 sound: 1 ~ 29
      音量 volume: 1 ~ 100
      '''
      return self.device.send('play_music_new',  [str(sound), volume])

  def get_channels():
    ''' 获取电台收藏列表 '''
    _list = []
    start = 0
    while True:
        result = self.device.send('get_channels', {"start": start * 10})
        chs = result.get('chs')
        if chs is None or len(chs) < 10:
            break
        start = start + 1
        _list.extend(chs)
    return _list