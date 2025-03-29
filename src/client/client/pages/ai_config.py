"""The AI config page."""

import reflex as rx
from client.state.chat_st import ChatState
from .components.sidebar import sidebar_bottom_profile
from .components.theme_wrap import theme_wrap
from .components.alert_dialog import alert_dialog

def platform() -> rx.Component:
    return rx.hstack(
        rx.icon("cog"),
        rx.heading(
            "platform", 
            size="5"
        ),
        rx.tooltip(
            rx.icon("info", size=18),
            content='''
                目前支持通义千问和自定义，选择通义千问请填写model和api_key，选择自定义请填写LLM_HOST和LLM_PORT
            ''',
        ),
        rx.spacer(),
        rx.select(
            ["Tongyi", "Custom"],
            size='3',
            default_value=ChatState.platform,
            name='platform',
            width='25%'
        ),
        align="center",
        width='100%'
    ),

def model() -> rx.Component:
    return rx.hstack(
        rx.icon("cog"),
        rx.heading(
            "model", 
            size="5"
        ),
        rx.tooltip(
            rx.icon("info", size=18),
            content='''
                选择要调用的模型
            ''',
        ),
        rx.spacer(),
        rx.select(
            ["deepseek-v3","qwen-max","qwen-plus"],
            size='3',
            default_value=ChatState.model,
            name='model',
            width='25%'
        ),
        align="center",
        width='100%'
    ),

def api_key() -> rx.Component:
    return rx.hstack(
        rx.icon("cog"),
        rx.heading(
            "api_key", 
            size="5"
        ),
        rx.tooltip(
            rx.icon("info", size=18),
            content='''
                大模型平台的api_key
            ''',
        ),
        rx.spacer(),
        rx.input(
            size='3',
            default_value=ChatState.api_key,
            name='api_key',
            width='60%'
        ),
        align="center",
        width='100%'
    ),

def LLM_HOST() -> rx.Component:
    return rx.hstack(
        rx.icon("cog"),
        rx.heading(
            "LLM_HOST", 
            size="5"
        ),
        rx.tooltip(
            rx.icon("info", size=18),
            content='''
                自部署大模型的host地址
            ''',
        ),
        rx.spacer(),
        rx.input(
            size='3',
            default_value=ChatState.LLM_HOST,
            name='LLM_HOST',
        ),
        align="center",
        width='100%'
    ),

def LLM_PORT() -> rx.Component:
    return rx.hstack(
        rx.icon("cog"),
        rx.heading(
            "LLM_PORT", 
            size="5"
        ),
        rx.tooltip(
            rx.icon("info", size=18),
            content='''
                自部署大模型的端口号
            ''',
        ),
        rx.spacer(),
        rx.input(
            size='3',
            default_value=ChatState.get_LLM_PORT,
            name='LLM_PORT'
        ),
        align="center",
        width='100%'
    ),

def MAX_ITERATIONS() -> rx.Component:
    return rx.hstack(
        rx.icon("cog"),
        rx.heading(
            "MAX_ITERATIONS", 
            size="5"
        ),
        rx.tooltip(
            rx.icon("info", size=18),
            content='''
                Reviser智能体的最大执行轮次，若值为0，则不调用Reviser，
                值范围：[0,10]，整数
            ''',
        ),
        rx.spacer(),
        rx.input(
            size='3',
            default_value=ChatState.get_MAX_ITERATIONS,
            name='MAX_ITERATIONS'
        ),
        align="center",
        width='100%'
    ),

def DO_SAMPLE() -> rx.Component:
    return rx.hstack(
        rx.icon("cog"),
        rx.heading(
            "DO_SAMPLE", 
            size="5"
        ),
        rx.tooltip(
            rx.icon("info", size=18),
            content='''
                控制是否进行采样输出。
                如果打开，那么LLM会根据每个词的概率进行随机选择。
                如果关闭，那么LLM会直接选择概率最高的词。
            ''',
        ),
        rx.spacer(),
        rx.switch(
            size='3',
            default_checked=ChatState.DO_SAMPLE,
            name='DO_SAMPLE'
        ),
        align="center",
        width='100%'
    ),

def TEMPERATURE() -> rx.Component:
    return rx.hstack(
        rx.icon("cog"),
        rx.heading(
            "TEMPERATURE", 
            size="5"
        ),
        rx.tooltip(
            rx.icon("info", size=18),
            content='''
                采样温度，控制模型生成文本的多样性。
                temperature越高，生成的文本更多样，反之，生成的文本更确定。
                取值范围：[0, 2)，小数
            ''',
        ),
        rx.spacer(),
        rx.input(
            size='3',
            default_value=ChatState.get_TEMPERATURE,
            name='TEMPERATURE'
        ),
        align="center",
        width='100%'
    ),

def TOP_P() -> rx.Component:
    return rx.hstack(
        rx.icon("cog"),
        rx.heading(
            "TOP_P", 
            size="5"
        ),
        rx.tooltip(
            rx.icon("info", size=18),
            content='''
                核采样的概率阈值，控制模型生成文本的多样性。
                top_p越高，生成的文本更多样。反之，生成的文本更确定。
                取值范围：(0,1.0]，小数
            ''',
        ),
        rx.spacer(),
        rx.input(
            size='3',
            default_value=ChatState.get_TOP_P,
            name='TOP_P'
        ),
        align="center",
        width='100%'
    ),

def MAX_TOKENS() -> rx.Component:
    return rx.hstack(
        rx.icon("cog"),
        rx.heading(
            "MAX_TOKENS", 
            size="5"
        ),
        rx.tooltip(
            rx.icon("info", size=18),
            content='''
                本次请求返回的最大Token数。
                max_tokens 的设置不会影响大模型的生成过程，如果模型生成的 Token 数超过max_tokens，本次请求会返回截断后的内容。
                取值范围：[100,8192]，整数
            ''',
        ),
        rx.spacer(),
        rx.input(
            size='3',
            default_value=ChatState.get_MAX_TOKENS,
            name='MAX_TOKENS'
        ),
        align="center",
        width='100%'
    ),

def N_RESULTS() -> rx.Component:
    return rx.hstack(
        rx.icon("cog"),
        rx.heading(
            "N_RESULTS", 
            size="5"
        ),
        rx.tooltip(
            rx.icon("info", size=18),
            content='''
                控制向量检索返回的相似度最高的元素个数，
                取值范围：[1,10]，整数
            ''',
        ),
        rx.spacer(),
        rx.input(
            size='3',
            default_value=ChatState.get_N_RESULTS,
            name='N_RESULTS'
        ),
        align="center",
        width='100%'
    ),

def E_HINT_THRESHOLD() -> rx.Component:
    return rx.hstack(
        rx.icon("cog"),
        rx.heading(
            "E_HINT_THRESHOLD", 
            size="5"
        ),
        rx.tooltip(
            rx.icon("info", size=18),
            content='''
                控制extractor智能体检索知识库的相似度阈值，
                取值范围：(0,1.00]，小数
            ''',
        ),
        rx.spacer(),
        rx.input(
            size='3',
            default_value=ChatState.get_E_HINT_THRESHOLD,
            name='E_HINT_THRESHOLD'
        ),
        align="center",
        width='100%'
    ),

def E_COL_THRESHOLD() -> rx.Component:
    return rx.hstack(
        rx.icon("cog"),
        rx.heading(
            "E_COL_THRESHOLD", 
            size="5"
        ),
        rx.tooltip(
            rx.icon("info", size=18),
            content='''
                控制extractor智能体检索列名的相似度阈值，
                取值范围：(0,1.00]，小数
            ''',
        ),
        rx.spacer(),
        rx.input(
            size='3',
            default_value=ChatState.get_E_COL_THRESHOLD,
            name='E_COL_THRESHOLD'
        ),
        align="center",
        width='100%'
    ),

def E_VAL_THRESHOLD() -> rx.Component:
    return rx.hstack(
        rx.icon("cog"),
        rx.heading(
            "E_VAL_THRESHOLD", 
            size="5"
        ),
        rx.tooltip(
            rx.icon("info", size=18),
            content='''
                控制extractor智能体检索列值的相似度阈值，
                取值范围：(0,1.00]，小数
            ''',
        ),
        rx.spacer(),
        rx.input(
            size='3',
            default_value=ChatState.get_E_VAL_THRESHOLD,
            name='E_VAL_THRESHOLD'
        ),
        align="center",
        width='100%'
    ),

def E_COL_STRONG_THRESHOLD() -> rx.Component:
    return rx.hstack(
        rx.icon("cog"),
        rx.heading(
            "E_COL_STRONG_THRESHOLD", 
            size="5"
        ),
        rx.tooltip(
            rx.icon("info", size=18),
            content='''
                在extractor智能体处理过程中，如果某列名和问题的相似度超过该阈值，则会视为与问题强关联的元素，
                强关联元素将直接加入下一轮次智能体的处理，
                取值范围：(0,1.00]，小数
            ''',
        ),
        rx.spacer(),
        rx.input(
            size='3',
            default_value=ChatState.get_E_COL_STRONG_THRESHOLD,
            name='E_COL_STRONG_THRESHOLD'
        ),
        align="center",
        width='100%'
    ),

def E_VAL_STRONG_THRESHOLD() -> rx.Component:
    return rx.hstack(
        rx.icon("cog"),
        rx.heading(
            "E_VAL_STRONG_THRESHOLD", 
            size="5"
        ),
        rx.tooltip(
            rx.icon("info", size=18),
            content='''
                在extractor智能体处理过程中，如果某列值和问题的相似度超过该阈值，则会视为与问题强关联的元素，
                强关联元素将直接加入下一轮次智能体的处理，
                取值范围：(0,1.00]，小数
            ''',
        ),
        rx.spacer(),
        rx.input(
            size='3',
            default_value=ChatState.get_E_VAL_STRONG_THRESHOLD,
            name='E_VAL_STRONG_THRESHOLD'
        ),
        align="center",
        width='100%'
    ),

def F_HINT_THRESHOLD() -> rx.Component:
    return rx.hstack(
        rx.icon("cog"),
        rx.heading(
            "F_HINT_THRESHOLD", 
            size="5"
        ),
        rx.tooltip(
            rx.icon("info", size=18),
            content='''
                控制filter智能体检索知识库的相似度阈值，
                取值范围：(0,1.00]，小数
            ''',
        ),
        rx.spacer(),
        rx.input(
            size='3',
            default_value=ChatState.get_F_HINT_THRESHOLD,
            name='F_HINT_THRESHOLD'
        ),
        align="center",
        width='100%'
    ),

def F_COL_THRESHOLD() -> rx.Component:
    return rx.hstack(
        rx.icon("cog"),
        rx.heading(
            "F_COL_THRESHOLD", 
            size="5"
        ),
        rx.tooltip(
            rx.icon("info", size=18),
            content='''
                控制filter智能体检索列名的相似度阈值，
                取值范围：(0,1.00]，小数
            ''',
        ),
        rx.spacer(),
        rx.input(
            size='3',
            default_value=ChatState.get_F_COL_THRESHOLD,
            name='F_COL_THRESHOLD'
        ),
        align="center",
        width='100%'
    ),

def F_LSH_THRESHOLD() -> rx.Component:
    return rx.hstack(
        rx.icon("cog"),
        rx.heading(
            "F_LSH_THRESHOLD", 
            size="5"
        ),
        rx.tooltip(
            rx.icon("info", size=18),
            content='''
                控制filter智能体LSH算法检索列值的相似度阈值，
                取值范围：(0,1.00]，小数
            ''',
        ),
        rx.spacer(),
        rx.input(
            size='3',
            default_value=ChatState.get_F_LSH_THRESHOLD,
            name='F_LSH_THRESHOLD'
        ),
        align="center",
        width='100%'
    ),

def F_VAL_THRESHOLD() -> rx.Component:
    return rx.hstack(
        rx.icon("cog"),
        rx.heading(
            "F_VAL_THRESHOLD", 
            size="5"
        ),
        rx.tooltip(
            rx.icon("info", size=18),
            content='''
                控制filter智能体检索列值的相似度阈值，
                取值范围：(0,1.00]，小数
            ''',
        ),
        rx.spacer(),
        rx.input(
            size='3',
            default_value=ChatState.get_F_VAL_THRESHOLD,
            name='F_VAL_THRESHOLD'
        ),
        align="center",
        width='100%'
    ),

def F_COL_STRONG_THRESHOLD() -> rx.Component:
    return rx.hstack(
        rx.icon("cog"),
        rx.heading(
            "F_COL_STRONG_THRESHOLD", 
            size="5"
        ),
        rx.tooltip(
            rx.icon("info", size=18),
            content='''
                在filter智能体处理过程中，如果某列名和问题的相似度超过该阈值，则会视为与问题强关联的元素，
                强关联元素将直接加入下一轮次智能体的处理，
                取值范围：(0,1.00]，小数
            ''',
        ),
        rx.spacer(),
        rx.input(
            size='3',
            default_value=ChatState.get_F_COL_STRONG_THRESHOLD,
            name='F_COL_STRONG_THRESHOLD'
        ),
        align="center",
        width='100%'
    ),

def F_VAL_STRONG_THRESHOLD() -> rx.Component:
    return rx.hstack(
        rx.icon("cog"),
        rx.heading(
            "F_VAL_STRONG_THRESHOLD", 
            size="5"
        ),
        rx.tooltip(
            rx.icon("info", size=18),
            content='''
                在filter智能体处理过程中，如果某列值和问题的相似度超过该阈值，则会视为与问题强关联的元素，
                强关联元素将直接加入下一轮次智能体的处理，
                取值范围：(0,1.00]，小数
            ''',
        ),
        rx.spacer(),
        rx.input(
            size='3',
            default_value=ChatState.get_F_VAL_STRONG_THRESHOLD,
            name='F_VAL_STRONG_THRESHOLD'
        ),
        align="center",
        width='100%'
    ),

def G_HINT_THRESHOLD() -> rx.Component:
    return rx.hstack(
        rx.icon("cog"),
        rx.heading(
            "G_HINT_THRESHOLD", 
            size="5"
        ),
        rx.tooltip(
            rx.icon("info", size=18),
            content='''
                控制generator智能体检索知识库的相似度阈值，
                取值范围：(0,1.00]，小数
            ''',
        ),
        rx.spacer(),
        rx.input(
            size='3',
            default_value=ChatState.get_G_HINT_THRESHOLD,
            name='G_HINT_THRESHOLD'
        ),
        align="center",
        width='100%'
    ),

def ai_config() -> rx.Component:
    return theme_wrap(
        rx.box( 
            sidebar_bottom_profile(),
            rx.center(
                rx.form(
                    rx.vstack(
                        rx.heading(
                            "AI配置", 
                            size="6"
                        ),
                        rx.scroll_area(
                            rx.vstack(
                                platform(),
                                model(),
                                api_key(),
                                LLM_HOST(),
                                LLM_PORT(),
                                MAX_ITERATIONS(),
                                DO_SAMPLE(),
                                TEMPERATURE(),
                                TOP_P(),
                                MAX_TOKENS(),
                                N_RESULTS(),
                                E_HINT_THRESHOLD(),
                                E_COL_THRESHOLD(),
                                E_VAL_THRESHOLD(),
                                E_COL_STRONG_THRESHOLD(),
                                E_VAL_STRONG_THRESHOLD(),
                                F_HINT_THRESHOLD(),
                                F_COL_THRESHOLD(),
                                F_LSH_THRESHOLD(),
                                F_VAL_THRESHOLD(),
                                F_COL_STRONG_THRESHOLD(),
                                F_VAL_STRONG_THRESHOLD(),
                                G_HINT_THRESHOLD(),
                                spacing="7",
                                align='center',
                                justify='center',
                            ),
                            type="hover",
                            scrollbars="vertical",
                            height=600,
                            width="100%",
                            padding_x='2em',
                            padding_y='1em'
                        ),
                        rx.button(
                            "保存设置",
                            type='submit',
                            size='3'
                        ),
                        rx.text(
                            "若不保存设置，新配置将不会生效",
                            text_align="center",
                            font_size=".75em",
                            color=rx.color("gray", 10),
                        ),
                        align='center',
                        justify='center',
                        spacing='6',
                        width='100%',
                        padding_top="70px",
                        padding_bottom="50px",
                    ),
                    on_submit=ChatState.save_ai_config,
                    width="60%",
                ),
                position="sticky",
                left="15%",
                width="85%",
            ),
            alert_dialog(
                description=ChatState.base_dialog_description,
                on_click=ChatState.base_dialog_open_change,
                open=ChatState.base_dialog_open
            ),
        )
    )