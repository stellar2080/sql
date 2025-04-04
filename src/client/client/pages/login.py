"""Login page. Uses auth_layout to render UI shared with the sign up page."""

import reflex as rx
from .components.alert_dialog import alert_dialog
from client.state.base_st import BaseState
from .components.theme_wrap import theme_wrap_out

def login():
    """The login page."""
    return theme_wrap_out(
        rx.center(
            rx.card(
                rx.flex(
                    rx.heading(
                        "用户登录",
                        align="center"
                    ),
                    rx.form(
                        rx.flex(
                            rx.flex(
                                rx.text(
                                    "用户名/邮箱",
                                    size="3",
                                    weight="medium",
                                    text_align="left",
                                    width="100%",
                                ),
                                rx.input(
                                    rx.input.slot(rx.icon("user")),
                                    placeholder='输入用户名或邮箱',
                                    name='user',
                                    size="3",
                                    width="100%",
                                ),
                                direction='column',
                                spacing='1'
                            ),
                            rx.flex(
                                rx.flex(
                                    rx.text(
                                        "密码",
                                        size="3",
                                        weight="medium",
                                        text_align="left",
                                    ),
                                    rx.text(
                                        rx.link("忘记密码？", href="/findpwd"),
                                    ),
                                    direction="row",
                                    justify="between",
                                    width='100%'
                                ),
                                rx.input(
                                    rx.input.slot(rx.icon("key-round")),
                                    placeholder='输入密码',
                                    type="password",
                                    name='password',
                                    size="3",
                                    width="100%",
                                ),
                                direction="column",
                                spacing='1',
                                align='center',
                                justify='center'
                            ),
                            rx.button(
                                "登录", 
                                type='submit', 
                                variant='surface',
                                size="3", 
                                width="100%",
                            ),
                            direction="column",
                            spacing="5",
                        ),
                        padding="32px",
                        width="100%",
                        on_submit=BaseState.login,
                        reset_on_submit=False,
                    ),
                    rx.text(
                        "还没有账号？ ",
                        rx.link(
                            "点击此处注册。", 
                            href="/signup"
                        ),
                        color=rx.color("gray", 10),
                    ),
                    align="center",
                    justify="center",
                    direction="column",
                    spacing='4',
                    width="100%",
                    height="100%",
                    padding='30px'
                ),
                width="500px",
            ),
            alert_dialog(
                description=BaseState.base_dialog_description,
                on_click=BaseState.base_dialog_open_change,
                open=BaseState.base_dialog_open
            ),
            alert_dialog(
                description=BaseState.base_dialog_description,
                on_click=BaseState.auth_success_redirect,
                open=BaseState.auth_success_dialog_open
            ),
            width="100%",
            height="100vh",
        )
    )