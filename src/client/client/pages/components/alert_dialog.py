import reflex as rx

def alert_dialog(
    description: str, 
    on_click: property, 
    open: bool
) -> rx.Component:
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("系统信息"),
            rx.alert_dialog.description(
                description,
            ),
            rx.flex(
                rx.alert_dialog.action(
                    rx.button(
                        "确定",
                        variant="soft",
                        on_click=on_click,
                    ),
                ),
                spacing="3",
                justify="end",
            ),
            max_width="450px",
        ),
        open=open,
    )