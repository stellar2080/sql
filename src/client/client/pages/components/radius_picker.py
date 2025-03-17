import reflex as rx

from state.settings_st import SettingsState

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
                value=SettingsState.radius,
                on_change=SettingsState.set_radius,
            ),
            width="100%",
        ),
    )
