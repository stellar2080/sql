import reflex as rx

from state.settings_st import SettingsState

def appearance_picker() -> rx.Component:
    return (
        rx.hstack(
            rx.icon("moon-star"),
            rx.heading("深色模式", size="6"),
            rx.color_mode.switch(
                size='3',
            ),
            align="center",
            width="100%",
        ),
    )
