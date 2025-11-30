import flet as ft
import requests
import time
import base64

def encode(original_string):
    try:
        string_bytes = original_string.encode('utf-8')
        encoded_bytes = base64.b64encode(string_bytes)
        encoded_string = encoded_bytes.decode('utf-8')
        return encoded_string
    except:
        return original_string

def decode(base64_string):
    try:
        base64_bytes = base64_string.encode('utf-8')
        decoded_bytes = base64.b64decode(base64_bytes)
        decoded_string = decoded_bytes.decode('utf-8')
        return decoded_string
    except:
        return base64_string

def _update_note_content(base_url, key, text):
    url = base_url + "/db/my_notepad_app_content/1"
    headers = {"Content-Type": "application/json", "Authorization": key}
    note = encode(text)

    try:
        r = requests.put(
            url = url,
            headers = headers,
            json = {"note-content": note}
        )
        r.raise_for_status()
        return r.json()
    except:
        return None


def _load_note_content(base_url, key):
    url = base_url + "/db/my_notepad_app_content/1"
    headers = {"Content-Type": "application/json", "Authorization": key}
    try:
        r = requests.get(url=url, headers=headers)
        r.raise_for_status()
        d = r.json()
        if d.get("ok",False):
            return decode(d["result"]["note-content"])
        else:
            return None
    except:
        return None


def main(page: ft.Page):
    page.title = "My Notepad"
    page.scroll = ft.ScrollMode.AUTO
    page.padding = ft.Padding(5, 50, 5, 10)

    def load_cred():
        s = page.client_storage.get("SYNC-NOTE-CRED")
        return s if s else {"api-key": "", "url": ""}

    creds = load_cred()

    key_i = ft.TextField(
        label="Secret Key",
        password=True,
        can_reveal_password=True,
        value=creds["api-key"],
    )

    url_i = ft.TextField(
        label="Backend URL",
        value=creds["url"],
    )

    settings = ft.Column(visible=False)

    def save_cred(e):
        apikey = key_i.value
        url = url_i.value

        if not apikey or not url:
            return

        page.client_storage.set(
            "SYNC-NOTE-CRED",
            {"api-key": apikey.strip(), "url": url.strip()},
        )

        settings.visible = False
        page.open(ft.SnackBar(content=ft.Text("Credentials Saved!")))
        page.update()
        _read()

    save_btn = ft.ElevatedButton(
        text="SAVE",
        width=500,
        bgcolor=ft.Colors.BLUE_500,
        color=ft.Colors.WHITE,
        on_click=save_cred,
    )

    settings.controls = [key_i, url_i, save_btn, ft.Divider(thickness=3)]

    main_textfield = ft.TextField(
        multiline=True,
        border=ft.InputBorder.NONE,
        hint_text="Your thoughts...",
    )

    def _read():
        creds = load_cred()
        base_url = creds["url"]
        key = creds["api-key"]

        if not base_url or not key:
            return

        main_textfield.value = "Lodding..."
        page.update()
        data = _load_note_content(base_url, key)

        if data is None:
            main_textfield.value = ""
            page.update()
            page.open(ft.SnackBar(content=ft.Text("Can't load notes")))
            return

        main_textfield.value = data
        page.update()

    def toggle_settings(e):
        settings.visible = not settings.visible
        page.update()

    def _save(e = None):
        text = main_textfield.value
        if not text:
            return

        creds = load_cred()
        base_url = creds["url"]
        key = creds["api-key"]

        if not base_url or not key:
            page.open(ft.SnackBar(content=ft.Text("Credentials not saved!")))
            return

        data = _update_note_content(base_url, key, text.strip())

        if data is None:
            page.open(ft.SnackBar(content=ft.Text("Can't save notes")))
            return

        if data.get("ok", False):
            page.open(ft.SnackBar(content=ft.Text("Notes Saved!")))
        else:
            page.open(ft.SnackBar(content=ft.Text(str(data.get("error")))))


    page.floating_action_button = ft.FloatingActionButton(
        content=ft.PopupMenuButton(
            items=[
                ft.PopupMenuItem(icon=ft.Icons.SAVE, text="Save", on_click=_save),
                ft.PopupMenuItem(icon=ft.Icons.SETTINGS, text="Settings", on_click=toggle_settings),
            ]
        ),
        bgcolor=ft.Colors.TRANSPARENT
    )

    page.add(
        ft.Container(
            expand=True,
            margin=ft.Margin(5,10,5,0), 
            padding=ft.Padding(0,10,0,10),
            content=ft.Column(
                expand=True, spacing=10,
                controls=[settings, main_textfield],
            )
        )
    )

    if not creds["url"] or not creds["api-key"]:
        settings.visible = True
        page.update()
    else:
        _read()

    def auto_save():
        time.sleep(90)
        _save()

    page.run_thread(auto_save)

ft.app(target=main)
