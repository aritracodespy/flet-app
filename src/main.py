

from google import genai
from google.genai import types
import flet as ft
from functionsTools import (
    get_current_time,
    get_current_date,
    get_current_weather,
    send_message_to_user,
    search_the_internet,
    get_latest_news,
    get_wikipedia_summary,
    convert_currency,
    create_or_update_event,
    list_events,
    get_stock_data
)

tools = [
    get_current_time,
    get_current_date,
    get_current_weather,
    send_message_to_user,
    search_the_internet,
    get_latest_news,
    get_wikipedia_summary,
    convert_currency,
    create_or_update_event,
    list_events,
    get_stock_data
]

system_instruction = """
🛠️ Always take a tool-first approach:
- Think clearly about the task at hand.
- Identify which tool(s) you need to use.
- Ask for or confirm any required arguments before using a tool.
- Use the "Search the Internet" tool to retrieve up-to-date or real-time information.
-Upon starting a conversation greet the user and intrroduce yourself with the information about what can you do.
"""

def create_new_chat(apikey:str, model:str, instruction:str):
    try:
        client = genai.Client(api_key=apikey)
        chat = client.chats.create(
            model=model,
            config=types.GenerateContentConfig(
                temperature=1,
                system_instruction=instruction + system_instruction,
                tools = tools
            )
        )
        return chat
    except:
        return None

def get_ai_responce(chat, message:str):
    try:
        reaponce = chat.send_message(
            message=message
        )
        return reaponce.text
    except:
        return None


def main(page: ft.Page):
    page.title = "GenAi"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 20

    chat = None



    def get_saved_settings():
        try:
            api_key = page.client_storage.get("api_key")
            instruction = page.client_storage.get("instruction")
            model = page.client_storage.get("model")
            return api_key, instruction, model
        except:
            return None, None, None

    def save_settings(api_key, instruction, model):
        try:
            page.client_storage.set("api_key", api_key)
            page.client_storage.set("instruction", instruction)
            page.client_storage.set("model", model)
        except:
            page.open(ft.SnackBar(content=ft.Text("Error saving settings")))
            page.update()


    def update_settings(e):
        nonlocal chat
        api_key = api_key_input.value
        instruction = instruction_input.value
        model = model_input.value
        if api_key is None or instruction is None or model is None:
            return
        save_settings(api_key, instruction, model)
        page.update()
        chat = create_new_chat(api_key, model, instruction)
        chat_list.controls.clear()
        update_chat("system", f"GenAi Active! Model: {model}")
        page.open(ft.SnackBar(content=ft.Text("Settings Updated",color=ft.Colors.GREEN),show_close_icon=True))
        page.update()



    def update_chat(role, message):
        if message == "":
            return

        is_user = role == "user"
        is_ai = role == "ai"

        # Message container styling
        message_container = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        controls=[
                            ft.Text(
                                role.capitalize(),
                                weight=ft.FontWeight.BOLD,
                                size=11,
                                opacity=0.8,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Markdown(
                        message,
                        code_theme=ft.MarkdownCodeTheme.TOMORROW_NIGHT,
                        selectable=True,
                        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                    ),
                ],
                spacing=4,
                tight=True,
            ),
            padding=ft.padding.symmetric(vertical=8, horizontal=12),
            border_radius=ft.border_radius.all(10),
        )

        # Set background color and alignment
        if is_user:
            message_container.bgcolor = ft.Colors.BLUE_GREY_800
            alignment = ft.alignment.center_right
        elif is_ai:
            message_container.bgcolor = ft.Colors.with_opacity(0.15, ft.Colors.WHITE)
            alignment = ft.alignment.center_left
        else:  # System message
            message_container.bgcolor = ft.Colors.with_opacity(0.05, ft.Colors.BLUE_100)
            alignment = ft.alignment.center

        # Add the message to the chat list in a Container for alignment
        chat_list.controls.append(
            ft.Container(
                content=message_container,
                alignment=alignment,
            )
        )
        page.update()

    def send_message(e):
        nonlocal chat
        if chat is None:
            return
        message = user_input.value
        if message is None or message == "":
            return
        user_input.value = ""
        update_chat("user", message)

        # Disable input and show thinking animation
        user_input.disabled = True
        send_button.disabled = True
        thinking_control = ft.Container(
            content=ft.ProgressRing(width=20, height=20, stroke_width=2),
            alignment=ft.alignment.center_left,
            padding=ft.padding.symmetric(vertical=10, horizontal=12),
        )
        chat_list.controls.append(thinking_control)
        page.update()

        # Get AI response
        responce = get_ai_responce(chat, message)

        # Remove thinking animation and re-enable input
        chat_list.controls.pop()
        user_input.disabled = False
        send_button.disabled = False

        if responce is not None:
            update_chat("ai", responce)
        else:
            update_chat("system", "Error getting response")
            page.update()


    chat_list = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True
    )
    chat_container = ft.Container(
        content=chat_list,
        expand=True,
        border=ft.border.all(1, ft.Colors.OUTLINE),
        border_radius=ft.border_radius.all(10),
        padding=ft.padding.all(10)
    )

    user_input = ft.TextField(
        hint_text="Ask me anything...",
        expand=True,
        border_radius=ft.border_radius.all(10),
        filled=True
    )
    send_button = ft.IconButton(
        icon=ft.Icons.SEND,
        icon_color=ft.Colors.GREEN_400,
        tooltip="Send message",
        on_click=send_message
    )

    api_key_input = ft.TextField(
        hint_text="Api key",
        password=True,
        border_radius=ft.border_radius.all(10),
        filled=True
    )
    instruction_input = ft.TextField(
        hint_text="Instruction",
        border_radius=ft.border_radius.all(10),
        multiline=True,
        min_lines=3,
        max_lines=6,
        filled=True
    )
    model_input = ft.TextField(
        hint_text="Model",
        border_radius=ft.border_radius.all(10),
        filled=True
    )
    save_button = ft.ElevatedButton(text="Save Settings", on_click=update_settings)


    input_row = ft.Row(
        controls=[
            user_input,
            send_button
        ],
        alignment=ft.MainAxisAlignment.START
    )

    chat_view = ft.Tab(
        text="Chat",
        icon=ft.Icons.CHAT_BUBBLE_OUTLINE,
        content=ft.Container(
            content=ft.Column(
                controls=[
                    chat_container,
                    input_row
                ],
                expand=True
            ),
            padding=ft.Padding(10,10,10,10),
            expand=True,
        )
    )
    setting_view = ft.Tab(
        text="Settings",
        icon=ft.Icons.SETTINGS_OUTLINED,
        content=ft.Container(
            content=ft.Column(
                controls=[
                    api_key_input,
                    instruction_input,
                    model_input,
                    save_button,
                ],
                spacing=15,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
            padding=ft.padding.symmetric(horizontal=40),
        ),
    )

    apikey, instruction, model = get_saved_settings()
    if apikey is not None and instruction is not None and model is not None:
        api_key_input.value = apikey
        instruction_input.value = instruction
        model_input.value = model
        page.update()
        chat = create_new_chat(apikey, model, instruction)
        chat_list.controls.clear()
        update_chat("system", f"Agent is Active! Model: {model}")
        page.update()
    

    page.add(
        ft.Container(
            content=ft.Tabs(
                selected_index=0,
                animation_duration=300,
                tabs=[chat_view, setting_view],
                expand=True
            ),
            expand=True,
        )
    )

if __name__ == "__main__":
    ft.app(target=main)
