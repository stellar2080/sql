import reflex as rx
from .auth_st import AuthState

class QA(rx.Base):
    """A question and answer pair."""

    question: str
    answer: str

DEFAULT_CHATS = {
    "Intros": [],
}

class ChatState(AuthState):

    chats: dict[str, list[QA]] = DEFAULT_CHATS

    current_chat = "Intros"

    question: str

    processing: bool = False

    new_chat_name: str = ""

    def create_chat(self):
        self.current_chat = self.new_chat_name
        self.chats[self.new_chat_name] = []

    def delete_chat(self):
        del self.chats[self.current_chat]
        if len(self.chats) == 0:
            self.chats = DEFAULT_CHATS
        self.current_chat = list(self.chats.keys())[0]

    def set_chat(self, chat_name: str):
        self.current_chat = chat_name

    @rx.var(cache=True)
    def chat_titles(self) -> list[str]:
        return list(self.chats.keys())

    async def process_question(self, form_data):
        question = form_data["question"]

        if question == "":
            return

        model = self.AI_process_question

        async for value in model(question):
            yield value

    async def AI_process_question(self, question: str):
        qa = QA(question=question, answer="")
        self.chats[self.current_chat].append(qa)

        self.processing = True
        yield

        messages = [
            {
                "role": "system",
                "content": "You are a friendly chatbot named Reflex. Respond in markdown.",
            }
        ]
        for qa in self.chats[self.current_chat]:
            messages.append({"role": "user", "content": qa.question})
            messages.append({"role": "assistant", "content": qa.answer})

        messages = messages[:-1]

        self.chats[self.current_chat][-1].answer = "水水水水水水水水水水水水水水水水水水水" + \
        "水水水水水水水水水水水水水水水水水水水水水水水水水水水水水水水水水水水水水水水水水水水水水水水水水水水水水水水"
            
        # # Stream the results, yielding after every word.
        # for item in session:
        #     if hasattr(item.choices[0].delta, "content"):
        #         answer_text = item.choices[0].delta.content
        #         # Ensure answer_text is not None before concatenation
        #         if answer_text is not None:
        #             self.chats[self.current_chat][-1].answer += answer_text
        #         else:
        #             # Handle the case where answer_text is None, perhaps log it or assign a default value
        #             # For example, assigning an empty string if answer_text is None
        #             answer_text = ""
        #             self.chats[self.current_chat][-1].answer += answer_text
        #         self.chats = self.chats
        #         yield

        self.processing = False