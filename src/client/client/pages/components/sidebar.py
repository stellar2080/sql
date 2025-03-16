import reflex as rx
from state.auth_st import AuthState

def sidebar_item(
    text: str, icon: str, on_click: property, 
) -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.icon(icon),
            rx.text(text, size="4"),
            width="100%",
            padding_x="0.5rem",
            padding_y="0.75rem",
            align="center",
            style={
                "_hover": {
                    "bg": rx.color("accent", 4),
                    "color": rx.color("accent", 11),
                },
                "border-radius": "0.5em",
            },
        ),
        on_click=on_click,
        underline="none",
        weight="medium",
        width="100%",
    )

def sidebar_bottom_profile() -> rx.Component:
    return rx.box(
        rx.desktop_only(
            rx.vstack(
                rx.hstack(
                    rx.icon(
                        "sparkles",
                        width="2.25em",
                        height="auto",
                        border_radius="25%",
                    ),
                    rx.heading(
                        "Text2SQL", size="7", weight="bold"
                    ),
                    align="center",
                    justify="start",
                    padding_x="0.5rem",
                    width="100%",
                ),
                rx.vstack(
                    sidebar_item("AI问答", "bot", rx.redirect("/account")),
                    sidebar_item("知识库", "square-library", rx.redirect("/account")),
                    sidebar_item("AI配置", "sliders-horizontal", rx.redirect("/account")),
                    sidebar_item("问答记录", "message_circle", rx.redirect("/account")),
                    spacing="1",
                    width="100%",
                ),
                rx.spacer(),
                rx.vstack(
                    rx.vstack(
                        sidebar_item(
                            "个人中心", "settings", rx.redirect("/account")
                        ),
                        sidebar_item(
                            "退出登录", "log-out", AuthState.logout
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    rx.divider(),
                    rx.hstack(
                        rx.icon_button(
                            rx.icon("user"),
                            size="3",
                            radius="full",
                            on_click=rx.redirect("/account")
                        ),
                        rx.vstack(
                            rx.box(
                                rx.text(
                                    AuthState.username,
                                    size="3",
                                    weight="bold",
                                ),
                                rx.text(
                                    AuthState.email,
                                    size="2",
                                    weight="medium",
                                ),
                                width="100%",
                            ),
                            spacing="0",
                            align="start",
                            justify="start",
                            width="100%",
                        ),
                        padding_x="0.5rem",
                        align="center",
                        justify="start",
                        width="100%",
                    ),
                    width="100%",
                    spacing="5",
                ),
                spacing="5",
                position="fixed",
                left="0%",
                top="0%",
                z_index="5",
                padding_x="1em",
                padding_y="1.5em",
                bg=rx.color("accent", 3),
                align="start",
                height="100%",
                width="16em",
            ),
        ),
    )