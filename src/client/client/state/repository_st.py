import reflex as rx
from .base_st import BaseState
from typing import List
from client.manager.manager import Manager

class Doc(rx.Base):

    key_id: str
    key: str 
    doc_id: str
    doc: str
    activated: bool

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

    upload_dialog_open: bool = False
    
    @rx.event
    def upload_dialog_open_change(self):
        self.upload_dialog_open = not self.upload_dialog_open

    def init_manager(self):
        return Manager(
            config={
                'user_id': self.user_id,
                'vectordb_only': True,
                'vectordb_host': '127.0.0.1',
                'vectordb_port': '8000',
            },
        )

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
        key_zip, tip_zip = await manager.get_repository()
        key_list=[]
        tip_list=[]
        if key_zip:
            key_list = [
                Doc(
                    key_id=key[0],
                    key=key[1],
                    doc_id=key[2],
                    doc=key[3],
                    activated=True if key[4] == 1 else False
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
                    activated=True if tip[2] == 1 else False
                )
                for tip in tip_zip
            ]
        self.docs=key_list+tip_list
        self.total_items = len(self.docs)

    async def toggle_sort(self):
        self.sort_reverse = not self.sort_reverse
        await self.load_entries()

    @rx.event
    async def refresh(self):
        await self.load_entries()   
        self.setvar("search_value","")
        self.setvar("sort_value","")
        self.setvar("sort_reverse",False)
        return rx.toast.success("刷新成功", duration=2000)

    @rx.event
    async def delete_doc(self, doc: Doc):
        self.docs.remove(doc)
        manager = self.init_manager()
        if doc.key_id != "":
            await manager.remove_doc(embedding_id=[doc.key_id,doc.doc_id])
        else:
            await manager.remove_doc(embedding_id=doc.doc_id)
        return rx.toast.success("删除成功", duration=2000)

    @rx.event
    async def update_activated(self, doc: Doc):
        doc.activated = not doc.activated
        manager = self.init_manager()
        if doc.key_id != "":
            for item in self.docs:
                if item.key_id == doc.key_id:
                    item.activated = doc.activated
                    break   
            await manager.update_activated(
                embedding_id=doc.key_id,
                activated=1 if doc.activated else 0,
            )
        else:
            for item in self.docs:
                if item.doc_id == doc.doc_id:
                    item.activated = doc.activated
                    break
            await manager.update_activated(
                embedding_id=doc.doc_id,
                activated=1 if doc.activated else 0,
            )
        return rx.toast.success("修改成功", duration=2000)
    
    @rx.event
    async def handle_upload(
        self, files: list[rx.UploadFile]
    ):
        manager = self.init_manager()
        for file in files:
            if not file._deprecated_filename.endswith('.txt'):
                yield rx.toast.error("仅支持txt格式的文件", duration=2000)
                return
        yield self.upload_dialog_open_change()
        for file in files:
            for bytes_line in file.file.readlines():
                text_line = bytes_line.decode('utf-8').strip()
                await manager.add_doc(text_line)
        yield self.upload_dialog_open_change()
        yield rx.toast.success('文件已解析完毕', duration=2000)
        await self.load_entries()

    @rx.event
    async def clear_doc(
        self
    ):
        self.docs.clear()
        self.total_items = len(self.docs)
        self.setvar("search_value","")
        self.setvar("sort_value","")
        self.setvar("sort_reverse",False)
        manager = self.init_manager()
        await manager.clear_doc()
        return rx.toast.success('清空成功',duration=2000)
