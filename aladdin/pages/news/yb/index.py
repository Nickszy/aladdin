from typing import List, Optional
import reflex as rx
from sqlmodel import Session
from datetime import date

from aladdin.templates import template
from aladdin.models.yb import IfindYb
from aladdin.services.yb_service import YbService
from aladdin.db import wewe_engine as engine
import reflex_chakra as rc


class YbState(rx.State):
    # 筛选条件
    org_filter: str = ""
    author_filter: str = ""
    industry_filter: str = ""
    date_filter: str = ""
    company_filter: str = ""

    # 数据列表
    yb_list: List[IfindYb] = []
    total_count: int = 1000

    # 分页
    current_page: int = 1
    page_size: int = 20

    # 下拉选项
    org_options: List[str] = [
        "中金公司",
        "中信证券",
        "华泰证券",
        "国泰君安",
        "海通国际",
    ]
    author_options: List[str] = ["刘伟", "张三", "要文强"]
    industry_options: List[str] = []

    # 详情页相关
    selected_yb: Optional[IfindYb] = None
    related_by_author: List[IfindYb] = []
    related_by_org: List[IfindYb] = []

    @rx.event
    def load_yb_data(self) -> None:
        """加载研报数据"""
        with Session(engine) as session:
            service = YbService(session)
            offset = (self.current_page - 1) * self.page_size
            self.yb_list = service.get_yb_list(
                org=self.org_filter if self.org_filter else None,
                author=self.author_filter if self.author_filter else None,
                industry=self.industry_filter if self.industry_filter else None,
                code=self.company_filter if self.company_filter else None,
                declare_date=(
                    date.fromisoformat(self.date_filter) if self.date_filter else None
                ),
                offset=offset,
                limit=self.page_size,
            )

    @rx.event
    def yb_search(self):
        with Session(engine) as session:
            service = YbService(session)
            self.selected_yb = service.get_yb_list(
                id=self.search_id,
            )[0]

    @rx.event
    def load_filter_options(self) -> None:
        """加载筛选选项"""
        with Session(engine) as session:
            service = YbService(session)
            #     self.org_options = service.get_all_orgs()
            #     self.author_options = service.get_all_authors()
            self.industry_options = service.get_all_industries()

    @rx.event
    def apply_filters(self) -> None:
        """应用筛选条件"""
        self.current_page = 1
        self.load_yb_data()

    @rx.event
    def reset_filters(self) -> None:
        """重置筛选条件"""
        self.org_filter = ""
        self.author_filter = ""
        self.industry_filter = ""
        self.date_filter = ""
        self.company_filter = ""
        self.current_page = 1
        self.load_yb_data()

    @rx.event
    def set_page(self, page: int) -> None:
        """设置页码"""
        self.current_page = page
        self.load_yb_data()

    @rx.event
    def view_yb_detail(self, yb_id: int) -> rx.Component:
        """查看研报详情"""
        with Session(engine) as session:
            service = YbService(session)
            self.selected_yb = service.get_yb_list(id=yb_id)[0]
            if self.selected_yb:
                # 获取相关分析师的其他研报(最多5条)
                self.related_by_author = service.get_yb_list(
                    author=self.selected_yb.f007v_yb003, limit=5
                )
                # 获取同公司其他研报(最多5条)
                if self.selected_yb.code:
                    self.related_by_org = service.get_yb_list(
                        code=self.selected_yb.code, limit=5
                    )
                else:
                    self.related_by_org = service.get_yb_list(
                        industry=self.selected_yb.hangye1, limit=5
                    )
        return rx.redirect(f"/yb/{yb_id}", is_external=True)

    @rx.event
    def back_to_list(self) -> rx.Component:
        """返回列表页"""
        self.selected_yb = None
        self.related_by_author = []
        self.related_by_org = []
        return rx.redirect("/yb")


def yb_filter_section() -> rx.Component:
    """研报筛选区域"""
    return rc.card(
        rx.vstack(
            rc.heading("研报筛选", size="md"),
            rx.grid(
                rx.hstack(
                    rc.text("机构", min_width="fit-content"),
                    rc.select(
                        YbState.org_options,
                        placeholder="选择机构",
                        on_change=YbState.set_org_filter,
                        value=YbState.org_filter,
                    ),
                    width="100%",
                    align="center",
                ),
                rx.hstack(
                    rc.text("作者", min_width="fit-content"),
                    rc.select(
                        YbState.author_options,
                        placeholder="选择作者",
                        on_change=YbState.set_author_filter,
                        value=YbState.author_filter,
                    ),
                    width="100%",
                    align="center",
                ),
                rx.hstack(
                    rc.text("行业分类", min_width="fit-content"),
                    rc.select(
                        YbState.industry_options,
                        placeholder="选择行业",
                        on_change=YbState.set_industry_filter,
                        value=YbState.industry_filter,
                    ),
                    align="center",
                    width="100%",
                ),
                rx.hstack(
                    rc.text("公司名称"),
                    rc.input(
                        placeholder="输入股票简称",
                        on_change=YbState.set_company_filter,
                        value=YbState.company_filter,
                    ),
                    align="center",
                    width="100%",
                ),
                # rx.vstack(
                #     rc.text("发布日期"),
                #     rc.input(
                #         placeholder="选择日期",
                #         type="date",
                #         on_change=YbState.set_date_filter,
                #         value=YbState.date_filter,
                #     ),
                #     width="100%",
                # ),
                # columns=["1", "2"],
                spacing="4",
                width="100%",
                columns="3",
            ),
            rx.hstack(
                rc.button(
                    "应用筛选", on_click=YbState.apply_filters, color_scheme="blue"
                ),
                rc.button(
                    "重置筛选", on_click=YbState.reset_filters, color_scheme="gray"
                ),
                spacing="3",
            ),
            spacing="4",
        ),
        width="100%",
    )


def yb_list_section() -> rx.Component:
    """研报列表区域"""
    return rx.vstack(
        # 修改为表格形式展示研报列表
        rc.table_container(
            rc.table(
                rc.thead(
                    rc.tr(
                        rc.th("标题", width="400px"),
                        rc.th("机构"),
                        rc.th("作者"),
                        rc.th("行业分类"),
                        rc.th("页数"),
                        rc.th("发布日期"),
                        rc.th("操作"),
                        # rc.th("摘要"),
                    )
                ),
                rc.tbody(
                    rx.foreach(
                        YbState.yb_list,
                        lambda yb: rc.tr(
                            rc.td(
                                rx.cond(
                                    yb.code,
                                    f"{yb.code}:{yb.title}",
                                    yb.title,
                                )
                                | ""
                            ),
                            rc.td(yb.f006v_yb003),
                            rc.td(yb.f007v_yb003),
                            rc.td(yb.hangye1),
                            rc.td(yb.f009n_yb003),
                            rc.td(yb.declaredate),
                            rc.td(
                                rc.button(
                                    "查看详情",
                                    on_click=YbState.view_yb_detail(yb.seq),
                                    size="sm",
                                    color_scheme="blue",
                                )
                            ),
                            # rc.td(yb.f010v_yb003 | ""),
                        ),
                    )
                ),
                size="sm",
                max_width="100%",
                # variant="striped",
            ),
            width="100%",
            # max_width="1200px",
        ),
        rx.hstack(
            rc.button(
                "上一页",
                on_click=YbState.set_page(YbState.current_page - 1),
                is_disabled=YbState.current_page <= 1,
                size="sm",
            ),
            rc.text(f"第 {YbState.current_page} 页"),
            rc.button(
                "下一页",
                on_click=YbState.set_page(YbState.current_page + 1),
                size="sm",
                is_disabled=YbState.current_page
                >= YbState.total_count / YbState.page_size,
                # 简化处理，实际应根据总数判断
            ),
            justify="center",
            align="center",
            spacing="4",
            width="100%",
        ),
        spacing="4",
        width="100%",
    )


@template(
    route="/yb",
    title="研报详情",
    on_load=[
        YbState.load_yb_data,
        YbState.load_filter_options,
    ],
)
def yb_page() -> rx.Component:
    """研报查询页面"""
    return rx.flex(
        rx.heading("研报查询", size="7"),
        # 只在未选择研报时显示筛选和列表区域
        rx.vstack(yb_filter_section(), yb_list_section(), width="100%"),
        direction="column",
        spacing="5",
        width="100%",
    )
