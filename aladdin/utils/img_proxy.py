import re
from typing import List, Dict, Optional, TypedDict

IMAGE_PROXY_URL = "https://webp.follow.is"


class RefererRule(TypedDict, total=False):
    url: re.Pattern[str]
    referer: str
    force: bool


class WebpCloudRule(TypedDict):
    url: re.Pattern[str]
    target: str


# 预编译正则，提升性能
image_referer_matches: List[RefererRule] = [
    {"url": re.compile(r"^https://\w+\.twimg\.com"), "referer": "https://x.com"},
    {"url": re.compile(r"^https://\w+\.sinaimg\.cn"), "referer": "https://weibo.com"},
    {"url": re.compile(r"^https://i\.pximg\.net"), "referer": "https://www.pixiv.net"},
    {
        "url": re.compile(r"^https://cdnfile\.sspai\.com"),
        "referer": "https://sspai.com",
    },
    {
        "url": re.compile(r"^https://(?:\w|-)+\.cdninstagram\.com"),
        "referer": "https://www.instagram.com",
    },
    {
        "url": re.compile(r"^https://sp1\.piokok\.com"),
        "referer": "https://www.piokok.com",
        "force": True,
    },
    {
        "url": re.compile(r"^https?://[\w-]+\.xhscdn\.com"),
        "referer": "https://www.xiaohongshu.com",
    },
]

webp_cloud_public_services_matches: List[WebpCloudRule] = [
    {
        "url": re.compile(r"^https://avatars\.githubusercontent\.com/u/"),
        "target": "https://avatars-githubusercontent-webp.webp.se/u/",
    },
]


def get_image_proxy_url(
    *, url: str, width: Optional[int] = None, height: Optional[int] = None
) -> str:
    """生成代理地址"""
    w = str(round(width)) if width is not None else ""
    h = str(round(height)) if height is not None else ""
    return f"{IMAGE_PROXY_URL}?url={__import__('urllib.parse').parse.quote(url)}&width={w}&height={h}"


def replace_img_url_if_need(
    *, url: Optional[str], in_browser: bool = True
) -> Optional[str]:
    """根据规则替换图片地址"""
    if not url:
        return url

    # 1. 优先走 webp.cloud 公共服务
    for rule in webp_cloud_public_services_matches:
        if rule["url"].match(url):
            return rule["url"].sub(rule["target"], url)

    # 2. 需要代理的站点
    for rule in image_referer_matches:
        if (in_browser or rule.get("force", False)) and rule["url"].match(url):
            return get_image_proxy_url(url=url, width=0, height=0)

    return url


from bs4 import BeautifulSoup
from aladdin.utils.logger import log_info


def process_img_src_in_html(html: str, in_browser: bool = True) -> str:
    if html:
        soup = BeautifulSoup(html, "html.parser")
        for img in soup.find_all("img"):
            original_src = img.get("src")
            if original_src:
                new_src = replace_img_url_if_need(
                    url=original_src, in_browser=in_browser
                )
                if new_src:
                    img["src"] = new_src
        return str(soup)
    return ""


# --------- 使用示例 ---------
if __name__ == "__main__":
    test_urls = [
        "https://avatars.githubusercontent.com/u/123456",
        "https://i.pximg.net/img-original/img/2021/12/31/12345678_p0.jpg",
        "https://cdnfile.sspai.com/2022/03/abc.png",
        "https://example.com/normal.jpg",
    ]
    for u in test_urls:
        log_info(f"{u} -> {replace_img_url_if_need(url=u, in_browser=True)}")
