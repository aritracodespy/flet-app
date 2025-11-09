import flet as ft
from utils import get_notes, add_note, delete_note

def main(page: ft.Page):
    page.title = "SyncNotes"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    def save_key(e):
        apikey = e.control.value
        if apikey is None: return
        if apikey.strip() == "": return
        page.client_storage.set("SYNC-NOTE-API-KEY", apikey)
        page.open(ft.SnackBar(content=ft.Text(value="key saved!!")))
        render_ui()

    def load_key():
        return page.client_storage.get("SYNC-NOTE-API-KEY")



    def yes_delete(e):
        id = dlg_modal.data
        if not id: return
        key = load_key()
        if key is None: 
            page.open(ft.SnackBar(content=ft.Text(value="key is not set!")))
            return
        page.close(dlg_modal)
        r = delete_note(id=id, key=key)
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
        value=load_key(),
        on_submit=save_key,
        visible=False
    )
    note_i = ft.TextField(label="Your new note",expand=True, multiline=True,min_lines=1,max_lines=5)
    note_list = ft.ListView(expand=True,auto_scroll=True,spacing=10)

    def render_ui():
        apikey = load_key()
        if apikey is None:
            page.open(ft.SnackBar(content=ft.Text(value="key is not set!")))
            return
        notes = get_notes(key=apikey)
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
        key = key_i.value
        if message is None or key is None: return
        if message.strip() == "": return
        r = add_note(note=message,key=key)

        if "error" in r:
            page.open(ft.SnackBar(content=ft.Text(value=r.get("error", "Error!!"))))
        if r.get("success",False):
            page.open(ft.SnackBar(content=ft.Text(value=r.get("message","added"))))
            note_i.value = ""
            render_ui()
    def toggle_key(e):
        key_i.visible = not key_i.visible
        page.update()
    page.add(
        ft.Container(
            expand=True,
            padding=ft.Padding(0,20,0,10),
            content=ft.Column(
                [
                    ft.Row(controls=[
                        ft.Text("SyncNotes",size=30),
                        ft.IconButton(icon=ft.Icons.SETTINGS,on_click=toggle_key)
                    ],alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    key_i,
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
