import reflex as rx

from client.state.repository_st import Doc, RepositoryState
from .alert_dialog import alert_dialog

def _delete_dialog(doc: Doc) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon('trash-2',size=15), 
                rx.text('删除'),
                color_scheme='tomato', 
                size="2", 
                variant="surface",
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
                                "确定", 
                                type="button",
                                size="2",
                                on_click=RepositoryState.delete_doc(doc)
                            ),
                        ),
                        rx.dialog.close(
                            rx.button(
                                "取消",
                                variant="soft",
                                size="2",
                                type="button",
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
                size="2", 
                variant="surface",
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
                    rx.button(
                        "关闭", 
                        size="2",
                        variant="soft",
                    ),
                ),
            ),
        ),
        max_width="50em",
    ) 

def _upload_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("file-up", size=20),
                "上传文件",
                size="3",
                variant="surface",
                display=["none", "none", "none", "flex"],
            ),
        ),
        rx.dialog.content(
            rx.vstack(
                rx.dialog.title('上传文件'),
                rx.upload(
                    rx.vstack(
                        rx.button(
                            "选择文件",
                            variant='surface',
                        ),
                        rx.text(
                            "在此处拖放文件或点击选择文件"
                        ),
                        align='center',
                        justify='center',
                        width='100%'
                    ),
                    id="upload1",
                    border="1px solid",
                    border_radius='15px',
                    padding="5em",
                    width='100%'
                ),
                rx.hstack(
                    rx.foreach(
                        rx.selected_files("upload1"), rx.badge
                    ),
                    wrap="wrap",
                    width='100%'
                ),
                rx.hstack(
                    rx.button(
                        "上传",
                        size="2",
                        on_click=RepositoryState.handle_upload(
                            rx.upload_files(upload_id="upload1")
                        ),
                        disabled=rx.selected_files("upload1").length() == 0 
                    ),
                    rx.button(
                        "清空",
                        size="2",
                        variant="surface",
                        on_click=rx.clear_selected_files('upload1')
                    ),
                    rx.dialog.close(
                        rx.button(
                            "关闭",
                            size="2",
                            variant="soft",
                        ),
                    ),
                    justify='center',
                    width='100%'
                ),
                width='100%'
            ),
            rx.dialog.root(
                rx.dialog.content(
                    rx.dialog.title("系统信息"),
                    rx.dialog.description(
                        '正在解析文件，请稍等....'
                    ),
                    max_width='450px'
                ),
                open=RepositoryState.upload_dialog_open,
            ),
        ),
        max_width='300px'
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
            max_width="100px",
        ),
        rx.table.cell(
            doc.doc,
            min_width="470px",
            max_width="470px",
        ),
        rx.table.cell(
            rx.checkbox(
                size='3',
                checked=doc.activated,
                on_change=RepositoryState.update_activated(doc),
                variant='surface'
            ),
            min_width="20px",
            max_width="20px",
        ),
        rx.table.cell(
            _dialog_group(doc),
            min_width="140px",
            max_width="140px"
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
                    value=RepositoryState.sort_value,
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
                rx.button(
                    rx.icon('refresh-ccw',size=15), 
                    rx.text('刷新'),
                    size="3", 
                    variant="surface",
                    on_click=RepositoryState.refresh
                ),
                rx.button(
                    rx.icon('file-x-2',size=15), 
                    rx.text('清空'),
                    size="3", 
                    variant="surface",
                    on_click=RepositoryState.clear_doc
                ),
                alert_dialog(
                    description=RepositoryState.base_dialog_description,
                    on_click=RepositoryState.base_dialog_open_change,
                    open=RepositoryState.base_dialog_open
                ),
                align="center",
                justify="end",
                spacing="3",
            ),
            _upload_dialog(),
            spacing="3",
            justify="between",
            wrap="wrap",
            width="100%",
            padding_bottom="1em",
        ),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    _header_cell("key", "file-key"),
                    _header_cell("doc", "file-text"),
                    _header_cell("启用", "circle-check-big"),
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
            height='65vh'
        ),
        _pagination_view(),
        width="100%",
    )
