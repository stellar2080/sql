import reflex as rx

from client.state.chat_record_st import Item, ChatRecordState

def _create_dialog(
    item: Item, icon_name: str, color_scheme: str, dialog_title: str
) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.icon_button(
                rx.icon(icon_name), color_scheme=color_scheme, size="2", variant="solid"
            )
        ),
        rx.dialog.content(
            rx.vstack(
                rx.dialog.title(dialog_title),
                rx.dialog.description(
                    rx.vstack(
                        rx.text(item.question),
                        rx.text(item.sql),
                        rx.data_table(
                            data=item.sql_result['rows'],
                            columns=item.sql_result['cols'],
                            pagination=True,
                            sort=True,        
                        ),
                        rx.text(item.create_time),
                    )
                ),
                rx.dialog.close(
                    rx.button("Close Dialog", size="2", color_scheme=color_scheme),
                ),
            ),
        ),
    )


def _delete_dialog(item: Item) -> rx.Component:
    return _create_dialog(item, "trash-2", "tomato", "Delete Dialog")


def _approve_dialog(item: Item) -> rx.Component:
    return _create_dialog(item, "check", "grass", "Approve Dialog")


def _edit_dialog(item: Item) -> rx.Component:
    return _create_dialog(item, "square-pen", "blue", "Edit Dialog")


def _dialog_group(item: Item) -> rx.Component:
    return rx.hstack(
        _approve_dialog(item),
        _edit_dialog(item),
        _delete_dialog(item),
        align="center",
        spacing="2",
        width="100%",
    )


def _header_cell(text: str, icon: str) -> rx.Component:
    return rx.table.column_header_cell(
        rx.hstack(
            rx.icon(icon, size=18),
            rx.text(text),
            align="center",
            spacing="2",
        ),
    )


def _show_item(item: Item, index: int) -> rx.Component:
    bg_color = rx.cond(
        index % 2 == 0,
        rx.color("gray", 1),
        rx.color("accent", 2),
    )
    hover_color = rx.cond(
        index % 2 == 0,
        rx.color("gray", 3),
        rx.color("accent", 3),
    )
    return rx.table.row(
        rx.table.row_header_cell(item.question),
        rx.table.cell(item.sql),
        rx.table.cell(item.sql_result),
        rx.table.cell(item.create_time),
        rx.table.cell(_dialog_group(item)),
        style={"_hover": {"bg": hover_color}, "bg": bg_color},
        align="center",
    )


def _pagination_view() -> rx.Component:
    return (
        rx.hstack(
            rx.text(
                "Page ",
                rx.code(ChatRecordState.page_number),
                f" of {ChatRecordState.total_pages}",
                justify="end",
            ),
            rx.hstack(
                rx.icon_button(
                    rx.icon("chevrons-left", size=18),
                    on_click=ChatRecordState.first_page,
                    opacity=rx.cond(ChatRecordState.page_number == 1, 0.6, 1),
                    color_scheme=rx.cond(ChatRecordState.page_number == 1, "gray", "accent"),
                    variant="soft",
                ),
                rx.icon_button(
                    rx.icon("chevron-left", size=18),
                    on_click=ChatRecordState.prev_page,
                    opacity=rx.cond(ChatRecordState.page_number == 1, 0.6, 1),
                    color_scheme=rx.cond(ChatRecordState.page_number == 1, "gray", "accent"),
                    variant="soft",
                ),
                rx.icon_button(
                    rx.icon("chevron-right", size=18),
                    on_click=ChatRecordState.next_page,
                    opacity=rx.cond(
                        ChatRecordState.page_number == ChatRecordState.total_pages, 0.6, 1
                    ),
                    color_scheme=rx.cond(
                        ChatRecordState.page_number == ChatRecordState.total_pages,
                        "gray",
                        "accent",
                    ),
                    variant="soft",
                ),
                rx.icon_button(
                    rx.icon("chevrons-right", size=18),
                    on_click=ChatRecordState.last_page,
                    opacity=rx.cond(
                        ChatRecordState.page_number == ChatRecordState.total_pages, 0.6, 1
                    ),
                    color_scheme=rx.cond(
                        ChatRecordState.page_number == ChatRecordState.total_pages,
                        "gray",
                        "accent",
                    ),
                    variant="soft",
                ),
                align="center",
                spacing="2",
                justify="end",
            ),
            spacing="5",
            margin_top="1em",
            align="center",
            width="100%",
            justify="end",
        ),
    )


def main_table() -> rx.Component:
    return rx.box(
        rx.flex(
            rx.flex(
                rx.cond(
                    ChatRecordState.sort_reverse,
                    rx.icon(
                        "arrow-down-z-a",
                        size=28,
                        stroke_width=1.5,
                        cursor="pointer",
                        flex_shrink="0",
                        on_click=ChatRecordState.toggle_sort,
                    ),
                    rx.icon(
                        "arrow-down-a-z",
                        size=28,
                        stroke_width=1.5,
                        cursor="pointer",
                        flex_shrink="0",
                        on_click=ChatRecordState.toggle_sort,
                    ),
                ),
                rx.select(
                    [
                        "question",
                        "sql",
                        "sql_result",
                        "create_time",
                    ],
                    placeholder="Sort By: question",
                    size="3",
                    on_change=ChatRecordState.set_sort_value,
                ),
                rx.input(
                    rx.input.slot(rx.icon("search")),
                    rx.input.slot(
                        rx.icon("x"),
                        justify="end",
                        cursor="pointer",
                        on_click=ChatRecordState.setvar("search_value", ""),
                        display=rx.cond(ChatRecordState.search_value, "flex", "none"),
                    ),
                    value=ChatRecordState.search_value,
                    placeholder="Search here...",
                    size="3",
                    max_width=["150px", "150px", "200px", "250px"],
                    width="100%",
                    variant="surface",
                    color_scheme="gray",
                    on_change=ChatRecordState.set_search_value,
                ),
                align="center",
                justify="end",
                spacing="3",
            ),
            spacing="3",
            justify="between",
            wrap="wrap",
            width="100%",
            padding_bottom="1em",
        ),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    _header_cell("question", "route"),
                    _header_cell("sql", "list-checks"),
                    _header_cell("sql_result", "notebook-pen"),
                    _header_cell("create_time", "calendar"),
                    _header_cell("操作", "calendar"),
                ),
            ),
            rx.table.body(
                rx.foreach(
                    ChatRecordState.get_current_page,
                    lambda item, index: _show_item(item, index),
                )
            ),
            variant="surface",
            size="3",
            width="100%",
        ),
        _pagination_view(),
        width="100%",
    )
