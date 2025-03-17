import reflex as rx

from state.theme_st import ThemeState

def radius_picker() -> rx.Component:
    return (
        rx.vstack(
            rx.hstack(
                rx.icon("radius"),
                rx.heading("圆角大小", size="6"),
                align="center",
            ),
            rx.select(
                [
                    "none",
                    "small",
                    "medium",
                    "large",
                    "full",
                ],
                size="3",
                value=ThemeState.radius,
                on_change=ThemeState.set_radius,
            ),
            width="100%",
        ),
    )
