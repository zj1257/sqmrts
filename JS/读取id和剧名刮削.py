# coding=utf-8
import requests
import re
from time import sleep
import urllib3 # 屏蔽ssl warning
urllib3.disable_warnings(urllib3.connectionpool.InsecureRequestWarning)
import json
from prettytable import PrettyTable

s = requests.Session()
s.headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) quark-cloud-drive/3.0.1 Chrome/100.0.4896.160 Electron/18.3.5.12-a038f7b798 Safari/537.36 Channel/pckk_other_ch',
}
cookies_str = "b-user-id=2fd27d35-d390-8183-fd19-3a4790010e93; isg=BE5OHXRipTijoRGWCBC735OmnyQQzxLJaWu-s3iX_dEM2-w14Fv02SzZEwe3Qwrh; _UP_A4A_11_=wb9c91b81e7a4972bc0b151548c43fa3; _qk_bx_ck_v1=eyJkZXZpY2VJZCI6ImVDeSNBQU9XWHU3blZPQm9lc3JKcUJqS2tUbHg3OEM0ZVdLMmpMekp3OWpFRGVsTVBYUmRCQ20rWk83QnkwTlN2TFBOVjVjPSIsImRldmljZUZpbmdlcnByaW50IjoiNzhhMjg4Y2RlNDcyODk3ZGZlOTI1NTBlNGY2MTY3Y2YifQ==; tfstk=gcbrOHseFzUz5UbzKIYEbr-gIaYJ-U2s8w9Bt6fHNLvu2gs2-16eOU13eMW2yZsSRLwJ86X68Rw_5P1RwFL3CRG5I8vp7BgoZvghiUdQLem__P1RwjcrK5s05Xk5NkXHK9xkmEA6n4clKBv0gBAIED0lKsV2HBnn-QvnomAetpYH-9f0gBpDKjFlZ60213VIpoLiZ-8J4dfk3V5AuQqyQPpm-obDasJGZm0n-ZRy4ZXAja_vVMf9Xa1a8qL5_iYDTwFiYp-NxaTcr-4MDHjFKIIYLDJNx_sOxnPurs8yUhbk4fivzMXR83Ir95CDrtI9B3rYHI755Hv90x2lGsJkbMW7H2v5bsX2fZMj5FjO3w-MSgWipI2qvwIrKD-kMIJ_gSWUNb6wgyQmADnpmFd2C7OSvDKkMIJ_gSoKvnvvgdNWN; __pus=7d626415788422964a91235bd188ce07AAQuPtNiKafO74bHQA8phjBKTVxsuJucRAdm8mg9sFf+0qWOkGrE1cxYVj03hriO2EZlicaF0G3pRiZT7YYrW1gc; __kp=8006ae10-2b43-11f0-8dc6-cf004eb593c5; __kps=AARU7wIFft+ykEyp6z8cXwiv; __ktd=h0g2aJQ0Q9XyVWV9BVhQnQ==; __uid=AARU7wIFft+ykEyp6z8cXwiv; __puus=82d6b04033156bb42265e699df4c12a7AAS2Y5Jg3x98dIfZtjpR2VA7Acu27aiyl4rO9dfRONDxgHSAZ8zckZG4j+mvWPWbh+HlHHCaXxptbkXlcNqGjdatlXo5Ou5qI2narvAz/Fmj9Ls5Xoq5C8/GKF/FaOC5s2Ni+SojKO/c5idVs+BwcooU211fmHT1cSd+xA9K6gIWDN8ruK2naqM8fz1Gp6SWVd/EVLxXlE5oHvINPBvO7zHW"
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
    print(vodList)
    return vodList




# 自动刮削
AUTO = True
print("自动刮削模式") if AUTO else print("手动刮削模式")
count = 1 if AUTO else 20
results = []
data = []
# data = [{'folder':'9cda66af018b490b9afcb6f1ee91d78f','fileName':'螺丝钉 第三季'},
# {'folder':'ecd2c07472704ff68e95b025347c813c','fileName':'平博士密码'}]

if not data:
    datas = getFolder("65b3da4439d04e29b467dd507cfc01f5")
    # with open('results2.json', 'w', encoding='utf-8') as f:
    #     json.dump(datas, f, ensure_ascii=False, indent=4)
    tb = PrettyTable(["序号", "文件夹ID", "文件夹名"])
    for i, data in enumerate(datas):
        tb.add_row([str(i), data['folder'], data['fileName']])
    print(tb)
    index = input("请选择需要刮削的文件夹序号（空格分隔）：")
    if " " in index:
        index = [int(i) for i in index.split(" ")]
    else:
        index = [int(index)]
    data = [datas[i] for i in index]
    print("你选择的文件夹是：")
    tb2 = PrettyTable(tb.field_names)
    for i in index:
        tb2.add_row(tb._rows[i])
    print(tb2)

for row in data:
    result = {}
    result['folder'] = row['folder']
    result['fileName'] = row['fileName']
    file_name = row['fileName']
    mid = scrapeMovieId(file_name)
    vod_list = getScrapeInfos(mid)
    sleep(0.1)  # 等待100毫秒，避免请求过于频繁
    if vod_list:
        result['imgurl'] = str(vod_list)
    results.append(result)



with open('results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run_code = 0