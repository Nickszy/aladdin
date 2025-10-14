"""Welcome to Reflex!."""

# Import all the pages.
import reflex as rx
from . import styles
from .pages import *
from aladdin.api import fastapi_app

# Create the app.
app = rx.App(
    style=styles.base_style,
    stylesheets=styles.base_stylesheets,
    api_transformer=fastapi_app,
)
