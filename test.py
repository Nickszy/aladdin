import requests
import json
from aladdin.utils.logger import log_info

url = "https://ims.hzbank.com.cn:9110/investManage/mpss/mpor/dingding/listStaffPage"

# 请求体
payload = ["1976243126375874561"]

# 请求头（把浏览器里粘过来的原样放进来即可）
headers = {
    "accept": "application/json, text/plain, */*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "connection": "keep-alive",
    "content-type": "application/json;charset=UTF-8",
    "Cookie": "appNo=1655; operType=00; userRole=0; alias=æ²ˆå“²å®‡; operNo=219838; opInfoKey=MCMC_LOGIN219838; token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyICAgICAgICAgICAgPGV4Y2x1c2lvbnM-XG4gICAgICAgICAgICAgICAgPGV4Y2x1c2lvbj5cbiAgICAgICAgICAgICAgICAgICAgPGdyb3VwSWQ-b3JnLmFwYWNoZS5sb2dnaW5nLmxvZzRqPC9ncm91cElkPlxuICAgICAgICAgICAgICAgICAgICA8YXJ0aWZhY3RJZD5sb2c0ai1zbGY0ai1pbXBsPC9hcnRpZmFjdElkPlxuICAgICAgICAgICAgICAgIDwvZXhjbHVzaW9uPlxuICAgICAgICAgICAgPC9leGNsdXNpb25zPk5hbWUiOiIyMTk4MzgiLCJ0b2tlbiI6ImMyNjYzNzM2LTcwNTUtNDhkYi05MjQxLTdmY2I0ZjBlZGMzZSIsImV4cCI6MTc2MDcwNzAyMn0.0ILHKs8RoRgIcgyKzYSGTIP5GFote3PYv2J00b6ppTE; locale=zh-CN; _gcl_au=1.1.465737462.1758597504; _gid=GA1.3.1228925942.1760578955; _ga=GA1.1.1521642238.1735889213; _ga_VPYRHN104D=GS2.1.s1760578955$o2$g1$t1760578980$j35$l0$h0; free.session.id=c2663736-7055-48db-9241-7fcb4f0edc3e",
    "host": "ims.hzbank.com.cn:9110",
    "origin": "https://ims.hzbank.com.cn:9110",
    "referer": "https://ims.hzbank.com.cn:9110/investManage/web/",
    "sec-ch-ua": '"Microsoft Edge";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0",
}

# 如果本地开了代理，保持跟浏览器一致；否则把 proxies 删掉
# proxies = {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}

resp = requests.post(
    url,
    data=json.dumps(payload),  # 等价于 json=payload
    headers=headers,
    # proxies=proxies,
    timeout=10,
)

log_info(f"状态码: {resp.status_code}")
log_info(f"响应头: {resp.headers}")
log_info(f"响应体: {resp.text}")
