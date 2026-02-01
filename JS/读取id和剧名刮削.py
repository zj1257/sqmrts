# coding=utf-8
import requests
import re
from time import sleep
import urllib3 # 屏蔽ssl warning
urllib3.disable_warnings(urllib3.connectionpool.InsecureRequestWarning)
import json
from prettytable import PrettyTable
import os

s = requests.Session()
s.headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) quark-cloud-drive/3.0.1 Chrome/100.0.4896.160 Electron/18.3.5.12-a038f7b798 Safari/537.36 Channel/pckk_other_ch',
}
cookies_str = "ctoken=npnC1oqZWWEXIwoeS9KlbM0i;b-user-id=582bd5d8-437f-b391-111a-4a1223574726;grey-id=4598be75-34c9-7ab0-a8a6-5cf6f97d71a5;grey-id.sig=_9dJ-Mnel-rHI64VwBH4A7UmiwQB-tfuZYoKyKFBDdg;isQuark=true;isQuark.sig=hUgqObykqFom5Y09bll94T1sS9abT1X-4Df_lzgl8nM;__wpkreporterwid_=755685c9-5f55-4a85-16d2-5ae412781ee5;_UP_A4A_11_=wb9cc1fec77a4868bc0dfd51f406597a;_UP_D_=pc;_UP_F7E_8D_=OU7RkS5Fl8As%2BzBYApELkZAj1vmg8xVBJrecefKxOw3mXKC6HZxA28beRDVDsfr9xbHg71N%2BX%2BRLHpvA%2Fhicy1HUTu2LBlCPom4qTWeMFqCgN55FQx3lIyu%2B1OsWIKjG1w4pOGWcZjvuo4m2jHof9eRj66wpeTPO4r7NBD%2F4wEE0IpjIBHWretgcndtvmRjOzww5cstuAQbqUw8FWZQadLzk4nczcPLP1rSgCMVm5ws2Z%2BPyTAVLm9DknFGHhIbrCg%2FZdcEvIQgqhPgIQ9TgLP9Y4da5UPkfCOADGv8v9D8VOMEdD6uzZJXMxBnUatpyAHLu79tlMNqP8TGNMQXXgvSqK5ufzR58ZeivnehV0qE%2FWt1yDEDt%2BfWrmT4mVs6zZWXvqpzmoV3MeygIUCEakjmqUpi%2BMoCaK%2BK%2BYrCYUbg6F8u7yQFbh%2F0Q7RCSfK2U6tAXQttwc%2FtDK7HYGyvolg%3D%3D;tfstk=gdYjeTwNxs-r0NKdcNlzRQaebD72lbuEG519tCU46ZQYWdOGUsrqmGk6VdpPHEoc3L66TC4N3I7x1d9phGJ6sjfOBdp1Qnor8IAcSNHeC2ueir9IY89fXGe-615YHbSAj7bJ0NHEL4umljj1WdrIzGJWwTf1MPI9B7h51s_TkGUY28Bl6NQODrF8y6CYB1CADbORE1QOBdQtNaBl6NB9BNdUkf5oX9AjOUiYjYFMoIB7WPLjRZBBwlzYkU1fnQdAFiS2PssfLGhcZnY9OCLVPHwt5TLDgULPcz0NeHOOl_j01P_9gTvC3dIy5yWCWqr_jtUON9lSNlqiW11iP9rLb-jAZ_-jNbZw3iClN9lSNlqGD_f8SbG7bK5..;_UP_30C_6A_=st9cc6201318cqglt3sp1g8fbcj2pb42;_UP_TS_=sg1222464072d5f810b2b10b4b969a7a5b6;_UP_E37_B7_=sg1222464072d5f810b2b10b4b969a7a5b6;_UP_TG_=st9cc6201318cqglt3sp1g8fbcj2pb42;_UP_335_2B_=1;__pus=9419630a8d4424a7f9cc41b0930be35eAASj/4qJ52RjX8qn7AlYxg7cddJr4+vdfOmEnuwvz8LYHcdQAZwbbJIPERgqJCGCrMyRhBNDVnZICA22AfattChN;__kp=84eee170-74f6-11f0-a1f3-c9db997168c5;__kps=AARU7wIFft+ykEyp6z8cXwiv;__ktd=h0g2aJQ0Q9XyVWV9BVhQnQ==;__uid=AARU7wIFft+ykEyp6z8cXwiv;web-grey-id=70a92f0b-349c-7700-6c2f-8adf211cb121;web-grey-id.sig=t3jsYfI-WdMKo-3F6u4ZldLwP8s6bWU6L4-Ff-_6UiE;__puus=5c66c8a647563725e551524f46ec7596AAS2Y5Jg3x98dIfZtjpR2VA71pxZGhZMIDihyx/EYlROvsmZv+bJN/X1gFkZA6PES1H8Z9Pvkzvdggrf5fyUsQeKEx9wdN4lSAydcUDovm3Tkrdx+TTYbj+aUZ5a99JdGXSR/MI0bIxbpgBeb/x8CgEcEtWS1guENuh9bxOjUAy8CycUkQgHgSQMXGB86gCE2tRhdaTh2AJ8xO4Y93xLNcGt"
cookies_dict = dict([l.split("=", 1) for l in cookies_str.split("; ")])
if cookies_dict:
    cookies = requests.utils.cookiejar_from_dict(cookies_dict)
    s.cookies.update(cookies)

# 存储所有文件夹信息
folders = []

def getFolder(fid, path="", recursive=False, write_file=False):
    """
    递归获取指定 fid 下的所有子文件夹，并记录到 folders 中。
    每进入一个层级都写入一次 Excel，防止程序中途崩溃。
    """
    print(f"正在处理：{path} ({fid})")
    pg = 1
    vodList = []
    sleep(1) 
    # 获取当前目录下所有内容
    while True:
        url = f'https://drive-pc.quark.cn/1/clouddrive/file/sort?pr=ucpro&fr=pc&uc_param_str=&pdir_fid={fid}&_page={pg}&_size=100&_fetch_total=1&_fetch_sub_dirs=0&_sort=file_type:asc,file_name:asc'
        r = s.get(url, timeout=10)
        sleep(0.1)
        data = r.json()
        # print(data)
        vodList += data["data"]["list"]
        pg += 1
        if pg > -(-data['metadata']['_total'] // 100):  # 向上取整
            break

    # 遍历列表，筛选出文件夹并递归处理
    for vod in vodList:
        if vod['dir']:  # 如果是文件夹
            folder = {
                "folder": vod["fid"],
                "parentId": vod["pdir_fid"],
                "fileType": "folder",
                "fileName": vod["file_name"],
                "parentName": path.split("/")[-1] if path else "",
                "path": path + "/" + vod["file_name"] if path else vod["file_name"]
            }
            folders.append(folder)
            if write_file:
                import pandas as pd
                # 实时写入 Excel，避免数据丢失 新版本的 pandas 需要指定 engine
                # df = pd.DataFrame([folder])
                # write_header = not hasattr(getFolder, "header_written") or not getFolder.header_written
                # df.to_excel("data.xlsx", index=False, header=write_header, mode='a', engine='openpyxl')
                # if write_header:
                #     getFolder.header_written = True

                # 实时写入 Excel，兼容旧版 Pandas（无 mode='a'）
                try:
                   df_old = pd.read_excel("data.xlsx", engine='openpyxl')
                   df_new = pd.DataFrame([folder])
                   df_combined = pd.concat([df_old, df_new], ignore_index=True)
                except FileNotFoundError:
                   df_combined = pd.DataFrame([folder])

                df_combined.to_excel("data.xlsx", index=False, engine='openpyxl')
            # 递归进入子文件夹
            if recursive:
                getFolder(vod["fid"], folder["path"], recursive, write_file)
    return folders


# 设置请求头
header = {
    'Content-Type': 'application/json',
    'Host': 'frodo.douban.com',
    'Connection': 'Keep-Alive',
    'Referer': 'https://servicewechat.com/wx2f9b06c1de1ccfca/84/page-frame.html',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat'
}

def scrapeMovieId(file_name):
    params = {'q': file_name, 'start': 0, 'count': count, 'apikey': '0ac44ae016490db2204ce0a042db2916'}
    r = requests.get('https://frodo.douban.com/api/v2/search/movie', headers=header, verify=False, params=params, timeout=10)
    #print(r.text.encode('utf-8').decode('unicode-escape'))
    if r.status_code == 200 and r.json()['items']:
        scrapes = []
        videos = r.json()['items']
        tb = PrettyTable(["序号", "ID", "标题", "年份", "类型", "备注"])
        for i, video in enumerate(videos):
            item={
                "id": video['target_id'],
                "title": video['target']['title'],
                "year": video['target']['year'],
                "type": video['type_name'],
                "remark": video['target']['card_subtitle'].replace(" / ", '|').replace(' ', '|'),
                "pic": video['target']['cover_url']
            }
            tb.add_row([str(i), item["id"], item["title"], str(item["year"]), item["type"], item["remark"]])
            if len(videos) == 1:
                return item
            scrapes.append(item)
        print(tb)
        index = int(input("请根据序号选择剧集："))
        print("你选择的剧集是：")
        print("{:<3} {:<10} {:<20} {:<5} {:<10} {:<50}".format(str(index), scrapes[index]["id"], scrapes[index]["title"], str(scrapes[index]["year"]), scrapes[index]["type"], scrapes[index]["remark"]))
        return scrapes[index]

def getScrapeInfos(item):            
    sid = item["id"]
    params = {'apikey': '0ac44ae016490db2204ce0a042db2916'}
    r = requests.get(f'https://frodo.douban.com/api/v2/movie/{sid}', headers=header, verify=False, params=params, timeout=10)
    scrapeInfos = r.json()
    # print(scrapeInfos)
    pic = re.sub(r'photo/(.*?)/', 'photo/l/', scrapeInfos['pic']['large']) + '@User-Agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36@Referer=https://www.douban.com/'
    year = scrapeInfos['year']
    title = scrapeInfos['title']
    remark = scrapeInfos['card_subtitle'].replace(' / ', '/').strip()
    content = scrapeInfos['intro'].strip()
    actors = ''
    for actor in scrapeInfos['actors']:
        actors += f"{actor['name']}|"
    actors = actors.strip('|')
    directors = ''
    for director in scrapeInfos['directors']:
        directors += f"{director['name']}|"
    directors = directors.strip('|')
    countries = ''
    for country in scrapeInfos['countries']:
        countries += f"{country}|"
    countries = countries.strip('|')
    vodList = {"pic": pic, "year": year, 'title': title, "remark": remark, 'content': content, 'actors': actors, 'directors': directors, 'countries': countries}
    #print(vodList)
    return vodList

# 选择菜单
print("=== 请选择 ===")
print("1. 生成文件列表，手动加图片")
print("2. 自动刮削")
print("3. 手动刮削")

# 获取用户输入并处理
while True:
    choice = input("\n请输入选项编号（1-3）：")
    if choice == "1":
        print("你选择了【生成文件列表】")
        AUTO = True
        LIST = True
        break
    elif choice == "2":
        print("你选择了【自动刮削】")
        # 自动刮削
        AUTO = True
        LIST = False
        break
    elif choice == "3":
        print("你选择了【手动刮削】")
        # 自动刮削
        AUTO = False
        LIST = False
        break
    else:
        print("输入错误！请仅输入 1 、 2 或 3")



#print("自动刮削模式") if AUTO else print("手动刮削模式")
count = 1 if AUTO else 20
results = []
data = []
# data = [{'folder':'9cda66af018b490b9afcb6f1ee91d78f','fileName':'螺丝钉 第三季'},
# {'folder':'ecd2c07472704ff68e95b025347c813c','fileName':'平博士密码'}]


# 替换为你的目标网址
url = "https://16158.kstore.space/scrape.json"

try:
    # 发送请求获取JSON
    response = requests.get(url, timeout=10)
    response.raise_for_status()  # 抛出HTTP错误（如404、500）
    
    # 解析JSON并赋值给变量
    scrape_data = response.json()
    
    # 保存到本地文件
    with open("scrape.json", "w", encoding="utf-8") as f:
        json.dump(scrape_data, f, ensure_ascii=False, indent=2)
    
    print("JSON获取并保存成功！")
except requests.exceptions.RequestException as e:
    print(f"请求失败：{e}")
except json.JSONDecodeError:
    print("解析JSON失败，目标网址返回内容非有效JSON")
# 1. 读取同级目录下的scrape.json文件
#file_path = "scrape.json"  # 同级目录直接写文件名
#with open(file_path, "r", encoding="utf-8") as f:
#    scrape_data = json.load(f)  # 加载为Python字典/列表

if not data:
    datas = getFolder("d4589f3a32874972a2f97622091e9888")
#来自分享d4589f3a32874972a2f97622091e9888
#安安专属65b3da4439d04e29b467dd507cfc01f5
   # datas = getFolder("207994a523684ab180ae835970ac9164")

    # with open('results2.json', 'w', encoding='utf-8') as f:
    #     json.dump(datas, f, ensure_ascii=False, indent=4)
    tb = PrettyTable(["序号", "文件夹ID", "文件夹名"])
    k=0
    datas2=[]
    for i, data in enumerate(datas):
        sign = False
        for j in scrape_data["scrape"]:
            if data['folder']==j["folder"]:
                sign = True
                break
        if sign == False:
            tb.add_row([str(k), data['folder'], data['fileName']])
            datas2.append(data)
            k=k+1
    print(tb)
    if LIST:
        data = datas2
    else:
        index = input("请选择需要刮削的文件夹序号（空格分隔）：")
        if " " in index:
            index = [int(i) for i in index.split(" ")]
        else:
            index = [int(index)]
        data = [datas2[i] for i in index]
        print("你选择的文件夹是：")
        tb2 = PrettyTable(tb.field_names)
        for i in index:
            tb2.add_row(tb._rows[i])
        print(tb2)

for row in data:
    result = {}
    result['folder'] = row['folder']
    result['fileName'] = row['fileName']
    result['imgurl'] = ""
    file_name = row['fileName'].split("：")[-1]
    print(file_name)
    if LIST:
        mid =False
    else:
        mid = scrapeMovieId(file_name)
        sleep(0.1)
    if mid:
        vod_list = getScrapeInfos(mid)
        sleep(0.1)  # 等待100毫秒，避免请求过于频繁
        if vod_list:
            result['imgurl'] = str(vod_list)
    elif mid=='':
        print("未找到匹配的刮削信息")
    results.append(result)
print(json.dumps(results, ensure_ascii=False, indent=0))
with open('./results0.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=0)

# 3. 覆盖原文件保存（确保原文件备份，避免数据丢失）
#with open(file_path, "w", encoding="utf-8") as f:
#    json.dump(scrape_data,f,ensure_ascii=False,indent=0)