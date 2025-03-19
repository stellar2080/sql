import reflex as rx
import reflex_chakra as rc
from .components.sidebar import sidebar_bottom_profile
from .components.loading_icon import loading_icon
from state.chat_st import QA, ChatState
from .components.theme_wrap import theme_wrap

def message(qa: QA) -> rx.Component:
    return rx.box(
        rx.box(          
            rx.flex(
                rx.badge(
                    rx.flex(
                        rx.icon("user", size=25),
                        direction="row",
                        align="center",
                    ),
                    size="2",
                    color=rx.color("gray", 12)
                ),
                rx.markdown(
                    qa.question,
                    background_color=rx.color("gray", 4),
                    color=rx.color("gray", 12),
                    display="inline-block", 
                    padding_x="1em", 
                    padding_y='0.1em',
                    max_width=["30em", "30em", "50em", "50em", "50em", "50em"],
                ),
                direction='row',
                align='center',
                spacing='4'
            ),
            text_align="left",
            margin_top="1em",
        ),
        rx.box(
            rx.flex(
                rx.badge(
                    rx.flex(
                        rx.icon("sparkles", size=25),
                        direction="row",
                        align="center",
                    ),
                    size="2",
                    color=rx.color("gray", 12)
                ),
                rx.markdown(
                    qa.answer,
                    background_color=rx.color("accent", 4),
                    color=rx.color("gray", 12),
                    display="inline-block", 
                    padding_x="1em", 
                    padding_y='0.1em',
                    max_width=["30em", "30em", "50em", "50em", "50em", "50em"]
                ),
                direction='row',
                align='center',
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
                ChatState.chats[ChatState.current_chat], message
            ), 
            width="100%"
        ),
        py="8",
        flex="1",
        width="100%",
        max_width="50em",
        padding_x="4px",
        align_self="center",
        overflow="hidden",
        padding_bottom="5em",
    )


def action_bar() -> rx.Component:
    return rx.center(
        rx.vstack(
            rc.form(
                rc.form_control(
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
                            type="submit",
                        ),
                        align_items="center",
                    ),
                    is_disabled=ChatState.processing,
                ),
                on_submit=ChatState.process_question,
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
            rx.box(
                rc.vstack( 
                    chat_box(),
                    action_bar(),
                    min_height="100vh",
                    align_items="stretch",
                    spacing="0",
                ),
                position="sticky",
                left="15%",
                width="85%",
            ),
        )
    )
