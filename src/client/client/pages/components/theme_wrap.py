from state.settings_st import SettingsState
import reflex as rx

def theme_wrap(component: rx.Component) -> rx.Component:
    return rx.theme(
        component,
        has_background=True,
        appearance=SettingsState.appearance,
        accent_color=SettingsState.accent_color,
        gray_color=SettingsState.gray_color,
        radius=SettingsState.radius,
        scaling=SettingsState.scaling,
    )