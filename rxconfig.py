import reflex as rx

config = rx.Config(
    app_name="aladdin",
    frontend_port=3002,
    backend_port=8032,
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ],
)
