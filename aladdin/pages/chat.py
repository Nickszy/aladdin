from reflex_chat import chat, api
import reflex as rx

chat1 = chat()
from ..templates import template


@template(route="/chat", title="chat")
def index() -> rx.Component:
    return rx.box(
        rx.box(
            chat(
                process=api.openai(
                    model="reflex",
                    url="https://u9ec3f0p2fj6vobt.ai-plugin.io",
                    key="123456",
                )
            ),
            height="90vh",
            width="100%",
        ),
        size="2",
        width="100%",
    )
