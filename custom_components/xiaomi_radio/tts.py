import os, logging, asyncio, functools, aiohttp, hashlib
from haffmpeg.core import HAFFmpeg
from homeassistant.components.ffmpeg import (DATA_FFMPEG, CONF_EXTRA_ARGUMENTS)

_LOGGER = logging.getLogger(__name__)

def md5(data):
    return hashlib.md5(data.encode(encoding='UTF-8')).hexdigest()

class AacConverter(HAFFmpeg):

    async def convert(self, input_source, output, extra_cmd=None, timeout=15):
        command = [
            "-vn",
            "-c:a",
            "aac",
            "-strict",
            "-2",
            "-b:a",
            "64K",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-y"
        ]      
        is_open = await self.open(cmd=command, input_source=input_source, output=output, extra_cmd=extra_cmd)         
        if not is_open:
            _LOGGER.warning("Error starting FFmpeg.")
            return False
        try:
            proc_func = functools.partial(self._proc.communicate, timeout=timeout)
            out, error = await self._loop.run_in_executor(None, proc_func)
        except (asyncio.TimeoutError, ValueError):
            _LOGGER.error("Timeout convert audio file.")
            self._proc.kill()
            return False    
        return True

    async def async_download(self, url, file_path):
        headers = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as response:
                file = await response.read()
                with open(file_path, 'wb') as f:
                    f.write(file)

    async def async_get_file(self, tts_dir, tts_url):
        file_name = f'radio_{md5(tts_url)}'
        mp3Path = f'{tts_dir}/{file_name}.mp3'
        aacPath = f'{tts_dir}/{file_name}.aac'
        # 下载文件
        if os.path.exists(mp3Path) == False:
            await self.async_download(tts_url, mp3Path)

        # 转码
        if os.path.exists(aacPath) == False:
            result = await self.convert(mp3Path, output=aacPath)
            if (not result) or (not os.path.exists(aacPath)) or (os.path.getsize(aacPath) < 1):
                _LOGGER.error("Convert file to aac failed.")
                return None
        return f'{file_name}.aac'

def get_converter(hass):
    return AacConverter(hass.data[DATA_FFMPEG].binary)