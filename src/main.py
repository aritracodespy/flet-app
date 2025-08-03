import flet as ft
from openai import OpenAI
import json
import os
from datetime import datetime

class AITerminalChat:
    def __init__(self):
        self.client = None
        self.chat_history = []
        self.settings = {
            "base_url": "https://api.openai.com/v1",
            "api_key": "",
            "model": "gpt-3.5-turbo",
            "instruction": "You are a helpful assistant. Give accurate and concise answers. "
        }
        self.load_settings()

    def load_settings(self):
        """Load settings from file if exists"""
        try:
            if os.path.exists("chat_settings.json"):
                with open("chat_settings.json", "r") as f:
                    self.settings.update(json.load(f))
        except Exception as e:
            print(f"Error loading settings: {e}")

    def save_settings(self):
        """Save settings to file"""
        try:
            with open("chat_settings.json", "w") as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def create_ai(self, base_url, api_key):
        try:
            client = OpenAI(
                base_url=base_url,
                api_key=api_key
            )
            return client
        except Exception as e:
            print("Error creating client:", e)
            return None

    def get_ai_response(self, client, model, query, history=[], instruction="You are a helpful assistant."):
        try:
            message = [
                {"role": "system", "content": instruction},
            ]

            if len(history) > 0:
                filtered_history = history[-6:]
                message.extend(filtered_history)

            message.append({
                "role": "user", "content": query
            })

            response = client.chat.completions.create(
                model=model,
                messages=message
            )
            return response.choices[0].message
        except Exception as e:
            print("Error generating response:", e)
            return None

def main(page: ft.Page):
    page.title = "AI Terminal Chat"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0c0c0c"
    page.padding = 0

    # Initialize chat instance
    chat = AITerminalChat()

    # Chat display
    chat_display = ft.ListView(
        expand=True,
        spacing=5,
        padding=ft.padding.all(10),
        auto_scroll=True,
    )

    # Input field
    input_field = ft.TextField(
        hint_text="Type your message...",
        multiline=True,
        min_lines=1,
        max_lines=4,
        border_color="#00ff00",
        text_style=ft.TextStyle(color="#00ff00", font_family="Courier New"),
        bgcolor="#1a1a1a",
        expand=True,
    )

    # Status indicator
    status_text = ft.Text(
        "●",
        color="#ff0000",
        size=16,
        tooltip="Not connected"
    )

    base_url_field = ft.TextField(
        label="Base URL",
        value=chat.settings["base_url"],
        expand=True,
    )

    api_key_field = ft.TextField(
        label="API Key",
        value=chat.settings["api_key"],
        password=True,
        expand=True,
    )

    model_field = ft.TextField(
         label="Model",
         value=chat.settings["model"],
         expand=True,
    )

    instruction_field = ft.TextField(
        label="System Instruction",
        value=chat.settings["instruction"],
        multiline=True,
        min_lines=3,
        max_lines=5,
        expand=True,
    )


    def add_message(content, is_user=True, is_system=False):
        """Add message to chat display"""
        timestamp = datetime.now().strftime("%H:%M:%S")

        if is_system:
            color = "#ffaa00"
            prefix = "[SYSTEM]"
        elif is_user:
            color = "#00ff00"
            prefix = "[USER]"
        else:
            color = "#00aaff"
            prefix = "[AI]"

        message_container = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(f"{prefix} {timestamp}",
                           color=color,
                           size=12,
                           font_family="Courier New"),
                ]),
                ft.Row([
                    ft.Container(
                        content=ft.Markdown(
                            content,
                            code_theme=ft.MarkdownCodeTheme.TOMORROW_NIGHT,
                            selectable=True,
                            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                        ),
                        expand=True,
                        padding=ft.padding.all(5),
                    )
                ], expand=True),
            ], spacing=2, tight=True),
            margin=ft.margin.only(bottom=10),
        )

        chat_display.controls.append(message_container)
        page.update()

    def update_status():
        """Update connection status"""
        if chat.client and chat.settings["api_key"]:
            status_text.color = "#00ff00"
            status_text.tooltip = "Connected"
        else:
            status_text.color = "#ff0000"
            status_text.tooltip = "Not connected"
        page.update()

    def send_message(e):
        """Send message to AI"""
        message = input_field.value.strip()
        if not message:
            return

        # Clear input
        input_field.value = ""
        page.update()

        # Add user message
        add_message(message, is_user=True)

        # Check if client is available
        if not chat.client:
            add_message("Error: AI client not configured. Please check settings.", is_system=True)
            return

        # Get AI response
        try:
            add_message("Thinking...", is_system=True)

            response = chat.get_ai_response(
                chat.client,
                chat.settings["model"],
                message,
                chat.chat_history,
                chat.settings["instruction"]
            )

            # Remove "Thinking..." message
            chat_display.controls.pop()

            if response:
                # Add to history
                chat.chat_history.append({"role": "user", "content": message})
                chat.chat_history.append({"role": "assistant", "content": response.content})

                # Display response
                add_message(response.content, is_user=False)
            else:
                add_message("Error: Failed to get AI response", is_system=True)

        except Exception as ex:
            # Remove "Thinking..." message if exists
            if chat_display.controls and "Thinking..." in str(chat_display.controls[-1].content):
                chat_display.controls.pop()
            add_message(f"Error: {str(ex)}", is_system=True)

    def clear_chat(e):
        """Clear chat history"""
        chat_display.controls.clear()
        chat.chat_history.clear()
        add_message("Chat cleared", is_system=True)


    def save_settings(e):
        """Save settings and close dialog"""
        chat.settings["base_url"] = base_url_field.value
        chat.settings["api_key"] = api_key_field.value
        chat.settings["model"] = model_field.value
        chat.settings["instruction"] = instruction_field.value

        # Create new client
        if chat.settings["api_key"]:
            chat.client = chat.create_ai(
                chat.settings["base_url"],
                chat.settings["api_key"]
            )

        chat.save_settings()
        update_status()
        page.go("/")
        page.update()
        add_message("Settings updated", is_system=True)


    # Input handler
    def on_key_down(e: ft.KeyboardEvent):
        if e.key == "Enter" and not e.shift:
            send_message(e)

    input_field.on_submit = send_message
    page.on_keyboard_event = on_key_down

    # Header
    header = ft.Container(
        content=ft.Row([
            ft.Text(
                "AI Terminal Chat",
                size=22,
                weight=ft.FontWeight.BOLD,
                color="#00ff00",
                font_family="Courier New"
            ),
            ft.Row([
                status_text,
                ft.IconButton(
                    ft.Icons.SETTINGS,
                    icon_color="#00ff00",
                    tooltip="Settings",
                    icon_size=20,
                    on_click =lambda _: page.go("/settings"),
                ),
                ft.IconButton(
                    ft.Icons.CLEAR_ALL,
                    icon_color="#ff6666",
                    tooltip="Clear Chat",
                    on_click=clear_chat,
                    icon_size=20,
                ),
            ], spacing=5),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=ft.padding.all(15),
        bgcolor="#1a1a1a",
        border=ft.border.only(bottom=ft.BorderSide(1, "#333333")),
    )

    # Input area
    input_area = ft.Container(
        content=ft.Row([
            input_field,
            ft.IconButton(
                ft.Icons.SEND,
                icon_color="#00ff00",
                tooltip="Send (Enter)",
                on_click=send_message,
                icon_size=24,
            ),
        ], spacing=10),
        padding=ft.padding.all(15),
        bgcolor="#1a1a1a",
        border=ft.border.only(top=ft.BorderSide(1, "#333333")),
    )

    # Chat area
    chat_area = ft.Container(
        content=chat_display,
        expand=True,
        bgcolor="#0c0c0c",
    )

    # Main layout

    home_page = ft.Column([
        header,
        chat_area,
        input_area,
    ], spacing=5, expand=True)

    settings_page = ft.Column([
        base_url_field,
        api_key_field,
        model_field,
        instruction_field,
        ft.Row([
            ft.ElevatedButton("SAVE",on_click=save_settings),
            ft.ElevatedButton("CANCEL", on_click= lambda _: page.go("/"))
        ],alignment = ft.MainAxisAlignment.SPACE_EVENLY)
    ], spacing=15, expand=True)

    def route_change(route):
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [home_page],
            )
        )
        if page.route == "/settings":
            page.views.append(
                ft.View(
                    "/settings",
                    [settings_page]
                )
            )
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    # Initialize
    if chat.settings["api_key"]:
        chat.client = chat.create_ai(
            chat.settings["base_url"],
            chat.settings["api_key"]
        )
    update_status()
    add_message("Welcome to AI Terminal Chat! Configure your settings to get started.", is_system=True)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

if __name__ == "__main__":
    ft.app(target=main)
