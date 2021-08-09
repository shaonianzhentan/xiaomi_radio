import aiohttp, yaml, asyncio, hashlib, os

# 下载文件
async def download(url, file_path):
    headers = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            file = await response.read()
            with open(file_path, 'wb') as f:
                f.write(file)

# MD5加密
def md5(data):
    return hashlib.md5(data.encode(encoding='UTF-8')).hexdigest()

# 执行异步方法
def async_create_task(async_func):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_func)

# 加载yaml
def load_yaml(file_path):
    # 不存在则返回空字典
    if os.path.exists(file_path) == False:
        return {}
    fs = open(file_path, encoding="UTF-8")
    data = yaml.load(fs, Loader=yaml.FullLoader)
    return data

# 存储为yaml
def save_yaml(file_path, data):
    _dict = {}
    _dict.update(data)
    with open(file_path, 'w') as f:
        yaml.dump(_dict, f)