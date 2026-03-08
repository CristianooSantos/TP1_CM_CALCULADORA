from dataclasses import field
import flet as ft
import sympy
import re
from datetime import datetime


@ft.control
class CalcButton(ft.Button):
    expand: int = field(default_factory=lambda: 1)

@ft.control
class DigitButton(CalcButton):
    bgcolor: ft.Colors = ft.Colors.WHITE_24
    color: ft.Colors = ft.Colors.WHITE

@ft.control
class ActionButton(CalcButton):
    bgcolor: ft.Colors = ft.Colors.ORANGE
    color: ft.Colors = ft.Colors.WHITE

@ft.control
class ExtraActionButton(CalcButton):
    bgcolor: ft.Colors = ft.Colors.BLUE_GREY_100
    color: ft.Colors = ft.Colors.BLACK

class HistoryItem(ft.Container):
    def __init__(self, index, expression, result, on_delete):
        super().__init__()
        self.padding = 10
        self.margin = 5
        self.bgcolor = ft.Colors.WHITE10
        self.border_radius = 8
        self.expression = expression
        self.result_val = result

        def copy_to_clipboard(e):
            try:
                e.page.set_clipboard(str(self.result_val))
                print(f"Copiado: {self.result_val}")
            except Exception as err:
                print(f"Erro ao copiar: {err}")

        self.content = ft.Column([
            ft.Row([
                ft.Text(f"#{index} - {datetime.now().strftime('%H:%M:%S')}", size=10, color=ft.Colors.BLUE_200),
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.COPY, 
                        icon_size=16, 
                        on_click=copy_to_clipboard 
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

@ft.control
class CalculatorApp(ft.Container):
    def init(self):
        self.reset()
        self.width = 400
        self.bgcolor = ft.Colors.BLACK
        self.border_radius = ft.BorderRadius.all(20)
        self.padding = 20
        
        self.history_index = 0
        self.is_continuation = False 

        self.expression_txt = ft.Text(value="", color=ft.Colors.WHITE_54, size=15)
        self.result = ft.Text(value="0", color=ft.Colors.WHITE, size=30)
        
        self.history_column = ft.Column(scroll=ft.ScrollMode.AUTO, height=0, visible=False)

        self.content = ft.Column(
            controls=[
                ft.Row([
                    ft.Text("Calculadora", weight="bold", color=ft.Colors.WHITE),
                    ft.IconButton(ft.Icons.HISTORY, on_click=self.toggle_history, icon_color=ft.Colors.WHITE)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                self.history_column,

                ft.Column(
                    controls=[
                        ft.Row(controls=[self.expression_txt], alignment=ft.MainAxisAlignment.END),
                        ft.Row(controls=[self.result], alignment=ft.MainAxisAlignment.END),
                    ],
                    spacing=0,
                ),
                ft.Row(controls=[
                    ExtraActionButton(content="AC", on_click=self.button_clicked),
                    ExtraActionButton(content="CE", on_click=self.button_clicked),
                    ExtraActionButton(content="\u2B05", on_click=self.button_clicked),
                    ActionButton(content="/", on_click=self.button_clicked),
                ]),
                ft.Row(controls=[
                    ExtraActionButton(content="(", on_click=self.button_clicked),
                    ExtraActionButton(content=")", on_click=self.button_clicked),
                    ExtraActionButton(content="√", on_click=self.button_clicked),
                    ActionButton(content="*", on_click=self.button_clicked),
                ]),
                ft.Row(controls=[
                    DigitButton(content="7", on_click=self.button_clicked),
                    DigitButton(content="8", on_click=self.button_clicked),
                    DigitButton(content="9", on_click=self.button_clicked),
                    ActionButton(content="-", on_click=self.button_clicked),
                ]),
                ft.Row(controls=[
                    DigitButton(content="4", on_click=self.button_clicked),
                    DigitButton(content="5", on_click=self.button_clicked),
                    DigitButton(content="6", on_click=self.button_clicked),
                    ActionButton(content="+", on_click=self.button_clicked),
                ]),
                ft.Row(controls=[
                    DigitButton(content="1", on_click=self.button_clicked),
                    DigitButton(content="2", on_click=self.button_clicked),
                    DigitButton(content="3", on_click=self.button_clicked),
                    ActionButton(content="^", on_click=self.button_clicked),
                ]),
                ft.Row(controls=[
                    DigitButton(content="1/x", on_click=self.button_clicked),
                    DigitButton(content="0", on_click=self.button_clicked),
                    DigitButton(content="!", on_click=self.button_clicked),
                    ActionButton(content="=", on_click=self.button_clicked),
                ]),
            ]
        )

    def toggle_history(self, e):
        self.history_column.visible = not self.history_column.visible
        self.history_column.height = 300 if self.history_column.visible else 0
        self.update()

    def delete_history_item(self, item):
        self.history_column.controls.remove(item)
        self.update()

    def add_to_history(self, expr, res):
        if self.is_continuation: return 
        
        self.history_index += 1
        item = HistoryItem(self.history_index, expr, res, self.delete_history_item)
        self.history_column.controls.insert(0, item)
        
        if len(self.history_column.controls) > 10:
            self.history_column.controls.pop()
        self.update()

    def format_with_spaces(self, text):
        clean_text = str(text).replace(" ", "")
        def replacer(match):
            num_str = match.group(0)
            if "." in num_str:
                parts = num_str.split(".")
                return "{:,}".format(int(parts[0])).replace(",", " ") + "." + parts[1]
            return "{:,}".format(int(num_str)).replace(",", " ")
        return re.sub(r'\d+(\.\d+)?', replacer, clean_text)

    def button_clicked(self, e):
        data = e.control.content if hasattr(e.control, 'content') else e.control.text
        current = self.result.value.replace(" ", "")

        if self.result.value == "Error" or data == "AC":
            self.result.value = "0"
            self.expression_txt.value = ""
            self.reset()
            self.is_continuation = False

        elif data in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0", ".", "(", ")"):
            if self.result.value == "0" or self.new_operand:
                self.result.value = data
                if self.new_operand: self.is_continuation = False
                self.new_operand = False
            else:
                self.result.value += data

        elif data in ("+", "-", "*", "/"):
            if self.new_operand: self.is_continuation = True
            self.result.value += data
            self.new_operand = False

        elif data == "=":
            try:
                raw_expr = current
                math_expr = current.replace("^", "**").replace("√", "sqrt").replace("!", "factorial")
                res = sympy.sympify(math_expr).evalf()
                final_val = float(res)
                if final_val % 1 == 0: final_val = int(final_val)

                res_str = self.format_with_spaces(str(round(final_val, 6)))
                
                self.add_to_history(f"{raw_expr} =", res_str)

                self.expression_txt.value = self.format_with_spaces(current) + " ="
                self.result.value = res_str
                self.new_operand = True
                self.update()
                return
            except:
                self.result.value = "Error"

        elif data == "CE":
            self.result.value = "0"
            self.new_operand = True

        elif data == "\u2B05":
            self.result.value = self.result.value[:-1] if len(self.result.value) > 1 else "0"

        elif data == "√":
            self.result.value = self.result.value + "sqrt(" if self.result.value != "0" else "sqrt("
            self.new_operand = False

        elif data == "1/x":
            self.result.value = self.result.value + "1/(" if self.result.value != "0" else "1/("
            self.new_operand = False

        elif data == "!":
            self.result.value += "!"

        elif data == "^":
            if self.result.value != "0":
                if self.result.value[-1] in "+-*/^":
                    self.result.value = self.result.value[:-1] + "^"
                else:
                    self.result.value += "^"
                self.new_operand = False

        self.result.value = self.format_with_spaces(self.result.value)
        self.update()

    def reset(self):
        self.new_operand = True

def main(page: ft.Page):
    page.title = "Calc App"
    page.horizontal_alignment = ft.MainAxisAlignment.CENTER
    calc = CalculatorApp()
    page.add(calc)

ft.run(main)