import flet as ft
from datetime import datetime
from openai import OpenAI

def create_client(api_key, base_url):
    try:
        client =OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        return client
    except Exception as e:
        return None
def get_ai_response(client, model, user_query, history = [], instruction = "you are a helpful assistant."):
    try:
        messages = [{
            "role": "system",
            "content": instruction
        }]
        if history:
            messages.extend(history[6:])
        messages.append({
            "role": "user",
            "content": user_query
        })
        response = client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return response.choices[0].message.content

    except Exception as e:
        return None


def main(page: ft.Page):
    page.title = "ai bot"
    page.vertical_alignment = ft.MainAxisAlignment.END
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = ft.Padding(10, 20, 10, 10)

    client = None
    chat_history = []
    base_url = "https://api.openai.com/v1"
    api_key = ""
    model = "gpt-3.5-turbo"
    instruction = "you are a helpful assistant."



    def get_cridentials():
        cridentials = page.client_storage.get("cridentials")
        if cridentials:
            return cridentials.get("base_url"), cridentials.get("api_key"), cridentials.get("model"), cridentials.get("instruction")
        return None

    def save_cridentials(base_url, api_key, model, instruction):
        cridentials = {
            "base_url": base_url,
            "api_key": api_key,
            "model": model,
            "instruction": instruction
        }
        page.client_storage.set("cridentials", cridentials)


    base_url_input = ft.TextField(label="Base URL", value=base_url)
    api_key_input = ft.TextField(label="API Key", password=True, can_reveal_password=True, value=api_key)
    model_input = ft.TextField(label="Model", value=model)
    instruction_input = ft.TextField(label="Instruction",value=instruction,expand=True,multiline=True,min_lines=1,max_lines=5)

    user_input = ft.TextField(label="User Input",expand=True,multiline=True,min_lines=1,max_lines=3)

    chat_list = ft.ListView(
        expand=1,
        spacing=10,
        auto_scroll=True,
    )

    def add_message(sender, message):
        time_stamp = datetime.now().strftime("%H:%M:%S")

        if sender == "user":
            color = ft.Colors.BLUE_300
            bg_color = ft.Colors.with_opacity(0.1, ft.Colors.GREY_300)
        elif sender == "ai":
            color = ft.Colors.GREEN_300
            bg_color = ft.Colors.with_opacity(0.1, ft.Colors.BLUE_300)
        else:
            color = ft.Colors.AMBER_300
            bg_color = ft.Colors.with_opacity(0.1, ft.Colors.BLACK)
        
        message_widget = ft.Container(content=ft.Column(tight=True,spacing=10,controls=[
            ft.Row(expand=True,controls=[ft.Text(f"{sender.upper()} ({time_stamp})",color=color,size=12)]),
            ft.Row(expand=True,controls=[ft.Container(expand=1,bgcolor=bg_color,padding=10,content=ft.Markdown(
                message,
                selectable=True,
                code_theme=ft.MarkdownCodeTheme.NIGHT_OWL,
                extension_set=ft.MarkdownExtensionSet.GITHUB_WEB
            ))])
        ]))
        chat_list.controls.append(message_widget)
        page.update()

    def save_clicked(e):
        nonlocal client, chat_history, base_url, api_key, model, instruction

        base_url = base_url_input.value
        api_key = api_key_input.value
        model = model_input.value
        instruction = instruction_input.value

        if base_url and api_key and model and instruction:
            save_cridentials(base_url, api_key, model, instruction)
            chat_history = []
            client = create_client(api_key, base_url)
            chat_list.controls.clear()
            if client is not None:
                add_message("system",f"New credentials added.\nAi model: {model}")
            else:
                add_message("system", "invalid apikey or base url")
        page.go("/")
        page.update()


    def send_clicked(e):
        nonlocal client, chat_history, base_url, api_key, model, instruction
        user_query = user_input.value
        if user_query == "" or client is None or base_url == "" or api_key == "" or model == "" or instruction is None:
            add_message("system", "invalid credentials")
            return
        user_input.value = ""
        add_message("user", user_query)
        add_message("ai", "thinking...")
        output = get_ai_response(client, model, user_query, chat_history, instruction)
        if output is None:
            add_message("system", "invalid apikey or base url")
            return
        chat_history.append({"role": "user", "content": user_query})
        chat_history.append({"role": "assistant", "content": output})
        chat_list.controls.pop()
        add_message("ai", output)

    def clear_clicked(e):
        nonlocal chat_history
        chat_history = []
        chat_list.controls.clear()
        page.update()

    chat_screen = ft.Column(
        expand=True,
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Row([
                ft.Text("OpenAI BOT", size=20,color=ft.Colors.GREEN),
                ft.Row(controls=[
                    ft.IconButton(icon=ft.Icons.SETTINGS, on_click=lambda e: page.go("/settings")),
                    ft.IconButton(icon=ft.Icons.CLEAR,on_click=clear_clicked)],alignment=ft.MainAxisAlignment.SPACE_AROUND)
            ],alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(),
            ft.Container(expand=True,padding=ft.Padding(0,10,0,10), content=chat_list),
            ft.Row(controls=[user_input, ft.IconButton(icon=ft.Icons.SEND,on_click=send_clicked)])
        ]
    )

    settings_screen = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
        base_url_input,
        api_key_input,
        model_input,
        instruction_input,
        ft.Divider(),
        ft.Row(
            width=page.width*0.8 if page.width else 200,
            controls=[
            ft.ElevatedButton("Save", on_click=save_clicked, expand=True),
            ft.ElevatedButton("Back", on_click=lambda _: page.go("/"), expand=True),
        ],alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    ])

    def route_change(route):
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [ft.Container(expand=True,content=chat_screen,padding=ft.Padding(0,30,0,20))],
            )
        )
        if page.route == "/settings":
            page.views.append(
                ft.View(
                    "/settings",
                    [ft.Container(expand=True,content=settings_screen,padding=ft.Padding(0,30,0,20))],
                )
            )
        page.update()


    cridentials = get_cridentials()
    if cridentials is not None:
        base_url, api_key, model, instruction = cridentials
        base_url_input.value = base_url
        api_key_input.value = api_key
        model_input.value = model
        instruction_input.value = instruction
        client = create_client(api_key, base_url)
        if client is not None:
            add_message("system",f"Ai model: {model}")
    else:
        add_message("system", "Setup Cridentials first")
    page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)  # type: ignore

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

if __name__ == "__main__":
    ft.app(target=main)