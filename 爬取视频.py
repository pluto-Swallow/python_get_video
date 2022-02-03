'''
Author: your name
Date: 2022-01-22 19:23:14
LastEditTime: 2022-01-25 11:31:56
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: \MarkDown_note\爬取视频网站\爬取视频网站.py
'''

# 第01集: https://v8.dious.cc/20210519/VWpRtPQl/1000kb/hls/index.m3u8
# 第02集: https://v8.dious.cc/20210519/jf1HF0Es/1000kb/hls/index.m3u8
# 第03集: https://v8.dious.cc/20210519/IJP4Qn98/1000kb/hls/index.m3u8
# 第04集: https://v8.dious.cc/20210519/oOVEZ275/1000kb/hls/index.m3u8
# 第05集: https://v8.dious.cc/20210519/94wrIFcZ/1000kb/hls/index.m3u8
# 第06集: https://v8.dious.cc/20210519/IPet4PUW/1000kb/hls/index.m3u8


# 第14集: https://v8.dious.cc/20210519/eQNayZxP/1000kb/hls/index.m3u8

from posixpath import split
import re
import os			#导入模块
import requests
import asyncio
import aiofiles
import aiohttp
from Crypto.Cipher import AES

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"
}

# 创建文件夹
"""
path = 'E:/爬虫/视频/水月洞天/'	#设置创建后文件夹存放的位置
for i in range(1,31):	#这里创建10个文件夹
    if i < 10:
        i = "0" + str(i)
    else:
        i = str(i)
    name = "第" + i + "集"
	# *定义一个变量判断文件是否存在,path指代路径,str(i)指代文件夹的名字*
    isExists = os.path.exists(path+name)
    if not isExists:						#判断如果文件不存在,则创建
        os.makedirs(path+name)	
        print(f"{name} 目录创建成功")
    else:
        print(f"{name} 目录已经存在")	
        continue			#如果文件不存在,则继续上述操作,直到循环结束
    
"""


## 读取第一集m3u8并下载第一集的ts文件
def get_name(epi_num):
    if epi_num < 10:
        i = "0" + str(epi_num)
    else:
        i = str(epi_num)
    name = "第" + i + "集"
    return name


async def get_one_ts(name,url,ts_ser_num,session):
    headers = {
        "Referer": "http://www.bsjh66.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36"
    }
         # 发送请求
    try:
        async with session.get(url,headers = headers) as resp:             # 得到响应 
            # print(resp)
            async with aiofiles.open(f"E:/爬虫/视频/水月洞天/{name}/{ts_ser_num}",mode="wb") as f:

                await f.write(await resp.content.read())
            print(f"{name}: {ts_ser_num}","完成!!")
    except Exception as e:
        print(e)


def get_m3u8_url(epi_num):
    obj = re.compile(r'"url":"https:.*?"',re.S)
    resp = requests.get(f'http://www.bsjh66.com/vodplay/13237/1/{epi_num}.html',headers = headers)

    resp.encoding = "utf-8"
    url_id = obj.findall(resp.text)
    split_data = url_id[0].rsplit("\/",3)[1]
    split_str = url_id[0].rsplit("\/",3)[2]
    m3u8_url = f'https://v3.dious.cc/{split_data}/{split_str}/1000kb/hls/index.m3u8'
    resp.close()
    return m3u8_url

def get_m3u8_file(epi_num):

    m3u8_url = get_m3u8_url(epi_num)
    resp = requests.get(m3u8_url,headers = headers)
    name = get_name(epi_num)
    with open(f"E:/爬虫/视频/水月洞天/{name}/{name}.m3u8",mode = "wb") as f:
        f.write(resp.content)
    resp.close()

async def get_ts_url(epi_num):
    name = get_name(epi_num)
    tasks = []
    try:

        async with aiohttp.ClientSession() as session:  
            async with aiofiles.open(f"E:/爬虫/视频/水月洞天/{name}/{name}.m3u8",mode="r",encoding="utf-8") as f:
                tasks = []
                async for line in f:
                    line = line.strip()
                    if line.startswith("#"):
                        continue
                    ts_ser_num = line.rsplit("/",1)[1]          
                    tasks.append(asyncio.create_task(get_one_ts(name,line,ts_ser_num,session)))
                
                await asyncio.wait(tasks)  
    except Exception as e:
        print(e)

def get_key(epi_num):
    name = get_name(epi_num)
    try:
        with open(f"E:/爬虫/视频/水月洞天/{name}/{name}.m3u8",mode="r",encoding="utf-8") as f:
            data = f.read()
            key_url = re.search(r'URI="(?P<key_url>.*?)"',data).group("key_url")
        
        resp = requests.get(key_url,headers=headers)
        return(resp.text)
    except Exception as e:
        print(e)
        return "xxxxxxxxxxxx"

async def dec_ts(ts_file_name,key,epi_num):
    name = get_name(epi_num)
    aes = AES.new(key=str(key).encode("utf-8"),IV=b"0000000000000000",mode=AES.MODE_CBC)
    try:
        async with aiofiles.open("E:/爬虫/视频/水月洞天/第05集/{ts_file_name}",mode="rb") as f1,\
            aiofiles.open("E:/爬虫/视频/水月洞天/第05集/temp_{ts_file_name}",mode="wb") as f2:

            bs = await f1.read()
            await f2.write(aes.decrypt(bs))
        print(f"{name}: {ts_file_name} 解密完成!!!")
    except Exception as e:
        print(name)
        print(f"错误:{e}")
    

async def aio_dec(key,epi_num):
    name = get_name(epi_num) 
    tasks = []
    try:
        async with aiofiles.open(f"E:/爬虫/视频/水月洞天/{name}/{name}.m3u8",mode="r",encoding="utf-8") as f:
            async for line in f:
                line = line.strip()
                if line.startswith("#"):
                    continue
                ts_file_name = line.rsplit("/",1)[1]
                print(ts_file_name)
                task = asyncio.create_task(dec_ts(ts_file_name,key,epi_num))
                tasks.append(task)
            await asyncio.wait(tasks)
    except Exception as e:
        print(e)

async def main():
    # 创建文件夹
    epi_num = 6
    get_m3u8_file(epi_num)
    await get_ts_url(epi_num)
    key = get_key(epi_num)
    # print(key)
    await aio_dec(key,epi_num)
    

    
if __name__ == '__main__':
    # asyncio.run(main())
    asyncio.get_event_loop().run_until_complete(main())
