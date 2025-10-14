# ## 飞书云文档组件
# # 先开发一个云文档组件

# from reflex.components.component import Component
# from reflex.vars import Var, LiteralVar
# from reflex import field


# class FeishuDocComponent(Component):
#     """飞书云文档组件"""

#     # 组件库及依赖
#     library = "https://sf1-scmcdn-cn.feishucdn.com/obj/feishu-static/docComponentSdk/lib/1.0.3.js"

#     # 文档源地址
#     src: rx.Var[str] = None
#     # 认证信息
#     app_id: rx.Var[str]
#     open_id: rx.Var[str]
#     signature: rx.Var[str]
#     timestamp: rx.Var[str]
#     nonce_str: rx.Var[str]
#     url: rx.Var[str]
#     js_api_list: rx.Var[list[str]]

#     @classmethod
#     def create(cls, **props) -> Component:
#         """创建组件实例"""
#         # 创建一个容器用于挂载文档组件
#         container = rx.box(
#             id="doc-pos",
#             width="100%",
#             min_height="600px",
#         )

#         # 添加初始化脚本
#         init_script = rx.script(
#             """
#                 <!--在网页 html 中-->
#                 <script src="https://sf1-scmcdn-cn.feishucdn.com/obj/feishu-static/docComponentSdk/lib/1.0.3.js"></script>
#                 """
#         )

#         # 返回包含容器和初始化脚本的组件
#         # return rx.script(
#         #     """
#         # myComponent = new window.DocComponentSdk({
#         # src: "https://bytedance.feishu.cn/docx/RVx9dHXxMonmtVxTA3UcjHunnCu",
#         # mount: document.querySelector('#doc-pos'),  // 将组件挂在到哪个元素上
#         # auth: {
#         #     {openId},    # 当前登录用户的open id，要确保与生成 signature 使用的 user_access_token 相对应，使用 app_access_token 时此项不填。
#         #     {signature}, // 签名
#         #     {appId},     // 应用 appId
#         #     {timestamp}, // 时间戳（毫秒）
#         #     {nonceStr},  // 随机字符串
#         #     {url},       // 参与签名加密计算的url
#         #     {jsApiList}, // 指定要使用的组件，请根据对应组件的开发文档填写。如云文档组件，填写['DocsComponent']
#         # },
#         # });
#         # myComponent.start().then(() => {
#         # });

#         # // 销毁组件
#         # myComponent.destroy()
#         # """
#         # )
#         return rx.text("feishudoc")


# feishuDoc = FeishuDocComponent.create
