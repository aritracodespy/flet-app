
import flet as ft
import json
from google import genai

ai_model = "gemini-2.0-flash-lite-001"


def main(page: ft.Page):
    page.title = "Flet API Client"
    page.vertical_alignment = ft.MainAxisAlignment.START

    def get_key():
        data = page.client_storage.get("apikey")
        return json.loads(data) if data else ""

    def save_key(keys):
        page.client_storage.set("apikey", json.dumps(keys))

    response_list = ft.ListView(expand=True, spacing=2, auto_scroll=True)
    input_field = ft.TextField(expand=True, label="Your query..",  multiline= True, max_lines=3, min_lines=1,autofocus = False)

    key_input = ft.TextField(expand=True, label="Enter Api Key",value=get_key(), multiline= True, max_lines=3, min_lines=1)

    def save_api_key(e):
        key = key_input.value
        page.close(dlg_key)
        if key == "":
           print("enpty")
           return
        save_key(key)
        top_button.icon_color = ft.Colors.GREEN
        page.update()
        print(key)


    def send_post(e):
        user_input = input_field.value
        key = get_key()
        if key == "" or user_input == "":
            response_list.controls.append(ft.Text("Add a valid apikey!")) if key == "" else response_list.controls.append(ft.Text("enter a prompty!"))
            page.update()
            return
        try:

            response_list.controls.append(
                 ft.Row(controls=[ft.Container(expand=True,padding=ft.Padding(20,5,20,5),margin=10,border_radius=8,
                                      bgcolor=ft.Colors.GREY_500,
                                      content=ft.Text(user_input,
                                                      color=ft.Colors.BLACK,
                                                      size=16,
                                                      text_align=ft.TextAlign.RIGHT)
                        )], alignment=ft.MainAxisAlignment.END,expand=True))


            client = genai.Client(api_key=key)
            
            page.update()

            response = client.models.generate_content(
                model = "gemini-2.0-flash-lite-001", contents = str(user_input)
            )

            response_list.controls.append(ft.Container(
                content=ft.Markdown(response.text),
                expand=True,
                padding=20,
                margin=10,
                border_radius=8,
                bgcolor=ft.Colors.GREY_800))


        except Exception as ex:
            response_list.controls.append(ft.Text(f"Exception: {ex}"))
        finally:
            input_field.autofocus = False

            input_field.value = ""
            page.update()


    dlg_key = ft.AlertDialog(
            modal=True,
            title=ft.Text("Add a new Apikey"),
            content=ft.Column(expand=False,tight=True, controls=[key_input,ft.TextButton("Dont have a api key GoTo ai.google.dev Webside",
                                   on_click=lambda _: page.launch_url("https://ai.google.dev/"))]),
            actions=[
                ft.TextButton("ADD", on_click = save_api_key),
                ft.TextButton("Cancel", on_click=lambda e: page.close(dlg_key)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )


    top_button = ft.ElevatedButton(
        icon_color = ft.Colors.RED_300,
        text="Api Key",
        icon=ft.Icons.CIRCLE,
        on_click=lambda e: page.open(dlg_key)
    )

    bottom_row = ft.Row(
        controls=[
            input_field,
            ft.IconButton(icon=ft.Icons.SEND,icon_size=40,icon_color=ft.Colors.WHITE,padding=ft.Padding(30,0,30,0),on_click=send_post)
        ],
        alignment=ft.MainAxisAlignment.END,spacing=20,
    )

    clr_pop = ft.PopupMenuButton(
        items=[
            ft.PopupMenuItem(icon=ft.Icons.CLEAR, text="Clear",on_click=lambda _: [response_list.controls.clear(),page.update()])])


    page.add(ft.Container(expand=True,padding=ft.Padding(0,20,0,20),content=ft.Column(expand =True, controls=[
             ft.Row([
                ft.Text("Ai ChatBot Python",color=ft.Colors.YELLOW,size=20,weight=ft.FontWeight.W_500),
                ft.Row([top_button,clr_pop],alignment=ft.MainAxisAlignment.END)],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
             response_list,
             bottom_row,
        ])
    ))


    key = get_key()
    top_button.icon_color = ft.Colors.RED if key == "" else ft.Colors.GREEN
    page.update()

ft.app(target=main)
