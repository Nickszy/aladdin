# http://img.nickszy.com/obsidian/1001273295188370-6-20250731-1754575533531.pdf


from aladdin.components.pdf import pdfviewer
import reflex as rx

from aladdin.templates import template


@template(route="/pdf", title="pdf")
def pdf():
    return rx.box(
        pdfviewer(
            title="富途结单",
            url="http://img.nickszy.com/obsidian/1001273295188370-6-20250731-1754575533531.pdf",
            display="flex",
            justify_content="center",
        ),
        width="100%",
    )
