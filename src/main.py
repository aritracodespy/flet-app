import flet as ft
from datetime import datetime
from openai import OpenAI


def create_client(api_key, base_url):
    try:
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        return client
    except Exception:
        return None


def get_ai_response(client, model, chat_messages, instruction=""):
    try:
        messages = [{
            "role": "system",
            "content": instruction
        }]
        messages.extend(chat_messages[-10:])
        response = client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return response.choices[0].message.content

    except Exception:
        return None


def main(page: ft.Page):
    page.title = "ai bot"
    page.vertical_alignment = ft.MainAxisAlignment.END
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = ft.Padding(10, 20, 10, 10)

    client = None
    chat_history = []
    base_url = ""
    api_key = ""
    model = ""
    instruction = ""

    # ---------- Storage ----------
    def get_credentials():
        credentials = page.client_storage.get("credentials")
        if credentials:
            return credentials
        return None

    def save_credentials(data):
        page.client_storage.set("credentials", data)

    def clear_credentials():
        page.client_storage.remove("credentials")

    def get_options():
        credentials = get_credentials()
        options = []
        if credentials is None:
            return options
        models = list(credentials.keys())
        for model in models:
            options.append(ft.dropdown.Option(text=model))
        return options

    # ---------- Input Fields ----------
    model_i = ft.TextField(label="Model")
    apikey_i = ft.TextField(label="API Key", password=True, can_reveal_password=True)
    url_i = ft.TextField(label="URL")
    instruction_i = ft.TextField(label="Instruction", expand=True, multiline=True, min_lines=1, max_lines=8)

    user_input = ft.TextField(label="User Input", expand=True, multiline=True, min_lines=1, max_lines=3)

    chat_list = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )

    # ---------- Dropdowns ----------
    def change_model(e):
        nonlocal model, client, base_url, api_key, instruction
        if e.control.value == model:
            return
        model = e.control.value
        credential = get_credentials()
        if credential is None or model not in credential:
            add_message("system", "Please configure model credentials in settings first.")
            return
        base_url = credential[model]["base_url"]
        api_key = credential[model]["api_key"]
        instruction = credential[model]["instruction"]
        client = create_client(api_key, base_url)
        add_message("system", f"Successfully switched to model: {model}" if client else f"Failed to load model '{model}'. Please check your credentials in settings.")

    def edit_model_value(e):
        m = e.control.value
        credential = get_credentials()
        if credential is None or m not in credential:
            return
        model_i.value = m
        apikey_i.value = credential[m]["api_key"]
        url_i.value = credential[m]["base_url"]
        instruction_i.value = credential[m]["instruction"]
        page.update()

    def save_model_value(e):
        credentials = get_credentials()
        if model_i.value == "" or url_i.value == "" or apikey_i.value == "":
            return
        if credentials is None:
            credentials = {}
        credentials[model_i.value] = {
            "base_url": url_i.value,
            "api_key": apikey_i.value,
            "instruction": instruction_i.value
        }
        save_credentials(credentials)
        add_message("system", f"Credentials for model '{model_i.value}' saved successfully.")
        model_i.value = ""
        apikey_i.value = ""
        url_i.value = ""
        instruction_i.value = ""
        model_edit.options = get_options() if len(get_options()) > 0 else [ft.dropdown.Option(text="No models configured.")]
        model_select.options = get_options() if len(get_options()) > 0 else [ft.dropdown.Option(text="No models configured.")]
        page.update()

    def del_all_model(e):
        clear_credentials()
        model_i.value = url_i.value = apikey_i.value = instruction_i.value = ""
        model_edit.options = get_options() if len(get_options()) > 0 else [ft.dropdown.Option(text="No models configured.")]
        model_select.options = get_options() if len(get_options()) > 0 else [ft.dropdown.Option(text="No models configured.")]
        chat_history = []
        chat_list.controls.clear()
        add_message("system", "No saved model.")
        page.close(dlg_modal)
        page.update()


    dlg_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Please confirm"),
        content=ft.Text("Do you really want to delete models?"),
        actions=[
            ft.TextButton("Yes", on_click=del_all_model),
            ft.TextButton("No", on_click=lambda e: page.close(dlg_modal)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )


    model_select = ft.Dropdown(
        label="Select Model",
        options=get_options() if len(get_options()) > 0 else [ft.dropdown.Option(text="No models configured.")],
        on_change=change_model,
        width= 500,
    )

    model_edit = ft.Dropdown(
        label="Edit Model",
        options=get_options() if len(get_options()) > 0 else [ft.dropdown.Option(text="No models configured.")],
        on_change=edit_model_value,
        width = 500,
    )

    # ---------- Chat Functions ----------
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

        message_widget = ft.Container(
            content=ft.Column(
                tight=True,
                spacing=10,
                controls=[
                    ft.Row(expand=True, controls=[ft.Text(f"{sender.upper()} ({time_stamp})", color=color, size=12)]),
                    ft.Row(
                        expand=True,
                        controls=[
                            ft.Container(
                                expand=1,
                                bgcolor=bg_color,
                                padding=10,
                                content=ft.Markdown(
                                    message,
                                    selectable=True,
                                    code_theme=ft.MarkdownCodeTheme.NIGHT_OWL,
                                    extension_set=ft.MarkdownExtensionSet.GITHUB_WEB
                                )
                            )
                        ]
                    )
                ]
            )
        )
        chat_list.controls.append(message_widget)
        page.update()

    def send_clicked(e):
        nonlocal client, chat_history, model, instruction
        user_query = user_input.value
        if not user_query or instruction is None:
            return
        user_input.value = ""
        add_message("user", user_query)
        add_message("ai", "Thinking...")
        user_message = {"role": "user", "content": user_query}
        chat_history.append(user_message)
        ai_response = get_ai_response(client, model, chat_history, instruction)
        if ai_response is None:
            chat_list.controls.pop()
            add_message("system", "Error: Could not get response from AI. Please check your credentials and network connection.")
            page.update()
            return
        chat_history.append({"role": "assistant", "content": ai_response})
        chat_list.controls.pop()
        add_message("ai", ai_response)

    def clear_clicked(e):
        nonlocal chat_history, model
        chat_history = []
        chat_list.controls.clear()
        add_message("system", f"New chat started with AI model: {model}")
        page.update()

    # ---------- Screens ----------
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
            ft.Divider(),
            model_select,
            ft.Row(controls=[user_input, ft.IconButton(icon=ft.Icons.SEND,on_click=send_clicked)])
        ]
    )

    settings_screen = ft.ListView(expand = True, spacing = 10, auto_scroll = False,
        #horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            model_edit,
            model_i,
            apikey_i,
            url_i,
            instruction_i,
            ft.Divider(),
            ft.Row(
                width=page.width*0.8 if page.width else 200,
                controls=[
                ft.ElevatedButton("Save", on_click=save_model_value, expand=True),
                ft.ElevatedButton("Back", on_click=lambda _: page.go("/"), expand=True),
                ft.ElevatedButton("Delete", on_click=lambda _: page.open(dlg_modal), expand=True)
            ],alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    ])



    # ---------- Navigation ----------
    def route_change(route):
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [ft.Container(expand=True, content=chat_screen, padding=ft.Padding(0, 30, 0, 20))]
            )
        )
        if page.route == "/settings":
            page.views.append(
                ft.View(
                    "/settings",
                    [ft.Container(expand=True, content=settings_screen, padding=ft.Padding(0, 30, 0, 20))],
                )
            )
        page.update()

    credentials = get_credentials()
    if credentials is not None and len(credentials) > 0:
        model = list(credentials.keys())[0]
        base_url = credentials[model]["base_url"]
        api_key = credentials[model]["api_key"]
        instruction = credentials[model]["instruction"]
        client = create_client(api_key, base_url)
        add_message("system", f"Model '{model}' loaded successfully." if client else f"Failed to load model '{model}'. Please check your credentials.")
    else:
        add_message("system", "Welcome! Please go to settings to configure a model.")

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)   # type: ignore

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)


if __name__ == "__main__":
    ft.app(target=main)
