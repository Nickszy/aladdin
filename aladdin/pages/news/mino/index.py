from typing import List
from aladdin.services.mino import Mino
from aladdin.templates import template
import reflex as rx


class minostate(rx.State):
    yb_list: str = ""
    search_company: str = ""
    company: str = ""
    page: int = 1

    def load_yb_data(self) -> None:
        self.search(self.page)

    def set_search_company(self, company: str) -> None:
        mino = Mino()
        self.search_company = mino.get_company_list(company)["data"]

    def search(self, page: int) -> None:
        mino = Mino()
        self.yb_list = mino.get_research_list(
            page=page,
            page_size=10,
            company_names=[self.company],
            # research_institutes=["中信证券", "国泰君安"],
        ).to_html()


def yb_filter_section() -> rx.Component:
    return rx.box(
        rx.heading("筛选条件"),
        rx.vstack(
            rx.input(
                placeholder="输入公司名称",
                on_blur=minostate.set_search_company,
            ),
            rx.text("mino 查询:", minostate.search_company),
            rx.input(placeholder="公司", on_blur=minostate.set_company),
            rx.button("查询", on_click=minostate.load_yb_data),
            spacing="4",
        ),
    )


def yb_list_section() -> rx.Component:
    return rx.box(
        rx.heading("研报列表"),
        rx.vstack(
            rx.html(minostate.yb_list),
            spacing="4",
        ),
    )


@template(
    route="/mino",
    title="mino研报查询",
    on_load=[
        minostate.load_yb_data,
    ],
)
def mino_page() -> rx.Component:
    return rx.box(
        rx.heading("mino"),
        rx.vstack(
            yb_filter_section(),
            yb_list_section(),
            spacing="4",
        ),
    )
