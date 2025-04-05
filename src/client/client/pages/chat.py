import reflex as rx
import reflex_chakra as rc
from .components.sidebar import sidebar_bottom_profile
from .components.loading_icon import loading_icon
from client.state.chat_st import QA, ChatState
from .components.theme_wrap import theme_wrap

def message(qa: QA) -> rx.Component:
    return rx.box(
        rx.box(          
            rx.flex(
                rx.badge(
                    rx.icon("user", size=25),
                    size="3",
                    color=rx.color("gray", 12)
                ),
                rx.box(
                    rx.text(
                        qa.question, 
                        padding="1em",
                        box_shadow="rgba(0, 0, 0, 0.15) 0px 2px 8px",
                        display="inline-block",
                        background_color=rx.color("gray", 4),
                        white_space='pre',
                        text_wrap='pretty',
                        max_width="72em",
                    ),  
                ),
                direction='row',
                align='start',
                spacing='4'
            ),
            text_align="left",
            margin_top="1em",
        ),
        rx.box(
            rx.flex(
                rx.badge(
                    rx.icon("sparkles", size=25),
                    size="3",
                    color=rx.color("gray", 12)
                ),
                rx.vstack(
                    rx.cond(
                        qa.show_text,
                        rx.box(
                            rx.text(
                                qa.answer_text,
                                padding="1em",
                                box_shadow="rgba(0, 0, 0, 0.15) 0px 2px 8px",    
                                display="inline-block",
                                background_color=rx.color("accent", 8),
                                white_space='pre',
                                text_wrap='pretty',
                                max_width="72em",
                            ),
                        ),
                    ),
                    rx.cond(
                        qa.show_table,
                        rx.box(
                            rx.data_table(
                                data=qa.table_datas,
                                columns=qa.table_cols,
                                pagination=True,
                                sort=True,        
                            ),
                            max_width="72em",
                        ),
                    ),
                    rx.cond(
                        qa.show_text & qa.show_table,
                        rx.hstack(
                            rx.tooltip(
                                rx.icon(
                                    "copy",
                                    size=28,
                                    stroke_width=1.5,
                                    cursor="pointer",
                                    flex_shrink="0",
                                    on_click=ChatState.copy_answer_text(qa),
                                ),
                                content='复制文本'
                            ),
                            rx.tooltip(
                                rx.icon(
                                    "clipboard-list",
                                    size=28,
                                    stroke_width=1.5,
                                    cursor="pointer",
                                    flex_shrink="0",
                                    on_click=ChatState.copy_table(qa),
                                ),
                                content='复制表'
                            ),
                            align='center',
                            justify='start',
                            spacing='3'
                        ),
                    ),
                ),
                direction='row',
                align='start',
                spacing='4'
            ),
            text_align="left",
            padding_top="1em",
        ),
        width="100%",
    )


def chat_box() -> rx.Component:
    return rx.vstack(
        rx.box(
            rx.foreach(
                ChatState.current_chat, message
            ), 
            width="100%"
        ),
        py="8",
        flex="1",
        width="100%",
        max_width="80em",
        padding_x="4px",
        align_self="center",
        overflow="hidden",
        padding_bottom="0.2em",
    )


def action_bar() -> rx.Component:
    return rx.center(
        rx.vstack(
            rc.form(
                rx.hstack(
                    rx.input(
                        rx.input.slot(
                            rx.tooltip(
                                rx.icon("info", size=18),
                                content="输入你要转换成SQL的问题。",
                            )
                        ),
                        placeholder="输入你的问题...",
                        id="question",
                        width=["15em", "20em", "45em", "50em", "50em", "50em"],
                    ),
                    rx.button(
                        rx.cond(
                            ChatState.processing,
                            loading_icon(height="1em"),
                            rx.text("发送"),
                        ),
                        disabled=ChatState.processing,
                        type="submit",
                        width='10em',
                        variant='surface'
                    ),
                    rx.button(
                        rx.icon('arrow-down-to-line',size=15),
                        "滚到底部",
                        type='button',
                        variant='surface',
                        on_click=rx.scroll_to("bottom"),
                    ),
                    rx.button(
                        rx.icon('message-circle-off',size=15),
                        "清空对话",
                        type='button',
                        variant='surface',
                        on_click=ChatState.clear_chat,
                        disabled=ChatState.chat_empty
                    ),
                    align_items="center",
                ),
                on_submit=ChatState.AI_process_question,
                reset_on_submit=True,
            ),
            rx.text(
                "AI可能会生成错误答案，请仔细甄别",
                text_align="center",
                font_size=".75em",
                color=rx.color("gray", 10),
            ),
            align_items="center",
        ),
        position="sticky",
        bottom="0",
        left="0",
        padding_y="16px",
        backdrop_filter="auto",
        backdrop_blur="lg",
        border_top=f"1px solid {rx.color('gray', 3)}",
        background_color=rx.color("gray", 2),
        align_items="stretch",
        width="100%",
    )

def chat():
    return theme_wrap(
        rx.box( 
            sidebar_bottom_profile(),
            rc.vstack( 
                rx.heading(
                    'AI问答',
                    size='6'
                ),
                rx.scroll_area(
                    chat_box(),
                    rx.text("",id='bottom'),
                    type="hover",
                    scrollbars="vertical",
                    height=660,
                    width="100%",
                    max_width="80em",
                ),
                action_bar(),
                min_height="100vh",
                align='center',
                spacing="6",
                position="sticky",
                left="15%",
                width="85%",
                padding_top="70px",
            ),
        )
    )
