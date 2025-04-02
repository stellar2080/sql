import reflex as rx

from client.state.repository_st import Doc, RepositoryState

def _delete_dialog(doc: Doc) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon('trash-2',size=15), 
                rx.text('删除'),
                color_scheme='tomato', 
                size="2", 
                variant="solid"
            )
        ),
        rx.dialog.content(
            rx.dialog.title('删除对话'),
            rx.dialog.description(
                rx.vstack(
                    rx.text('确定要删除吗'),
                    rx.hstack(
                        rx.dialog.close(
                            rx.button(
                                "取消",
                                variant="soft",
                                size="3",
                                type="button",
                            ),
                        ),
                        rx.dialog.close(
                            rx.button(
                                "确定", 
                                type="button",
                                size="3",
                                on_click=RepositoryState.delete_doc(doc)
                            ),
                        ),
                        spacing="5",
                        justify="end",
                    ), 
                )
            ),
            max_width="450px",
        ),
    ) 

def _detail_dialog(doc: Doc) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon('list',size=15), 
                rx.text('详情'),
                color_scheme='blue', 
                size="2", 
                variant="solid"
            )
        ),
        rx.dialog.content(
            rx.vstack(
                rx.dialog.title('查看详情'),
                rx.dialog.description(
                    rx.vstack(
                        rx.hstack(
                            rx.badge("key_id"),
                            rx.text(doc.key_id),
                            align='center',
                        ),
                        rx.hstack(
                            rx.badge("key"),
                            rx.text(doc.key),
                            align='center',
                        ),
                        rx.hstack(
                            rx.badge("doc_id"),
                            rx.text(doc.doc_id),
                            align='center',
                        ),
                        rx.hstack(
                            rx.badge("doc"),
                            rx.text(doc.doc),
                            align='center',
                        ),
                    )
                ),
                rx.dialog.close(
                    rx.button("关闭", size="3", color_scheme='blue'),
                ),
            ),
            max_width="150em",
        ),
    ) 

def _dialog_group(doc: Doc) -> rx.Component:
    return rx.hstack(
        _detail_dialog(doc),
        _delete_dialog(doc),
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


def _show_item(doc: Doc, index: int) -> rx.Component:
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
        rx.table.row_header_cell(
            doc.key,
            min_width="100px",
            max_width="100px"
        ),
        rx.table.cell(
            doc.doc,
            min_width="500px",
            max_width="500px"
        ),
        rx.table.cell(
            _dialog_group(doc),
            min_width="120px",
            max_width="120px"
        ), 
        style={"_hover": {"bg": hover_color}, "bg": bg_color},
        align="center",
    )


def _pagination_view() -> rx.Component:
    return (
        rx.hstack(
            rx.text(
                "Page ",
                rx.code(RepositoryState.page_number),
                f" of {RepositoryState.total_pages}",
                justify="end",
            ),
            rx.hstack(
                rx.icon_button(
                    rx.icon("chevrons-left", size=18),
                    on_click=RepositoryState.first_page,
                    opacity=rx.cond(RepositoryState.page_number == 1, 0.6, 1),
                    color_scheme=rx.cond(RepositoryState.page_number == 1, "gray", "accent"),
                    variant="soft",
                ),
                rx.icon_button(
                    rx.icon("chevron-left", size=18),
                    on_click=RepositoryState.prev_page,
                    opacity=rx.cond(RepositoryState.page_number == 1, 0.6, 1),
                    color_scheme=rx.cond(RepositoryState.page_number == 1, "gray", "accent"),
                    variant="soft",
                ),
                rx.icon_button(
                    rx.icon("chevron-right", size=18),
                    on_click=RepositoryState.next_page,
                    opacity=rx.cond(
                        RepositoryState.page_number == RepositoryState.total_pages, 0.6, 1
                    ),
                    color_scheme=rx.cond(
                        RepositoryState.page_number == RepositoryState.total_pages,
                        "gray",
                        "accent",
                    ),
                    variant="soft",
                ),
                rx.icon_button(
                    rx.icon("chevrons-right", size=18),
                    on_click=RepositoryState.last_page,
                    opacity=rx.cond(
                        RepositoryState.page_number == RepositoryState.total_pages, 0.6, 1
                    ),
                    color_scheme=rx.cond(
                        RepositoryState.page_number == RepositoryState.total_pages,
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
                    RepositoryState.sort_reverse,
                    rx.icon(
                        "arrow-down-z-a",
                        size=28,
                        stroke_width=1.5,
                        cursor="pointer",
                        flex_shrink="0",
                        on_click=RepositoryState.toggle_sort,
                    ),
                    rx.icon(
                        "arrow-down-a-z",
                        size=28,
                        stroke_width=1.5,
                        cursor="pointer",
                        flex_shrink="0",
                        on_click=RepositoryState.toggle_sort,
                    ),
                ),
                rx.select(
                    [
                        "key",
                        "doc",
                    ],
                    placeholder="排序...",
                    size="3",
                    on_change=RepositoryState.set_sort_value,
                ),
                rx.input(
                    rx.input.slot(rx.icon("search")),
                    rx.input.slot(
                        rx.icon("x"),
                        justify="end",
                        cursor="pointer",
                        on_click=RepositoryState.setvar("search_value", ""),
                        display=rx.cond(RepositoryState.search_value, "flex", "none"),
                    ),
                    value=RepositoryState.search_value,
                    placeholder="在此处搜索...",
                    size="3",
                    max_width=["150px", "150px", "200px", "250px"],
                    width="100%",
                    variant="surface",
                    color_scheme="gray",
                    on_change=RepositoryState.set_search_value,
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
                    _header_cell("key", "message-circle-question"),
                    _header_cell("doc", "calendar"),
                    _header_cell("操作", "wrench"),
                ),
            ),
            rx.table.body(
                rx.foreach(
                    RepositoryState.get_current_page,
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
