from client.state.base_st import BaseState
import reflex as rx

def theme_wrap(component: rx.Component) -> rx.Component:
    return rx.theme(
        component,
        has_background=True,
        accent_color=BaseState.accent_color,
        gray_color=BaseState.gray_color,
        radius=BaseState.radius,
        scaling=BaseState.scaling,
    )