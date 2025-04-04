"""Sign up page. Uses auth_layout to render UI shared with the login page."""

import reflex as rx
from .components.alert_dialog import alert_dialog
from client.state.signup_st import SignupState
from .components.theme_wrap import theme_wrap_out

def signup():
    """The sign up page."""
    return theme_wrap_out(
        rx.center(
            rx.card(
                rx.flex(
                    rx.heading(
                        "用户注册",
                        align="center"
                    ),
                    rx.form(
                        rx.flex(
                            rx.flex(
                                rx.text(
                                    "用户名",
                                    size="3",
                                    weight="medium",
                                    text_align="left",
                                    width="100%",
                                ),
                                rx.input(
                                    rx.input.slot(rx.icon("user")),
                                    placeholder="输入用户名",
                                    name="username",
                                    size="3",
                                ),
                                direction='column',
                                spacing='1'
                            ),
                            rx.flex(
                                rx.text(
                                    "邮箱",
                                    size="3",
                                    weight="medium",
                                    text_align="left",
                                    width="100%",
                                ),
                                rx.input(
                                    rx.input.slot(rx.icon("mail")),
                                    placeholder="输入邮箱",
                                    name="email",
                                    on_change=lambda x: SignupState.set_email(x),
                                    size="3",
                                ),
                                direction='column',
                                spacing='1'
                            ),
                            rx.flex(
                                rx.text(
                                    "验证码",
                                    size="3",
                                    weight="medium",
                                    text_align="left",
                                    width="100%",
                                ),
                                rx.flex(
                                    rx.input(
                                        rx.input.slot(rx.icon("shield-check")),
                                        placeholder="输入验证码",
                                        name="captcha",
                                        size="3",
                                        width="60%",
                                    ),
                                    rx.button(
                                        rx.cond(
                                            SignupState.countdown > 0,
                                            f"重新发送 ({SignupState.countdown}s)",
                                            "发送验证码"
                                        ),
                                        type="button",
                                        on_click=SignupState.send_email,
                                        size="3",
                                        variant='surface',
                                        disabled=SignupState.countdown > 0,
                                        width="40%",
                                    ),
                                    direction="row",
                                    align="center",
                                    justify="center",
                                    spacing="4"
                                ),
                                direction='column',
                                spacing='1'
                            ),
                            rx.flex(
                                rx.text(  
                                    "密码",
                                    size="3",
                                    weight="medium",
                                    text_align="left",
                                    width="100%",
                                ),
                                rx.input(
                                    rx.input.slot(rx.icon("key-round")),
                                    type="password",
                                    name="password",
                                    placeholder="输入密码",
                                    size="3",
                                ),
                                direction='column',
                                spacing='1'
                            ),
                            rx.flex(
                                rx.text(
                                    "确认密码",
                                    size="3",
                                    weight="medium",
                                    text_align="left",
                                    width="100%",
                                ),
                                rx.input(
                                    rx.input.slot(rx.icon("key-round")),
                                    type="password",
                                    name="confirm_password",
                                    placeholder="再次确认密码",
                                    size="3",
                                ),
                                direction='column',
                                spacing='1'
                            ),
                            rx.button(
                                "注册",
                                type="submit",
                                variant='surface',
                                size="3",
                                width="100%",
                            ),
                            spacing="4",
                            direction="column"
                        ),
                        padding="32px",
                        width="100%",
                        on_submit=SignupState.signup,
                        reset_on_submit=False,
                    ),
                    rx.text(
                        "已有账号？ ",
                        rx.link(
                            "点击此处登录。", 
                            href="/login"
                        ),
                        color=rx.color("gray", 10),
                    ),
                    align="center",
                    justify="center",
                    direction="column",
                    spacing="4",
                    width="100%",
                    height="100%",
                    padding='30px'
                ),
                width="600px",
            ),
            width="100%",
            height="100vh",
        )
    )
