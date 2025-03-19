"""The AI config page."""

import reflex as rx

from state.base_st import BaseState
from .components.sidebar import sidebar_bottom_profile
from .components.theme_wrap import theme_wrap
from .components.alert_dialog import alert_dialog


def ai_config() -> rx.Component:
    return theme_wrap(
        rx.box( 
            sidebar_bottom_profile(),
            rx.box(
                rx.center(
                    rx.flex(
                        rx.heading(
                            "AI配置", 
                            size="5"
                        ),
                        rx.vstack(
                            rx.hstack(
                                rx.icon("palette"),
                                rx.heading("主题颜色", size="6"),
                                align="center",
                            ),
                            spacing="4",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.hstack(
                                rx.icon("blend"),
                                rx.heading("辅助颜色", size="6"),
                                align="center",
                            ),
                            spacing="4",
                            width="100%",
                        ),
                        rx.flex(
                            rx.button(
                                "恢复默认",
                                on_click=BaseState.reset_settings,
                                size='3'
                            ),
                            rx.button(
                                "保存设置",
                                on_click=BaseState.summit_settings,
                                size='3'
                            ),
                            direction='row',
                            width='100%',
                            spacing='5'
                        ),
                        rx.text(
                            "可前往各个页面预览效果，若不保存设置，退出登录后将丢失更改",
                            text_align="center",
                            font_size=".75em",
                            color=rx.color("gray", 10),
                        ),
                        spacing="7",
                        direction='column',
                        align='center',
                        justify='center'
                    ),
                    width="100%",
                    height="100vh",
                ),
                position="sticky",
                left="15%",
                width="85%",
            ),
            alert_dialog(
                description=BaseState.base_dialog_description,
                on_click=BaseState.settings_reset_open_change,
                open=BaseState.settings_reset_open
            ),
            alert_dialog(
                description=BaseState.base_dialog_description,
                on_click=BaseState.settings_saved_open_change,
                open=BaseState.settings_saved_open
            ),
        )
    )
            
