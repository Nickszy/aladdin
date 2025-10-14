from typing import List, Optional
from aladdin.models.yb import IfindYb
from aladdin.templates import template
import reflex as rx
from aladdin.pages.news.yb.index import YbState  # 添加导入
import reflex_chakra as rc


def report_list_component(title: str, yb_list: List[Optional[IfindYb]]) -> rx.Component:
    """相关研报组件"""
    # 设置默认标题值
    if title == "":
        title = "相关研报"

    return rx.hstack(
        # 同公司其他研报
        rx.vstack(
            rc.heading(title, size="md"),
            rx.cond(
                yb_list.length() > 0,
                rx.foreach(
                    yb_list,
                    lambda yb: rc.card(
                        rx.vstack(
                            rc.heading(
                                rx.cond(
                                    yb.code,
                                    f"{yb.code}:{yb.title}",
                                    yb.title,
                                ),
                                size="sm",
                            ),
                            rx.hstack(
                                rc.text(yb.f007v_yb003, font_size="sm"),
                                rc.text(yb.declaredate, font_size="sm"),
                                spacing="2",
                            ),
                            on_click=YbState.view_yb_detail(yb.seq),
                            spacing="2",
                        ),
                        width="100%",
                        variant="outline",
                    ),
                ),
                rc.text("暂无相关研报"),
            ),
            width="100%",
        ),
        width="100%",
        min_width="250px",
        spacing="6",
    )


@template(
    route="/yb/[search_id]",
    title="研报详情",
    on_load=[YbState.yb_search],
)
def yb_detail() -> rx.Component:
    """研报详情区域"""
    if YbState.search_id is None:
        return rx.redirect("/yb")
    return rx.cond(
        YbState.selected_yb,
        rx.grid(
            # 返回按钮
            rx.vstack(
                rx.hstack(
                    rc.button(
                        "← 返回列表",
                        on_click=YbState.back_to_list,
                        color_scheme="gray",
                        variant="outline",
                    ),
                    width="100%",
                    justify="start",
                ),
                # 研报基本信息
                rc.card(
                    rx.vstack(
                        rc.heading(
                            rx.cond(
                                YbState.selected_yb.code,
                                f"{YbState.selected_yb.code}:{YbState.selected_yb.title}",
                                YbState.selected_yb.title,
                            ),
                            size="lg",
                        ),
                        rx.grid(
                            rx.hstack(
                                rc.text("机构:", font_weight="bold"),
                                rc.text(YbState.selected_yb.f006v_yb003),
                            ),
                            rx.hstack(
                                rc.text("作者:", font_weight="bold"),
                                rc.text(YbState.selected_yb.f007v_yb003),
                            ),
                            rx.hstack(
                                rc.text("行业分类:", font_weight="bold"),
                                rc.text(YbState.selected_yb.hangye1),
                            ),
                            rx.hstack(
                                rc.text("发布日期:", font_weight="bold"),
                                rc.text(YbState.selected_yb.declaredate),
                            ),
                            columns="2",
                            spacing="4",
                            width="100%",
                        ),
                        rc.button(
                            "下载研报",
                            on_click=rx.download(
                                url=rx.cond(
                                    YbState.selected_yb.f012v_yb003,
                                    f"http://154.85.57.45/yb/{YbState.selected_yb.declaredate.to(str).replace('-', '')}/{YbState.selected_yb.f012v_yb003}.pdf?user=OmNweXM6Ojo6Ojo6Ojo2NTI4MDE6MTc0Mjc5MDc1MTo6Ojo4NjQwMDo6cGF6cV96bnR5MDAyMzE%3D&ticket=608ba05be83cc1e80ab75578691a2d00&source=cGF6cV96bnR5&fname={YbState.selected_yb.f012v_yb003},{YbState.selected_yb.code}%20({YbState.selected_yb.secname}):%20{YbState.selected_yb.title}",
                                    2,  # f"http://154.85.57.45/yb/{YbState.selected_yb.declaredate.replace('-', '')}/{YbState.selected_yb.f012v_yb003}.pdf?user=OmNweXM6Ojo6Ojo6Ojo2NTI4MDE6MTc0Mjc5MDc1MTo6Ojo4NjQwMDo6cGF6cV96bnR5MDAyMzE%3D&ticket=608ba05be83cc1e80ab75578691a2d00&source=cGF6cV96bnR5&fname={YbState.selected_yb.f012v_yb003},{YbState.selected_yb.title}"
                                ),
                                # url="/reflex_banner.png",
                                filename=YbState.selected_yb.f006v_yb003
                                + ":"
                                + YbState.selected_yb.title
                                + ".pdf",
                            ),
                            color_scheme="blue",
                            variant="outline",
                        ),
                        spacing="4",
                    ),
                    width="100%",
                ),
                # 研报摘要
                rc.card(
                    rx.vstack(
                        rc.heading("摘要", size="md"),
                        rc.text(YbState.selected_yb.f010v_yb003, whiteSpace="pre-wrap"),
                        spacing="3",
                        width="100%",
                    ),
                ),
                width="100%",
            ),
            # 相关推荐
            rx.hstack(
                report_list_component("同分析师的其他研报", YbState.related_by_author),
                report_list_component("同公司的其他研报", YbState.related_by_org),
            ),
            spacing="5",
            direction="row",
            # 修改模板列，使相关推荐只占30%
            template_columns="70% 30%",
            width="100%",
        ),
        # 如果没有选中研报，显示空状态
        rx.vstack(),
    )
