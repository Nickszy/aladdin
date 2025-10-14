import reflex as rx

"""
https://www.npmjs.com/package/react-pdf

"""
from typing import Callable

from reflex.event import EventHandler, no_args_event_spec


class Page(rx.Component):

    library = "react-pdf@^8.0.2"

    tag = "Page"

    is_default = False

    pageNumber: rx.Var[int] = 1

    scale: rx.Var[float] = 1
    width = "100%"

    # width: rx.Var[str] = "100%"  # 页面宽度自适应父容器


from reflex.vars.object import ObjectVar


class Document(rx.Component):

    library = "react-pdf@^8.0.2"

    tag = "Document"

    is_default = False

    file: rx.Var[str] = None

    numPages: rx.Var[int] = None

    width: rx.Var[str] = "100%"

    on_load_success: rx.EventHandler[lambda e0: [e0]]

    options = {
        "httpHeaders": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
            "Referrer-Policy": "no-referrer-when-downgrade",
        }
    }

    # pdfjs.GlobalWorkerOptions.workerSrc = {
    #     'cMapUrl': 'https://cdn.jsdelivr.net/npm/pdfjs-dist@latest/build/pdf.worker.min.mjs'
    # }
    def _get_custom_code(self) -> str:
        return """
        import { pdfjs } from 'react-pdf';
        pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/legacy/build/pdf.worker.min.js`;        
        pdfjs.disableWorker = true;
        import 'react-pdf/dist/Page/TextLayer.css';
        import 'react-pdf/dist/Page/AnnotationLayer.css';
        """


class PdfViewer(rx.ComponentState):
    title: str
    url: str = None
    num_pages = 1
    scroll_to: str = "1"  # 0 表示不滚动
    scale: str = "100%"
    scale_num: float = 1
    count: int = 0
    screen_width: int = 0  # 存储屏幕宽度

    def get_screen_width(self, width: int):
        """更新屏幕宽度到状态"""
        self.screen_width = width

    def set_scale(self, scale):

        self.scale = scale
        self.scale_num = float(scale[:-1]) / 100

    def handle_load_success(self, num_pages):
        """处理 PDF 加载成功事件"""
        # event 是 React 传递的事件对象，包含 numPages 属性
        self.num_pages = num_pages  # 提取总页数并更新状态
        # self.page_number = 1  # 重置当前页为第一页

    @classmethod
    def get_component(cls, **props):
        # Access the state vars and event handlers using `cls`.
        cls.title = props.get("title", "PDF Viewer")
        cls.url = props.get("url", None)
        pdf = document(
            rx.foreach(
                rx.Var.range(cls.num_pages),
                lambda i: page(
                    pageNumber=i + 1,
                    id=f"page-{i+1}",
                    scale=cls.scale_num,
                ),
            ),
            file=cls.url,
            on_load_success=lambda ev: cls.handle_load_success(ev["numPages"]),
            id="pdf-viewer",
        )
        return rx.vstack(
            rx.heading(cls.title, align="left"),
            rx.box(
                pdf,
                display="flex",
                justify_content="center",
                max_height="80vh",
                overflow_y="scroll",
                border="1px solid #ddd",
                padding_left="0",
                padding_right="0",
                width="100%",
            ),
            rx.flex(
                rx.hstack(
                    # 缩放pdf大小
                    rx.text("缩放:"),
                    rx.select(
                        ["25%", "50%", "75%", "100%", "150%", "200%", "300%"],
                        value=cls.scale,
                        type="string",
                        on_change=cls.set_scale,
                        width="100px",
                    ),
                    align="center",
                ),
                rx.hstack(
                    # rx.text(f"第"),
                    # rx.input(
                    #     value=pdf.numPages,
                    #     type="int",
                    #     on_change=pdf.set_num_pages,
                    #     width="30px",
                    # ),
                    rx.text(f"共{cls.num_pages}页"),
                ),
                justify="between",
                width="100%",
            ),
            width="100%",  # 让整体宽度 100%
            # # 当 scroll_to 改变时自动滚动
            # on_mount=rx.scroll_to(
            #     element_id=f"page-{pdfState.scroll_to}", behavior="smooth"
            # ),
            # on_mount=rx.scroll_to(elem_id=f"page-{pdfState.scroll_to}"),
        )


document = Document.create
page = Page.create
pdfviewer = PdfViewer.create
