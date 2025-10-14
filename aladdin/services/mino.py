from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad
from Crypto.Protocol.KDF import scrypt
import binascii
import json
import pandas as pd
import requests
import os
import datetime
import asyncio
import httpx
from PIL import Image
from io import BytesIO

import binascii
import json
import pandas as pd


class Mk:
    def __init__(self, key="5358468425923574"):
        # Default key is "5358468425923574"
        self.key = key.encode("utf-8")
        # Assuming IV is the same as the key as in the JS example
        self.iv = self.key

    def encrypt(self, plaintext, key=None):
        if key is None:
            key = self.key

        # 将明文编码为 UTF-8 字节
        data = plaintext.encode("utf-8")

        # 创建 AES cipher 对象，使用 CBC 模式
        cipher = AES.new(key, AES.MODE_CBC, iv=self.iv)

        # 对数据进行填充，以确保它是 AES 块大小的倍数
        padded_data = pad(data, AES.block_size)

        # 使用 AES 进行加密
        ciphertext = cipher.encrypt(padded_data)

        # 返回加密后的数据的十六进制表示
        return binascii.hexlify(ciphertext).decode("utf-8")

    def decrypt(self, ciphertext_hex, key=None):
        if key is None:
            key = self.key

        # Convert ciphertext from hex to bytes
        ciphertext = binascii.unhexlify(ciphertext_hex)

        # Create AES cipher object in CBC mode
        cipher = AES.new(key, AES.MODE_CBC, iv=self.iv)

        # Decrypt and remove padding
        decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)

        # Decode the decrypted bytes to UTF-8 string
        try:
            return decrypted.decode("utf-8")
        except UnicodeDecodeError:
            # If there's a decoding error (e.g., non-UTF-8 content), handle it
            return decrypted.decode("utf-8", errors="replace")


# Example usage:
mk = Mk()

# Encrypted ciphertext (example; should be replaced with actual ciphertext)
# encrypted_text = "f7e0b79e1c0c2f1fa88e9279e75fa40e"

# Decrypt the ciphertext
# decrypted_text = mk.decrypt(encrypted_text_hex)
# print(f"Decrypted Text: {decrypted_text}")


class Mino:
    def __init__(self, key="5358468425923574"):
        # Default key is "5358468425923574"
        self.key = key.encode("utf-8")
        # Assuming IV is the same as the key as in the JS example
        self.iv = self.key
        self.base_url = "https://www.minodata.com/api"
        self.headers = {
            "Accept": "application/json",
            "Authorization": "Bearer",
            "visitorId": "undefined",
            "Cookie": "user=%7B%22balance%22%3A0%2C%22company%22%3A%22%22%2C%22disable%22%3Afalse%2C%22email%22%3A%22%22%2C%22id%22%3A%22%22%2C%22name%22%3A%22%22%2C%22phone%22%3A%22%22%2C%22token%22%3A%22%22%2C%22hasPassword%22%3Afalse%2C%22vipList%22%3A%5B%5D%2C%22type%22%3Afalse%7D",
            "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
            "Content-Type": "application/json",
        }

    def encrypt(self, plaintext, key=None):
        if key is None:
            key = self.key
        data = plaintext.encode("utf-8")
        cipher = AES.new(key, AES.MODE_CBC, iv=self.iv)
        padded_data = pad(data, AES.block_size)
        ciphertext = cipher.encrypt(padded_data)
        return binascii.hexlify(ciphertext).decode("utf-8")

    def decrypt(self, ciphertext_hex, key=None):
        if key is None:
            key = self.key
        ciphertext = binascii.unhexlify(ciphertext_hex)
        cipher = AES.new(key, AES.MODE_CBC, iv=self.iv)
        decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)
        try:
            return decrypted.decode("utf-8")
        except UnicodeDecodeError:
            return decrypted.decode("utf-8", errors="replace")

    def request(self, method="GET", url=None, body=None):
        body = json.dumps(body)
        response = requests.request(method, url, data=body, headers=self.headers)
        try:
            return json.loads(self.decrypt(response.text[1:-1]))
        except:
            return response

    def get_research_list(
        self,
        page=0,
        page_size=10,
        search="",
        date=None,
        order=True,
        company_names=None,
        research_institutes=None,
        agg_order=False,
        svip=False,
    ):
        """获取研报列表
        Args:
            page (int): 页码，从0开始
            page_size (int): 每页数量
            search (str): 搜索关键词
            date (str, optional): 日期筛选
            order (bool): 排序方式
            company_names (list): 公司名称列表
            research_institutes (list): 研究机构列表
            agg_order (bool): 是否聚合排序
            svip (bool): 是否只看SVIP内容
        """
        tags = {}
        if company_names:
            tags["companyName_a"] = company_names
        if research_institutes:
            tags["researchInstitute"] = research_institutes

        search_params = {
            "page": page,
            "pageSize": page_size,
            "search": search,
            "date": date,
            "order": order,
            "tags": tags,
            "aggOrder": agg_order,
            "svip": svip,
        }

        url = f"{self.base_url}/yb/list"
        res = self.request("POST", url, body=search_params)
        print(res)
        df = pd.DataFrame(res["data"]["list"])

        # 补充可能缺失的字段
        default_columns = [
            "docID",
            "IPID",
            "arriveDate",
            "companyName",
            "headline",
            "title",
            "pages",
            "authora",
            "langDesca",
            "inda",
            "companyName_a",
            "rptStylesRespa",
            "is_svip",
            "oid",
            "langDesca_zh",
            "rptStylesRespa_zh",
            "companyName_zh",
            "img",
            "search",
            "inda_zh",
            "rptStylesRespa_colour",
            "companyName_a_zh",
            "table_count",
            "figure_count",
            "summary",
            "word_count",
            "text",
            "is_ocr",
        ]

        for col in default_columns:
            if col not in df.columns:
                df[col] = None

        return df

    def get_company_list(self, search_keyword, page=0):
        """获取公司列表"""
        url = f"{self.base_url}/yb/tags/companyName_a"
        params = {"search": search_keyword, "page": page}
        response = requests.get(url, params=params, headers=self.headers)
        try:
            return json.loads(self.decrypt(response.text[1:-1]))
        except:
            return response.json()

    def get_image_url(self, doc_id, arrive_date, page, zoom, exp):
        """生成图片预览URL"""
        time = datetime.datetime.now().timestamp()
        payload = {
            "id": doc_id,
            "date": arrive_date,
            "page": page,
            "zoom": zoom,
            "exp": exp,
            "time": time,
        }
        preview_id = self.encrypt(json.dumps(payload))
        return f"{self.base_url}/yb/preview?id={preview_id}"

    async def download_image(self, client, url, save_path):
        """异步下载图片"""
        try:
            response = await client.get(url, timeout=10.0)
            if response.status_code == 200:
                img_data = response.content
                image = Image.open(BytesIO(img_data))
                image.save(save_path)
                print(f"Downloaded page to {save_path}")
            else:
                print(
                    f"Failed to download image from {url} with status {response.status_code}"
                )
        except Exception as e:
            print(f"Error downloading image from {url}: {str(e)}")

    def merge_images_to_pdf(self, image_paths, output_pdf_path):
        """合并图片为PDF"""
        images = [Image.open(img_path) for img_path in image_paths]
        images[0].save(
            output_pdf_path,
            save_all=True,
            append_images=images[1:],
            resolution=100.0,
            quality=95,
        )
        print(f"PDF saved to {output_pdf_path}")

    async def download_pdf(self, research_info):
        """下载研报PDF"""
        doc_id = research_info["docID"]
        arrive_date = research_info["arriveDate"]
        total_pages = research_info["pages"]
        zoom = 2
        output_pdf_path = research_info["headline"] + ".pdf"
        image_dir = str(doc_id)
        exp = 60

        if not os.path.exists(image_dir):
            os.makedirs(image_dir)

        image_paths = []

        async with httpx.AsyncClient(verify=False) as client:
            tasks = []
            for page in range(total_pages):
                url = self.get_image_url(doc_id, arrive_date, page, zoom, exp)
                image_path = os.path.join(image_dir, f"page_{page}.jpg")
                tasks.append(self.download_image(client, url, image_path))
                image_paths.append(image_path)

            await asyncio.gather(*tasks)

        self.merge_images_to_pdf(image_paths, output_pdf_path)


# 使用示例:
"""
# 初始化Mino类
mino = Mino()

# 搜索研报列表
df = mino.get_research_list(
    page=0,
    page_size=10,
    search="新能源",
    company_names=["蔚来", "比亚迪"],
    research_institutes=["中信证券", "国泰君安"]
)

# 下载第一篇研报
research_info = df.iloc[0].to_dict()
await mino.download_pdf(research_info)

# 搜索公司
companies = mino.get_company_list("蔚来")
print(companies)
"""
