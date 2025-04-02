import reflex as rx
from .base_st import BaseState
from datetime import datetime
from typing import List, Dict
from client.manager.manager import Manager

class Doc(rx.Base):

    key_id: str
    key: str 
    doc_id: str
    doc: str

class RepositoryState(BaseState):

    @rx.event
    async def on_load(self):
        if not self.logged_in:
            return rx.redirect("/login")
        await self.load_entries()

    docs: List[Doc] = []

    search_value: str = ""
    sort_value: str = ""
    sort_reverse: bool = False

    total_items: int = 0
    offset: int = 0
    limit: int = 10

    delete_dialog_open: bool = False

    @rx.event
    def delete_dialog_open_change(self):
        self.delete_dialog_open = not self.delete_dialog_open

    def init_manager(self):
        return Manager(
            config={
                'user_id': self.user_id,
                'vectordb_only': True,
                'vectordb_host': 'localhost',
                'vectordb_port': '8000',
            },
        )

    @rx.event
    async def delete_doc(self, doc: Doc):
        self.docs.remove(doc)
        manager = self.init_manager()
        await manager.remove_doc(embedding_id=[doc.key_id,doc.doc_id],user_id=self.user_id)

    @rx.event
    def set_sort_value(self, sort_value: str):
        self.sort_value = sort_value

    @rx.event
    def set_search_value(self, search_value: str):
        self.search_value = search_value

    @rx.var(cache=True)
    def filtered_sorted_items(self) -> List[Doc]:
        docs = self.docs

        if self.sort_value:
            docs = sorted(
                docs,
                key=lambda item: str(getattr(item, self.sort_value)).lower(),
                reverse=self.sort_reverse,
            )

        if self.search_value:
            search_value = self.search_value.lower()
            docs = [
                item
                for item in docs
                if any(
                    search_value in str(getattr(item, attr)).lower()
                    for attr in [
                        "key",
                        "doc",
                    ]
                )
            ]

        return docs

    @rx.var(cache=True)
    def page_number(self) -> int:
        return (self.offset // self.limit) + 1

    @rx.var(cache=True)
    def total_pages(self) -> int:
        return (self.total_items // self.limit) + (
            1 if self.total_items % self.limit else 0
        )

    @rx.var(cache=True, initial_value=[])
    def get_current_page(self) -> list[Doc]:
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

    @rx.event
    async def load_entries(self):
        manager = self.init_manager()
        key_zip, tip_zip = await manager.get_repository(user_id=self.user_id)
        key_list=[]
        tip_list=[]
        if key_zip:
            key_list = [
                Doc(
                    key_id=key[0],
                    key=key[1],
                    doc_id=key[2],
                    doc=key[3],
                )
                for key in key_zip
            ]
        if tip_zip:
            tip_list = [
                Doc(
                    key_id="",
                    key="",
                    doc_id=tip[0],
                    doc=tip[1],
                )
                for tip in tip_zip
            ]
        self.docs=key_list+tip_list
        self.total_items = len(self.docs)

    def toggle_sort(self):
        self.sort_reverse = not self.sort_reverse
        self.load_entries()


