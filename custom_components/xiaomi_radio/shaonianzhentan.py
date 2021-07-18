import aiohttp, asyncio

# 下载文件
async def download(url, file_path):
    headers = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            file = await response.read()
            with open(file_path, 'wb') as f:
                f.write(file)

# 执行异步方法
def async_create_task(async_func):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_func)