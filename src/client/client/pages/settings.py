"""The settings page."""

import reflex as rx

from client.state.base_st import BaseState
from .components.sidebar import sidebar_bottom_profile
from .components.color_picker import primary_color_picker, secondary_color_picker
from .components.radius_picker import radius_picker
from .components.scaling_picker import scaling_picker
from .components.theme_wrap import theme_wrap
from .components.alert_dialog import alert_dialog


def settings() -> rx.Component:
    return theme_wrap(
        rx.box( 
            sidebar_bottom_profile(),
            rx.center(
                rx.vstack(
                    rx.heading(
                        "系统设置", 
                        size="6"
                    ),
                    rx.scroll_area(
                        rx.vstack(
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("palette"),
                                    rx.heading("主题颜色", size="5"),
                                    align="center",
                                ),
                                primary_color_picker(),
                                spacing="4",
                                width="100%",
                            ),
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("blend"),
                                    rx.heading("辅助颜色", size="5"),
                                    align="center",
                                ),
                                secondary_color_picker(),
                                spacing="4",
                                width="100%",
                            ),
                            radius_picker(),
                            scaling_picker(),
                            spacing="7",
                            align='center',
                            justify='center',   
                        ),
                        type="hover",
                        scrollbars="vertical",
                        height=600,
                        width="100%",
                        padding_x='2em',
                        padding_y='1em'
                    ),
                    rx.hstack(
                        rx.button(
                            "恢复默认",
                            on_click=BaseState.reset_settings,
                            variant='surface',
                            size='3'
                        ),
                        rx.button(
                            "保存设置",
                            on_click=BaseState.save_settings,
                            variant='surface',
                            size='3'
                        ),
                        width='100%',
                        spacing='5',
                        justify='center'
                    ),
                    rx.text(
                        "可前往各个页面预览效果，若不保存设置，退出登录后将丢失更改",
                        text_align="center",
                        font_size=".75em",
                        color=rx.color("gray", 10),
                    ),
                    spacing="6",
                    align='center',
                    justify='center',
                    padding_top="70px"
                ),
                position="sticky",
                left="15%",
                width="85%",
            ),
        )
    )
            
