import os
import sys
import reflex as rx
from reflex.components.radix.themes import theme

CLIENT_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CLIENT_PATH)

from pages import *
from state.account_st import AccountState
from state.chat_st import ChatState
from state.settings_st import SettingsState

app = rx.App()

app.add_page(index)
app.add_page(login, route="/login", title='用户登录')
app.add_page(signup, route="/signup", title='用户注册')
app.add_page(findpwd, route="/findpwd", title='找回密码')
app.add_page(account, route="/account", title='个人中心', on_load=AccountState.check_login)
app.add_page(chat, route="/chat", title='AI问答', on_load=ChatState.check_login)
app.add_page(settings, route="/settings", title='系统设置', on_load=SettingsState.check_login)