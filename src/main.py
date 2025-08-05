
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
def get_ai_response(client, model, chat_messages, instruction = ""):
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

    except Exception as e:
        return None


def main(page: ft.Page):
    page.title = "ai bot"
    page.vertical_alignment = ft.MainAxisAlignment.END
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = ft.Padding(10, 20, 10, 10)


    primary_llm = True
    client = None
    chat_history = []
    base_url = "https://api.openai.com/v1"
    api_key = ""
    model = "gpt-3.5-turbo"
    instruction = ""



    def get_cridentials():
        cridentials = page.client_storage.get("cridentials")
        if cridentials and "primary_llm" in cridentials and "secondary_llm" in cridentials:
            return [
                (
                    cridentials["primary_llm"]["base_url"], 
                    cridentials["primary_llm"]["api_key"], 
                    cridentials["primary_llm"]["model"], 
                    cridentials["primary_llm"]["instruction"]
                ),
                (
                    cridentials["secondary_llm"]["base_url"], 
                    cridentials["secondary_llm"]["api_key"], 
                    cridentials["secondary_llm"]["model"], 
                    cridentials["secondary_llm"]["instruction"]
                )
            ]
        return None

    def save_cridentials(base_url_1, api_key_1, model_1, instruction_1, base_url_2, api_key_2, model_2, instruction_2):
        cridentials = {
            "primary_llm" : {
                "base_url": base_url_1,
                "api_key": api_key_1,
                "model": model_1,
                "instruction": instruction_1
            },
            "secondary_llm" : {
                "base_url": base_url_2,
                "api_key": api_key_2,
                "model": model_2,
                "instruction": instruction_2
            },
        }
        page.client_storage.set("cridentials", cridentials)

    def get_notes():
        notes = page.client_storage.get("notes")
        if notes:
            return notes
        return ""

    def save_notes(notes):
        page.client_storage.set("notes", notes)


    base_url_input_1 = ft.TextField(label="Base URL", value=base_url)
    api_key_input_1 = ft.TextField(label="API Key", password=True, can_reveal_password=True, value=api_key)
    model_input_1 = ft.TextField(label="Model", value=model)
    instruction_input_1 = ft.TextField(label="Instruction",value=instruction,expand=True,multiline=True,min_lines=1,max_lines=5)

    base_url_input_2 = ft.TextField(label="Base URL", value=base_url)
    api_key_input_2 = ft.TextField(label="API Key", password=True, can_reveal_password=True, value=api_key)
    model_input_2 = ft.TextField(label="Model", value=model)
    instruction_input_2 = ft.TextField(label="Instruction",value=instruction,expand=True,multiline=True,min_lines=1,max_lines=5)


    user_input = ft.TextField(label="User Input",expand=True,multiline=True,min_lines=1,max_lines=3)

    chat_list = ft.ListView(
        expand=1,
        spacing=10,
        auto_scroll=True,
    )

    notes_input = ft.TextField(
        value = get_notes(),
        expand =True,
        border=ft.InputBorder.NONE,
        multiline = True,
        min_lines = 20,)

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


    def change_llm_clicked(e):
        nonlocal primary_llm, client, base_url, api_key, model, instruction
        primary_llm = llm_select.value
        cridentials = get_cridentials()
        if cridentials is None:
            add_message("system", "Setup Cridentials first")
            return
        
        if primary_llm:
            base_url, api_key, model, instruction = cridentials[0]
            client = create_client(api_key, base_url)
            add_message("system", f"Using Primary LLM {model}" if client is not None else "Invalid Cridentials for Primary LLM")
        else:
            base_url, api_key, model, instruction = cridentials[1]
            client = create_client(api_key, base_url)
            add_message("system", f"Using Secondary LLM {model}" if client is not None else "Invalid Cridentials for Secondary LLM")
        


    def save_clicked(e):
        nonlocal client, chat_history, base_url, api_key, model, instruction

        base_url_1 = base_url_input_1.value
        api_key_1 = api_key_input_1.value
        model_1 = model_input_1.value
        instruction_1 = instruction_input_1.value

        base_url_2 = base_url_input_2.value
        api_key_2 = api_key_input_2.value
        model_2 = model_input_2.value
        instruction_2 = instruction_input_2.value

        save_cridentials(base_url_1, api_key_1, model_1, instruction_1, base_url_2, api_key_2, model_2, instruction_2)
        chat_history = []
        if primary_llm:
            base_url = base_url_1
            api_key = api_key_1
            model = model_1
            instruction = instruction_1
            client = create_client(api_key, base_url)
            if client is not None:
                chat_list.controls.clear()
                add_message("system",f"Primary model: {model}")
            else:
                add_message("system", "Invalid Cridentials for Primary LLM")
        else:
            base_url = base_url_2
            api_key = api_key_2
            model = model_2
            instruction = instruction_2
            client = create_client(api_key, base_url)
            if client is not None:
                chat_list.controls.clear()
                add_message("system",f"Secondary model: {model}")
            else:
                add_message("system", "Invalid Cridentials for Secondary LLM")
        page.go("/")
        

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
            add_message("system", "Invalid Cridentials")
        chat_history.append({"role": "assistant", "content": ai_response})
        chat_list.controls.pop()
        add_message("ai", ai_response)
        



    def clear_clicked(e):
        nonlocal chat_history, model
        chat_history = []
        chat_list.controls.clear()
        add_message("system", f"New Chat started, Ai model: {model}")
        page.update()

    def save_notes_clicked(e):
        notes = notes_input.value
        save_notes(notes)
        add_message("system", "Notes saved")

    llm_select = ft.Checkbox(label="Use Primary LLM", value=primary_llm, on_change=change_llm_clicked)

    chat_screen = ft.Column(
        expand=True,
        spacing=10,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Row([
                ft.Text("OpenAI BOT", size=20,color=ft.Colors.GREEN),
                ft.Row(controls=[
                    ft.IconButton(icon=ft.Icons.SETTINGS, on_click=lambda e: page.go("/settings")),
                    ft.IconButton(icon=ft.Icons.EVENT_NOTE, on_click=lambda e: page.go("/notes")),
                    ft.IconButton(icon=ft.Icons.CLEAR,on_click=clear_clicked)],alignment=ft.MainAxisAlignment.SPACE_AROUND)
            ],alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(),
            ft.Container(expand=True,padding=ft.Padding(0,10,0,10), content=chat_list),
            ft.Divider(),
            llm_select,
            ft.Row(controls=[user_input, ft.IconButton(icon=ft.Icons.SEND,on_click=send_clicked)])
        ]
    )

    settings_screen = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Text("Primary llm"),
            base_url_input_1,
            api_key_input_1,
            model_input_1,
            instruction_input_1,
            ft.Divider(),
            ft.Text("Secondary llm"),
            base_url_input_2,
            api_key_input_2,
            model_input_2,
            instruction_input_2,
            ft.Divider(),
            ft.Row(
                width=page.width*0.8 if page.width else 200,
                controls=[
                ft.ElevatedButton("Save", on_click=save_clicked, expand=True),
                ft.ElevatedButton("Back", on_click=lambda _: page.go("/"), expand=True),
            ],alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    ])

    notes_screen = ft.Column(
        horizontal_alignment = ft.CrossAxisAlignment.CENTER,
        controls = [
            ft.Text("Notes"),
            ft.Divider(),
            notes_input,
            ft.Divider(),
            ft.Row(
                width=page.width*0.8 if page.width else 200,
                controls=[
                    ft.ElevatedButton("Save", expand=True, on_click=save_notes_clicked),
                    ft.ElevatedButton("Back", expand=True, on_click=lambda _:page.go("/")),
                ],alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
        ]
    )

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
        if page.route == "/notes":
            page.views.append(
                ft.View(
                    "/notes",
                    [ft.Container(expand=True,content=notes_screen,padding=ft.Padding(0,30,0,20))],
                )
            )
        page.update()


    cridentials = get_cridentials()
    if cridentials is not None:
        if primary_llm:
            base_url, api_key, model, instruction = cridentials[0]
            client = create_client(api_key, base_url)
            add_message("system", f"Primary model: {model}" if client is not None else "Invalid Cridentials for Primary LLM")
        else:
            base_url, api_key, model, instruction = cridentials[1]
            client = create_client(api_key, base_url)
            add_message("system", f"Secondary model: {model}" if client is not None else "Invalid Cridentials for Secondary LLM")
        base_url_input_1.value, api_key_input_1.value, model_input_1.value, instruction_input_1.value = cridentials[0]
        base_url_input_2.value, api_key_input_2.value, model_input_2.value, instruction_input_2.value = cridentials[1]

    else:
        add_message("system", "Setup Cridentials first")


    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)  # type: ignore

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

if __name__ == "__main__":
    ft.app(target=main)
