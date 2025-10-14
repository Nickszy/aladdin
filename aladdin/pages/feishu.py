"""The about page."""

from pathlib import Path
import time

import reflex as rx

from .. import styles
from ..templates import template


# 然后在系统中引用一下


@template(route="/feishu", title="feishudoc")
def feishudoc() -> rx.Component:
    """The about page.

    Returns:
        The UI for the about page.
    """
    return rx.flex(
        rx.text(rx.State.router.page.host, size="6", weight="bold"),
        rx.box(
            "这里是指定的 #doc-pos 盒子",
            id="doc-pos",  # 生成 <div id="doc-pos"> … </div>
            bg="gray.100",
            p="6",
            border_radius="lg",
            shadow="md",
        ),
        rx.script(
            src="https://sf1-scmcdn-cn.feishucdn.com/obj/feishu-static/docComponentSdk/lib/1.0.3.js"
        ),
        rx.script("console.log('inline javascript')"),
        # rx.script(
        #     """
        #         myComponent = new window.DocComponentSdk({
        #         src: "https://snow-360.feishu.cn/wiki/MSSowJ40yiQpyfkAsGichANpne0",
        #         mount: document.querySelector('#doc-pos'),  // 将组件挂在到哪个元素上
        #         auth: {
        #             openId,    // 当前登录用户的open id，要确保与生成 signature 使用的 user_access_token 相对应，使用 app_access_token 时此项不填。
        #             signature, // 签名
        #             appId,     // 应用 appId
        #             timestamp, // 时间戳（毫秒）
        #             nonceStr,  // 随机字符串
        #             url,       // 参与签名加密计算的url
        #             jsApiList, // 指定要使用的组件，请根据对应组件的开发文档填写。如云文档组件，填写['DocsComponent']
        #         },
        #         });
        #         myComponent.start().then(() => {
        #         });
        # """
        # ),
    )
