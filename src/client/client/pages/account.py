import reflex as rx
from state.account_st import AccountState
from .components.alert_dialog import alert_dialog
from .components.sidebar import sidebar_bottom_profile

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
                            color_scheme="gray",
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
            alert_dialog(
                description=AccountState.account_dialog_description,
                on_click=AccountState.account_dialog_open_change,
                open=AccountState.account_dialog_open
            ),
            alert_dialog(
                description=AccountState.account_dialog_description,
                on_click=AccountState.close_all_dialog,
                open=AccountState.success_dialog_open
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
                        placeholder="新邮箱",
                        name="email",
                        on_blur=lambda x: AccountState.set_email_sent(x),
                        size="3",
                        width='100%'
                    ),
                    rx.flex(
                        rx.input(
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
                            color_scheme="gray",
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
            alert_dialog(
                description=AccountState.account_dialog_description,
                on_click=AccountState.account_dialog_open_change,
                open=AccountState.account_dialog_open
            ),
            alert_dialog(
                description=AccountState.account_dialog_description,
                on_click=AccountState.close_all_dialog,
                open=AccountState.success_dialog_open
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
                        placeholder="新密码",
                        name="password",
                        type="password",
                        size="3",
                        width='100%'
                    ),
                    rx.input(
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
                            color_scheme="gray",
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
            alert_dialog(
                description=AccountState.account_dialog_description,
                on_click=AccountState.account_dialog_open_change,
                open=AccountState.account_dialog_open
            ),
            alert_dialog(
                description=AccountState.account_dialog_description,
                on_click=AccountState.close_all_dialog,
                open=AccountState.success_dialog_open
            ),
            max_width="450px",
        ),
        open=AccountState.change_password_dialog_open
    )

def account():
    return rx.box( 
        sidebar_bottom_profile(),
        rx.box( 
            rx.center(
                rx.card(
                    rx.flex(
                        rx.flex(
                            rx.flex(
                                rx.icon("user"),
                                rx.text(
                                    "用户名",
                                    size="4",
                                    width="100%",
                                    align="left",
                                    weight='bold'
                                ),
                                direction='row',
                                align='center',
                                justify='center',
                                spacing='2',
                                width='10%'
                            ),
                            rx.input(
                                placeholder=AccountState.username,
                                size="3",
                                width="30%",
                                disabled=True
                            ),
                            rx.button(
                                "修改",
                                size="3",
                                width="10%",
                                on_click=AccountState.change_username_dialog_open_change
                            ),
                            change_username(),
                            direction="row",
                            spacing="4",
                            align="center",
                            justify="center",
                            width="100%",
                        ),
                        rx.flex(
                            rx.flex(
                                rx.icon("mail"),
                                rx.text(
                                    "邮箱",
                                    size="4",
                                    width="100%",
                                    align="left",
                                    weight='bold'
                                ),
                                direction='row',
                                align='center',
                                justify='center',
                                spacing='2',
                                width='10%'
                            ),
                            rx.input(
                                placeholder=AccountState.email,
                                size="3",
                                width="30%",
                                disabled=True
                            ),
                            rx.button(
                                "修改",
                                size="3",
                                width="10%",
                                on_click=AccountState.change_email_dialog_open_change
                            ),
                            change_email(),
                            direction="row",
                            spacing="4",
                            align="center",
                            justify="center",
                            width="100%",
                        ),
                        rx.flex(
                            rx.flex(
                                rx.icon("key-round"),
                                rx.text(
                                    "密码",
                                    size="4",
                                    width="100%",
                                    align="left",
                                    weight='bold'
                                ),
                                direction='row',
                                align='center',
                                justify='center',
                                spacing='2',
                                width='10%'
                            ),
                            rx.input(
                                placeholder="*"*10,
                                size="3",
                                width="30%",
                                disabled=True
                            ),
                            rx.button(
                                "修改",
                                size="3",
                                width="10%",
                                on_click=AccountState.change_password_dialog_open_change
                            ),
                            change_password(),
                            direction="row",
                            spacing="4",
                            align="center",
                            justify="center",
                            width="100%",
                        ),
                        direction="column",
                        align="center",
                        justify="center",
                        spacing="8",    
                        width="100%",
                        height="100%",
                        padding="100px"
                    ),
                    width="90%",
                    height='90%'
                ),
                width="100%",
                height="100vh",
            ),
            position="fixed",
            left="15%",
            width="85%",
        ),
    )
