from datetime import datetime
import flet as ft

class HistoryItem(ft.Container):
    def __init__(self, index, expression, result, on_delete, page: ft.Page):
        super().__init__()
        self.padding = 10
        self.margin = 5
        self.bgcolor = ft.Colors.WHITE10
        self.border_radius = 8
        self.expression = expression
        self.result_val = result 
        
        self.content = ft.Column([
            ft.Row([
                ft.Text(f"#{index} - {datetime.now().strftime('%H:%M:%S')}", size=10, color=ft.Colors.BLUE_200),
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.COPY, 
                        icon_size=16, 
                        on_click=lambda _: page.set_clipboard(self.result_val) 
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE, 
                        icon_size=16, 
                        on_click=lambda _: on_delete(self)
                    ),
                ], spacing=0)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Text(self.expression, size=12, color=ft.Colors.WHITE54),
            ft.Text(self.result_val, size=18, weight="bold"),
        ], spacing=2)