import os
import reflex as rx

dir = os.path.dirname(os.path.abspath(__file__))

config = rx.Config(
    app_name="client",
    db_url="sqlite:///"+dir+"/db/reflex.db",
)