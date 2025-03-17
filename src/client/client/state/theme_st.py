import reflex as rx
from .auth_st import AuthState

class ThemeState(AuthState):
    """The state for the theme of the app."""

    appearance: str = "dark"

    accent_color: str = "blue"

    gray_color: str = "gray"

    radius: str = "large"

    scaling: str = "100%"

    @rx.event
    def set_appearance(self, appearance: str):
        self.appearance = appearance

    @rx.event
    def set_accent_color(self, accent_color: str):
        self.accent_color = accent_color

    @rx.event
    def set_gray_color(self, gray_color: str):
        self.gray_color = gray_color

    @rx.event
    def set_radius(self, radius: str):
        self.radius = radius

    @rx.event
    def set_scaling(self, scaling: str):
        self.scaling = scaling