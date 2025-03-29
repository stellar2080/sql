import reflex as rx

from client.pages import *
from client.state import *

app = rx.App()

app.add_page(index, title='首页')
app.add_page(login, route="/login", title='用户登录')
app.add_page(signup, route="/signup", title='用户注册')
app.add_page(findpwd, route="/findpwd", title='找回密码')
app.add_page(account, route="/account", title='个人中心', on_load=AccountState.on_load)
app.add_page(chat, route="/chat", title='AI问答', on_load=ChatState.on_load)
app.add_page(settings, route="/settings", title='系统设置', on_load=BaseState.check_login)
app.add_page(ai_config, route="/ai_config", title='AI配置', on_load=ChatState.on_load)
app.add_page(chat_record, route="/chat_record", title='问答记录', on_load=ChatRecordState.on_load)