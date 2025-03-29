"""The Chat Record page."""

import reflex as rx
from client.state.chat_record_st import ChatRecordState
from .components.sidebar import sidebar_bottom_profile
from .components.theme_wrap import theme_wrap
from .components.alert_dialog import alert_dialog
from .components.table import main_table

def chat_record() -> rx.Component:
    return theme_wrap(
        rx.box( 
            sidebar_bottom_profile(),
            rx.center(
                rx.vstack(
                    rx.heading(
                        "问答记录", 
                        size="6"
                    ),
                    main_table(),
                    align='center',
                    justify='center',
                    spacing='6',
                    width='80%',
                    padding_top="70px",
                    padding_bottom="50px",
                ),
                position="sticky",
                left="15%",
                width="85%",
            ),
        )
    )