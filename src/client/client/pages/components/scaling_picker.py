import reflex as rx

from state.settings_st import SettingsState


def scaling_picker() -> rx.Component:
    return (
        rx.vstack(
            rx.hstack(
                rx.icon("ruler"),
                rx.heading("比例大小", size="6"),
                align="center",
            ),
            rx.select(
                [
                    "90%",
                    "95%",
                    "100%",
                    "105%",
                    "110%",
                ],
                size="3",
                value=SettingsState.scaling,
                on_change=SettingsState.set_scaling,
            ),
            width="100%",
        ),
    )
