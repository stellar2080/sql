import os
import sys
import reflex as rx
from reflex.components.radix.themes import theme

CLIENT_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CLIENT_PATH)

from pages import *
from state.account_st import AccountState
from state.chat_st import ChatState
from state.theme_st import ThemeState

app = rx.App(
    theme=theme(
        appearance="dark", 
        has_background=True, 
        radius="large", 
        accent_color="violet",
        gray_color="gray",
        scaling="100%"
    )
)

app.add_page(index)
app.add_page(login, route="/login")
app.add_page(signup, route="/signup")
app.add_page(findpwd, route="/findpwd")
app.add_page(account, route="/account", on_load=AccountState.check_login)
app.add_page(chat, route="/chat", on_load=ChatState.check_login)
app.add_page(settings, route="/settings", on_load=ThemeState.check_login)