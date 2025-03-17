import reflex as rx
from .components.theme_wrap import theme_wrap

def index():
    return theme_wrap(
        rx.center(
            rx.card(
                rx.flex(
                    rx.flex(
                        rx.icon(
                            "sparkles",
                            width="4em",
                            height="auto",
                        ),
                        rx.spacer(),
                        rx.heading(
                            "Text2SQL",
                            size="9",
                            weight="medium",
                            trim="both",
                        ),
                        align="center",
                        justify="center",
                        padding_x="0.5rem",
                        width="100%",
                    ),
                    rx.button(
                        "开始使用",
                        on_click=rx.redirect("/login"),
                        size="4",
                        width="100%",
                    ),
                    direction="column",
                    align="center",
                    justify="center",
                    spacing="7",
                    padding="32px",
                    width="410px",
                ),
            ),
            width="100%",
            height="100vh",
        )
    )