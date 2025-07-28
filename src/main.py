import flet as ft
from ddgs import DDGS

def main(page: ft.Page):
    page.title = "NEWS APP"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20
    page.theme_mode = ft.ThemeMode.DARK


    news_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)

    topic_input = ft.TextField(
        hint_text="Topic",
        border_radius=ft.border_radius.all(10),
        filled=True,
        expand=True
    )

    def search_news(e):
        topic = topic_input.value
        if topic is None or topic == "":
            return
        news = DDGS().news(topic, region="in-en", max_results=10)
        news_list.controls.clear()
        if not news:
            news_list.controls.append(ft.Text("No news found"))
            page.update()
            return
        for n in news:
            news_container = ft.Container(
                content=ft.Column(
                    [
                        ft.Text(n["date"]),
                        ft.Text(n["title"]),
                        ft.Text(n["body"]),
                        ft.TextButton(n["source"],on_click=lambda _: page.launch_url(n["url"]))
                    ]),
                padding=ft.padding.all(10),
                border_radius=ft.border_radius.all(10),
                bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.WHITE)
            )
            news_list.controls.append(news_container)
            page.update()
            

    search_button = ft.IconButton(
        icon=ft.Icons.SEARCH,
        icon_color=ft.Colors.GREEN_400,
        tooltip="Search",
        on_click=search_news
    )

    page.add(ft.Container(
        padding=ft.padding.all(10),
        expand=True,
        content= ft.Column(expand=True,controls=[
        ft.Row(
            controls=[
                topic_input,
                search_button
            ],
            alignment=ft.MainAxisAlignment.START
        ),
        ft.Container(
            content=news_list,
            expand=True,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=ft.border_radius.all(10),
            padding=ft.padding.all(10)
        )
    ])))


if __name__ == "__main__":
    ft.app(target=main)
