import flet as ft
import requests

def get_notes(key, url):
    payload = {
        "command": "select * from mysyncnotes;"
    }
    try:
        r = requests.post(
            url=url,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": key
            },
            json=payload
        )
        r.raise_for_status()
        data = r.json()
        if data["success"] and data["data"] is not None:
            return data["data"]
        else:
            return None
    except:
        return None

def add_note(note, key, url):
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": key
    }

    payload = {
        "command":"INSERT INTO mysyncnotes (note) VALUES (?)",
        "params":[note]
    }

    try:
        r = requests.post(url=url, headers=headers, json=payload)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}
    
def delete_note(id, key, url):
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": key
    }

    payload = {
        "command":"DELETE FROM mysyncnotes WHERE id = ?",
        "params":[int(id)]
    }

    try:
        r = requests.post(url=url, headers=headers, json=payload)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def main(page: ft.Page):
    page.title = "SyncNotes"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    def save_cred(e):
        apikey = key_i.value
        url = url_i.value
        if apikey is None or url is None: return
        if apikey.strip() == "" or url.strip() == "": return
        page.client_storage.set("SYNC-NOTE-CRED", {"api-key": apikey, "url": url})
        settings.visible=False
        page.open(ft.SnackBar(content=ft.Text(value="key saved!!")))
        render_ui()

    def load_cred():
        cred = page.client_storage.get("SYNC-NOTE-CRED")
        if cred is not None:
            return cred
        else:
            return {"api-key": "", "url": ""}



    def yes_delete(e):
        id = dlg_modal.data
        if not id: return
        cred = load_cred()
        if cred.get("api-key", "") == "" or cred.get("url", "") == "":
            page.open(ft.SnackBar(content=ft.Text(value="Creadentials is not set yet!")))
            return
        page.close(dlg_modal)
        r = delete_note(id=id, key=cred["api-key"], url=cred["url"])
        if "error" in r:
            page.open(ft.SnackBar(content=ft.Text(value=r.get("error", "Error!!"))))
        if r.get("success",False):
            page.open(ft.SnackBar(content=ft.Text(value=r.get("message","deleted"))))
            render_ui()


    dlg_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("Please confirm"),
        content=ft.Text("Do you really want to delete this note?"),
        actions=[
            ft.TextButton("Yes", on_click=yes_delete),
            ft.TextButton("No", on_click=lambda _: page.close(dlg_modal)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def open_dlg(note_id):
        dlg_modal.data = note_id
        page.open(dlg_modal)
        

    key_i = ft.TextField(
        label="secret key",
        expand=False,
        multiline=False,
        password=True,
        can_reveal_password=True,
        value=load_cred()["api-key"]
    )
    url_i = ft.TextField(
        label="url",
        multiline=False,
        value=load_cred()["url"]
    )

    settings = ft.Column(controls=[
        key_i, 
        url_i,
        ft.ElevatedButton(
            text="SAVE", 
            on_click=save_cred,
            width=500,
            bgcolor=ft.Colors.BLUE_500,
            color=ft.Colors.BLACK
        ),
        ft.Divider(thickness=3)
    ],visible=False)

    note_i = ft.TextField(label="Your new note",expand=True, multiline=True,min_lines=1,max_lines=5)
    note_list = ft.ListView(expand=True,auto_scroll=True,spacing=10)

    def render_ui():
        cred = load_cred()
        if cred.get("api-key", "") == "" or cred.get("url", "") == "":
            page.open(ft.SnackBar(content=ft.Text(value="Creadentials is not set yet!")))
            return
        notes = get_notes(key=cred["api-key"],url=cred["url"])
        if notes is None:
            page.open(ft.SnackBar(content=ft.Text(value="Error")))
            return
        note_list.controls.clear()
        if len(notes) == 0:
            note_list.controls.append(ft.Text(value="No saved notes"))
        for note in reversed(notes): # type: ignore
            content = ft.Card(
                content=ft.Container(
                    padding=10,
                    content=ft.Row(
                        controls=[
                            ft.Text(note["note"], expand=True,selectable=True),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                on_click=lambda e, id=note["id"]: open_dlg(note_id=id),
                            ),
                        ]
                    )
                )
            )
            note_list.controls.append(content)
        page.update()

    def send(e):
        message = note_i.value
        cred = load_cred()
        if cred.get("api-key", "") == "" or cred.get("url", "") == "" or message is None:
            return
        if message.strip() == "": return
        r = add_note(note=message,key=cred["api-key"], url=cred["url"])

        if "error" in r:
            page.open(ft.SnackBar(content=ft.Text(value=r.get("error", "Error!!"))))
        if r.get("success",False):
            page.open(ft.SnackBar(content=ft.Text(value=r.get("message","added"))))
            note_i.value = ""
            render_ui()
    def toggle_settings(e):
        settings.visible = not settings.visible
        page.update()
    page.add(
        ft.Container(
            expand=True,
            padding=ft.Padding(0,20,0,10),
            content=ft.Column(
                [
                    ft.Row(controls=[
                        ft.Text("SyncNotes",size=30),
                        ft.IconButton(icon=ft.Icons.SETTINGS,on_click=toggle_settings)
                    ],alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(thickness=3),
                    settings,
                    note_list,
                    ft.Row(
                        [
                            note_i,
                            ft.IconButton(icon=ft.Icons.NOTE_ADD_OUTLINED, on_click=send, tooltip="Add Note"),
                        ],
                    ),
                ],
                expand=True,
            ),
        )
    )

    render_ui()
ft.app(target=main)
