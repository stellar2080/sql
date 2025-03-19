import reflex as rx

from state.base_st import BaseState


def scaling_picker() -> rx.Component:
    return (
        rx.vstack(
            rx.hstack(
                rx.icon("ruler"),
                rx.heading("比例大小", size="5"),
                align="center",
            ),
            rx.select(
                [
                    "100%",
                    "105%",
                    "110%",
                ],
                size="3",
                value=BaseState.scaling,
                on_change=BaseState.set_scaling,
            ),
            width="100%",
        ),
    )
