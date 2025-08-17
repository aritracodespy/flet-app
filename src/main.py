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


def stream_ai_response(page, chat_list, client, model, chat_messages, instruction=""):
    try:
        messages = [{"role": "system", "content": instruction}]
        messages.extend(chat_messages[-10:])

        response_stream = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
        )

        # Create placeholder message in UI
        time_stamp = datetime.now().strftime("%H:%M:%S")
        ai_text = ft.Markdown(
            "", 
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            code_theme=ft.MarkdownCodeTheme.NIGHT_OWL,
        )
        ai_message_widget = ft.Container(
            content=ft.Column(
                tight=True,
                spacing=10,
                controls=[
                    ft.Row(expand=True, controls=[ft.Text(f"AI ({time_stamp})", color=ft.Colors.GREEN_300, size=12)]),
                    ft.Row(
                        expand=True,
                        controls=[
                            ft.Container(
                                expand=1,
                                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLUE_300),
                                padding=10,
                                content=ai_text
                            )
                        ]
                    )
                ]
            )
        )
        chat_list.controls.append(ai_message_widget)
        page.update()

        final_text = ""
        for event in response_stream:
            delta = event.choices[0].delta.content if event.choices[0].delta else ""
            if delta:
                final_text += delta
                ai_text.value = final_text
                page.update()

        return final_text

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

    def get_options():
        credentials = get_credentials()
        options = []
        if credentials is None:
            return options
        bots = list(credentials.keys())
        for b in bots:
            options.append(ft.dropdown.Option(text=b))
        return options

    # ---------- Input Fields ----------
    bot_name_i = ft.TextField(label="Bot Name")
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
        bot_name = e.control.value
        credential = get_credentials()
        if credential is None or bot_name not in credential:
            add_message("system", "Please configure bot credentials in settings first.")
            return
        bot_data = credential[bot_name]
        model = bot_data["model"]
        base_url = bot_data["base_url"]
        api_key = bot_data["api_key"]
        instruction = bot_data["instruction"]
        client = create_client(api_key, base_url)
        add_message("system", f"Switched to bot: {bot_name} (Model: {model})" if client else f"Failed to load bot '{bot_name}'. Please check credentials.")

    def edit_model_value(e):
        b = e.control.value
        credential = get_credentials()
        if credential is None or b not in credential:
            return
        bot_name_i.value = b
        model_i.value = credential[b]["model"]
        apikey_i.value = credential[b]["api_key"]
        url_i.value = credential[b]["base_url"]
        instruction_i.value = credential[b]["instruction"]
        page.update()

    def save_model_value(e):
        credentials = get_credentials()
        if bot_name_i.value == "" or model_i.value == "" or url_i.value == "" or apikey_i.value == "":
            return
        if credentials is None:
            credentials = {}
        credentials[bot_name_i.value] = {
            "model": model_i.value,
            "base_url": url_i.value,
            "api_key": apikey_i.value,
            "instruction": instruction_i.value
        }
        save_credentials(credentials)
        add_message("system", f"Bot '{bot_name_i.value}' saved successfully.")
        bot_name_i.value = ""
        model_i.value = ""
        apikey_i.value = ""
        url_i.value = ""
        instruction_i.value = ""
        model_edit.options = get_options() if len(get_options()) > 0 else [ft.dropdown.Option(text="No bots configured.")]
        model_select.options = get_options() if len(get_options()) > 0 else [ft.dropdown.Option(text="No bots configured.")]
        page.update()

    def del_selected_bot(e):
        credentials = get_credentials()
        if credentials is None:
            return
        bot_name = model_edit.value
        if bot_name is None or bot_name not in credentials:
            add_message("system", "No bot selected to delete.")
            page.close(dlg_modal)
            return
        del credentials[bot_name]
        save_credentials(credentials)
        add_message("system", f"Bot '{bot_name}' deleted successfully.")
        bot_name_i.value = model_i.value = url_i.value = apikey_i.value = instruction_i.value = ""
        model_edit.options = get_options() if len(get_options()) > 0 else [ft.dropdown.Option(text="No bots configured.")]
        model_select.options = get_options() if len(get_options()) > 0 else [ft.dropdown.Option(text="No bots configured.")]
        page.close(dlg_modal)
        page.update()

    dlg_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Please confirm"),
        content=ft.Text("Do you really want to delete the selected bot?"),
        actions=[
            ft.TextButton("Yes", on_click=del_selected_bot),
            ft.TextButton("No", on_click=lambda e: page.close(dlg_modal)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    model_select = ft.Dropdown(
        label="Select Bot",
        options=get_options() if len(get_options()) > 0 else [ft.dropdown.Option(text="No bots configured.")],
        on_change=change_model,
        width=500,
    )

    model_edit = ft.Dropdown(
        label="Edit Bot",
        options=get_options() if len(get_options()) > 0 else [ft.dropdown.Option(text="No bots configured.")],
        on_change=edit_model_value,
        width=500,
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
        user_message = {"role": "user", "content": user_query}
        chat_history.append(user_message)

        # Stream AI response
        ai_response = stream_ai_response(page, chat_list, client, model, chat_history, instruction)
        if ai_response is None:
            add_message("system", "Error: Could not stream response from AI.")
            return

        chat_history.append({"role": "assistant", "content": ai_response})

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
                ft.Text("OpenAI BOT", size=20, color=ft.Colors.GREEN),
                ft.Row(controls=[
                    ft.IconButton(icon=ft.Icons.SETTINGS, on_click=lambda e: page.go("/settings")),
                    ft.IconButton(icon=ft.Icons.CLEAR, on_click=clear_clicked)], alignment=ft.MainAxisAlignment.SPACE_AROUND)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(),
            ft.Container(expand=True, padding=ft.Padding(0, 10, 0, 10), content=chat_list),
            ft.Divider(),
            model_select,
            ft.Row(controls=[user_input, ft.IconButton(icon=ft.Icons.SEND, on_click=send_clicked)])
        ]
    )

    settings_screen = ft.ListView(
        expand=True, spacing=10, auto_scroll=False,
        controls=[
            model_edit,
            bot_name_i,
            model_i,
            apikey_i,
            url_i,
            instruction_i,
            ft.Divider(),
            ft.Row(
                width=page.width * 0.8 if page.width else 200,
                controls=[
                    ft.ElevatedButton("Save", on_click=save_model_value, expand=True),
                    ft.ElevatedButton("Back", on_click=lambda _: page.go("/"), expand=True),
                    ft.ElevatedButton("Delete", on_click=lambda _: page.open(dlg_modal), expand=True)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
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
        first_bot = list(credentials.keys())[0]
        bot_data = credentials[first_bot]
        model = bot_data["model"]
        base_url = bot_data["base_url"]
        api_key = bot_data["api_key"]
        instruction = bot_data["instruction"]
        client = create_client(api_key, base_url)
        add_message("system", f"Bot '{first_bot}' loaded successfully. (Model: {model})" if client else f"Failed to load bot '{first_bot}'. Please check your credentials.")
    else:
        add_message("system", "Welcome! Please go to settings to configure a bot.")

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)   # type: ignore

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)


if __name__ == "__main__":
    ft.app(target=main)
