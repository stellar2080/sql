"""The settings page."""

import reflex as rx

from .components.sidebar import sidebar_bottom_profile
from .components.color_picker import primary_color_picker, secondary_color_picker
from .components.radius_picker import radius_picker
from .components.scaling_picker import scaling_picker

def settings() -> rx.Component:
    """The settings page.

    Returns:
        The UI for the settings page.

    """
    return rx.box( 
        sidebar_bottom_profile(),
        rx.box(
            rx.center(
                rx.flex(
                    rx.heading(
                        "Settings", 
                        size="5"
                    ),
                    rx.vstack(
                        rx.hstack(
                            rx.icon("palette", color=rx.color("accent", 10)),
                            rx.heading("主题颜色", size="6"),
                            align="center",
                        ),
                        primary_color_picker(),
                        spacing="4",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.hstack(
                            rx.icon("blend", color=rx.color("gray", 11)),
                            rx.heading("灰度颜色", size="6"),
                            align="center",
                        ),
                        secondary_color_picker(),
                        spacing="4",
                        width="100%",
                    ),
                    radius_picker(),
                    scaling_picker(),
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
    )
     
