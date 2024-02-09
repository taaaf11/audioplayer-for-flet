from audioplayer import AudioPlayer
import flet as ft


def main(page: ft.Page):
    page.add(AudioPlayer(page, "C:\\Users\\Altaaf\\Music"))


ft.app(main)
