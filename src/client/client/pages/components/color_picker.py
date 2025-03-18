import reflex as rx
from reflex.components.radix.themes.base import LiteralAccentColor, LiteralGrayColor

from state.base_st import BaseState

box_shadow_style = "0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)"
color_box_size = ["2.25rem", "2.25rem", "2.5rem"]
color_picker_style = {
    "border_radius": "max(var(--radius-3), var(--radius-full))",
    "box_shadow": box_shadow_style,
    "cursor": "pointer",
    "display": "flex",
    "align_items": "center",
    "justify_content": "center",
    "transition": "transform 0.15s ease-in-out",
    "_active": {
        "transform": "translateY(2px) scale(0.95)",
    },
}


primary_color_dict: dict[str, str] = {
    color.capitalize(): f"linear-gradient(45deg, {rx.color(color, 10)}, {rx.color(color, 8)})"
    for color in LiteralAccentColor.__args__
}

secondary_color_dict: dict[str, str] = {
    color.capitalize(): f"linear-gradient(45deg, {rx.color(color, 10)}, {rx.color(color, 8)})"
    for color in LiteralGrayColor.__args__
    if color != "auto"
}


class ColorPickerState(rx.State):
    primary_color_options: dict[str, str] = primary_color_dict
    secondary_color_options: dict[str, str] = secondary_color_dict

def _display_primary_color(color: list) -> rx.Component:
    return rx.tooltip(
        rx.box(
            rx.cond(
                color[0].lower() == BaseState.accent_color.lower(),
                rx.box(
                    rx.icon("check", color=rx.color("gray", 12)),
                    bg=color[1],
                    height=color_box_size,
                    width=color_box_size,
                    border=f"2px solid  {rx.color('gray', 12)}",
                    style=color_picker_style,
                ),
                rx.box(
                    bg=color[1],
                    height=color_box_size,
                    width=color_box_size,
                    style=color_picker_style,
                ),
            ),
            on_click=BaseState.setvar("accent_color", color[0].lower()),
        ),
        content=color[0],
    )


def _display_secondary_color(colors: list) -> rx.Component:
    return rx.tooltip(
        rx.box(
            rx.cond(
                colors[0].lower() == BaseState.gray_color.lower(),
                rx.box(
                    rx.icon("check", color=rx.color("gray", 12)),
                    bg=colors[1],
                    height=color_box_size,
                    width=color_box_size,
                    border=f"2px solid  {rx.color('gray', 12)}",
                    style=color_picker_style,
                ),
                rx.box(
                    bg=colors[1],
                    height=color_box_size,
                    width=color_box_size,
                    style=color_picker_style,
                ),
            ),
            on_click=BaseState.setvar("gray_color", colors[0].lower()),
        ),
        content=colors[0],
    )


def primary_color_picker() -> rx.Component:
    return rx.flex(
        rx.foreach(ColorPickerState.primary_color_options, _display_primary_color),
        width="100%",
        max_width="40rem",
        wrap="wrap",
        gap=["15px", "15px", "20px"],
    )


def secondary_color_picker() -> rx.Component:
    return rx.flex(
        rx.foreach(ColorPickerState.secondary_color_options, _display_secondary_color),
        width="100%",
        max_width="40rem",
        wrap="wrap",
        gap=["15px", "15px", "20px"],
    )
