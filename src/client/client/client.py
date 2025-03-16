import os
import sys
import reflex as rx
from reflex.components.radix.themes import theme

CLIENT_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CLIENT_PATH)

from pages import index, login, signup, findpwd, account
from state.account_st import AccountState

app = rx.App(
    theme=theme(
        appearance="dark", 
        has_background=True, 
        radius="large", 
        accent_color="violet",
        gray_color='gray'
    )
)

app.add_page(index)
app.add_page(login, route="/login")
app.add_page(signup, route="/signup")
app.add_page(findpwd, route="/findpwd")
app.add_page(account, route="/account", on_load=AccountState.check_login)