import reflex as rx
import pandas as pd

class QA(rx.Base):

    question: str
    answer_text: str
    table_cols: list
    table_datas: list
    text_loading: bool
    table_loading: bool