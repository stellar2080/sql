import reflex as rx
from client.state.account_st import AccountState
from .components.alert_dialog import alert_dialog
from .components.sidebar import sidebar_bottom_profile
from .components.theme_wrap import theme_wrap


def change_username() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                "修改用户名",
            ),
            rx.form(
                rx.flex(
                    rx.text(
                        "请填写以下信息",
                        align='center'
                    ),
                    rx.input(
                        rx.input.slot(rx.icon("user")),
                        placeholder="新用户名",
                        name="username",
                        size="3",
                        width='100%',
                    ),
                    rx.flex(
                        rx.button(
                            "取消",
                            variant="soft",
                            size="3",
                            type="button",
                            on_click=AccountState.change_username_dialog_open_change
                        ),
                        rx.button(
                            "提交", 
                            type="submit",
                            size="3",
                        ),
                        spacing="5",
                        justify="end",
                    ),
                    direction="column",
                    spacing="5",
                ),
                padding="16px",
                width="100%",
                on_submit=AccountState.change_username,
                reset_on_submit=False,
            ),
            max_width="450px",
        ),
        open=AccountState.change_username_dialog_open
    )

def change_email() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                "修改邮箱",
            ),
            rx.form(
                rx.flex(
                    rx.text(
                        "请填写以下信息",
                        align='center'
                    ),
                    rx.input(
                        rx.input.slot(rx.icon("mail")),
                        placeholder="新邮箱",
                        name="email",
                        on_change=lambda x: AccountState.set_email_sent(x),
                        size="3",
                        width='100%'
                    ),
                    rx.flex(
                        rx.input(
                            rx.input.slot(rx.icon("shield-check")),
                            placeholder="验证码",
                            name="captcha",
                            size="3",
                            width="60%",
                        ),
                        rx.button(
                            rx.cond(
                                AccountState.countdown > 0,
                                f"重新发送 ({AccountState.countdown}s)",
                                "发送验证码"
                            ),
                            type="button",
                            on_click=AccountState.send_email,
                            size="3",
                            disabled=AccountState.countdown > 0,
                            width="40%",
                        ),
                        direction="row",
                        align="center",
                        justify="center",
                        spacing="4"
                    ),
                    rx.flex(
                        rx.button(
                            "取消",
                            type="button",
                            size="3",
                            variant="soft",
                            on_click=AccountState.change_email_dialog_open_change
                        ),
                        rx.button(
                            "提交", 
                            type="submit",
                            size="3",
                        ),
                        spacing="5",
                        justify="end",
                    ),
                    direction="column",
                    spacing="5",
                ),
                padding="16px",
                width="100%",
                on_submit=AccountState.change_email,
                reset_on_submit=False,
            ),
            max_width="450px",
        ),
        open=AccountState.change_email_dialog_open
    )

def change_password() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                "修改密码",
            ),
            rx.form(
                rx.flex(
                    rx.text(
                        "请填写以下信息",
                        align='center'
                    ),
                    rx.input(
                        rx.input.slot(rx.icon("key-round")),
                        placeholder="新密码",
                        name="password",
                        type="password",
                        size="3",
                        width='100%'
                    ),
                    rx.input(
                        rx.input.slot(rx.icon("key-round")),
                        placeholder="确认密码",
                        name="confirm_password",
                        type="password",
                        size="3",
                        width='100%'
                    ),
                    rx.flex(
                        rx.button(
                            "取消",
                            variant="soft",
                            size="3",
                            type="button",
                            on_click=AccountState.change_password_dialog_open_change,
                        ),
                        rx.button(
                            "提交", 
                            type="submit",
                            size="3",
                        ),
                        spacing="5",
                        justify="end",
                    ),
                    direction="column",
                    spacing="5",
                ),
                padding="16px",
                width="100%",
                on_submit=AccountState.change_password,
                reset_on_submit=False,
            ),
            max_width="450px",
        ),
        open=AccountState.change_password_dialog_open
    )

def user_box() -> rx.Component:
    return rx.flex(
        rx.flex(
            rx.icon("user"),
            rx.text(
                "用户名",
                size="4",
                width="50%",
                align="left",
                weight='bold'
            ),
            direction='row',
            align='center',
            justify='center',
            spacing='2',
            width='10%'
        ),
        rx.text(
            AccountState.username,
            size="3",
            width="20%",
        ),
        rx.button(
            "修改",
            size="3",
            width="10%",
            variant='surface',
            on_click=AccountState.change_username_dialog_open_change
        ),
        change_username(),
        direction="row",
        spacing="4",
        align="center",
        justify="center",
        width="100%",
    ),

def email_box() -> rx.Component:
    return rx.flex(
        rx.flex(
            rx.icon("mail"),
            rx.text(
                "邮箱",
                size="4",
                width="50%",
                align="left",
                weight='bold'
            ),
            direction='row',
            align='center',
            justify='center',
            spacing='2',
            width='10%'
        ),
        rx.text(
            AccountState.email,
            size="3",
            width="20%",
        ),
        rx.button(
            "修改",
            size="3",
            width="10%",
            variant='surface',
            on_click=AccountState.change_email_dialog_open_change
        ),
        change_email(),
        direction="row",
        spacing="4",
        align="center",
        justify="center",
        width="100%",
    ),

def password_box() -> rx.Component:
    return rx.flex(
        rx.flex(
            rx.icon("key-round"),
            rx.text(
                "密码",
                size="4",
                width="50%",
                align="left",
                weight='bold'
            ),
            direction='row',
            align='center',
            justify='center',
            spacing='2',
            width='10%'
        ),
        rx.text(
            "*"*10,
            size="3",
            width="20%",
        ),
        rx.button(
            "修改",
            size="3",
            width="10%",
            variant='surface',
            on_click=AccountState.change_password_dialog_open_change
        ),
        change_password(),
        direction="row",
        spacing="4",
        align="center",
        justify="center",
        width="100%",
    ),

def account():
    return theme_wrap(
        rx.box( 
            sidebar_bottom_profile(),
            rx.center(  
                rx.flex(
                    rx.heading(
                        "个人中心",
                        size="6"
                    ),
                    rx.scroll_area(
                        rx.vstack(
                            user_box(),
                            email_box(),
                            password_box(),
                            align="center",
                            justify="center",
                            spacing="7",
                        ),
                        type="hover",
                        scrollbars="vertical",
                        height=600,
                        width="100%",
                        padding_x='2em',
                        padding_y='12em'
                    ),
                    direction="column",
                    align="center",
                    justify="center",
                    spacing="7",
                    width="100%",
                    padding_top="70px",
                    padding_bottom="50px",
                ),
                position="sticky",
                left="15%",
                width="85%",
            ),
        )
    )