import reflex as rx
from .base_st import BaseState
import numpy as np
import pandas as pd
from client.db_model import ChatRecord
from datetime import datetime
from .data_class.qa import QA
from typing import List, Dict

class Item(rx.Base):
    """The item class."""

    question: str
    sql: str
    sql_result: Dict[str, List]
    create_time: datetime

class ChatRecordState(BaseState):

    @rx.event
    def on_load(self):
        if not self.logged_in:
            return rx.redirect("/login")
        self.load_entries()

    items: List[Item] = []

    search_value: str = ""
    sort_value: str = ""
    sort_reverse: bool = False

    total_items: int = 0
    offset: int = 0
    limit: int = 10

    @rx.var(cache=True)
    def filtered_sorted_items(self) -> List[Item]:
        items = self.items

        if self.sort_value:
            items = sorted(
                items,
                key=lambda item: str(getattr(item, self.sort_value)).lower(),
                reverse=self.sort_reverse,
            )

        if self.search_value:
            search_value = self.search_value.lower()
            items = [
                item
                for item in items
                if any(
                    search_value in str(getattr(item, attr)).lower()
                    for attr in [
                        "question",
                        "sql",
                        "sql_result",
                        "create_time",
                    ]
                )
            ]

        return items

    @rx.var(cache=True)
    def page_number(self) -> int:
        return (self.offset // self.limit) + 1

    @rx.var(cache=True)
    def total_pages(self) -> int:
        return (self.total_items // self.limit) + (
            1 if self.total_items % self.limit else 0
        )

    @rx.var(cache=True, initial_value=[])
    def get_current_page(self) -> list[Item]:
        start_index = self.offset
        end_index = start_index + self.limit
        return self.filtered_sorted_items[start_index:end_index]

    def prev_page(self):
        if self.page_number > 1:
            self.offset -= self.limit

    def next_page(self):
        if self.page_number < self.total_pages:
            self.offset += self.limit

    def first_page(self):
        self.offset = 0

    def last_page(self):
        self.offset = (self.total_pages - 1) * self.limit

    def load_entries(self):
        with rx.session() as session:
            chat_records = session.exec(
                ChatRecord.select().where(
                    ChatRecord.user_id == self.user_id
                )
            ).all()
            self.items = [
                Item(
                    question=chat_record.question, 
                    sql=chat_record.sql,
                    sql_result=chat_record.sql_result, 
                    create_time=chat_record.create_time
                ) for chat_record in chat_records
            ]
        self.total_items = len(self.items)

    def toggle_sort(self):
        self.sort_reverse = not self.sort_reverse
        self.load_entries()


