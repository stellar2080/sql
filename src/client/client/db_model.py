import datetime
from sqlmodel import Field

import reflex as rx

class User(rx.Model, table=True):

    user_id: str = Field(primary_key=True)
    username: str
    password: str
    email: str

class Settings(rx.Model, table=True):

    user_id: str = Field(primary_key=True)
    accent_color: str
    gray_color: str
    radius: str
    scaling: str