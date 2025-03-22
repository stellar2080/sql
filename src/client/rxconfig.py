import os
import sys
import reflex as rx

CLIENT_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CLIENT_PATH)
target_db_path = os.path.join(CLIENT_PATH,"dataset","Bank_Financials.sqlite")

config = rx.Config(
    app_name="client",
    db_url="sqlite:///"+CLIENT_PATH+"/db/reflex.db",
    frontend_port=3000,
    backend_port=8001,
)