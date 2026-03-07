from dataclasses import field
import flet as ft
import sympy
import re

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

@ft.control
class CalculatorApp(ft.Container):
    def init(self):
        
        
        self.reset()
        self.width = 400
        self.bgcolor = ft.Colors.BLACK
        self.border_radius = ft.BorderRadius.all(20)
        self.padding = 20
        

        self.expression_txt = ft.Text(value="", color=ft.Colors.WHITE_54, size=15)


        self.result = ft.Text(value="0", color=ft.Colors.WHITE, size=30)

        self.content = ft.Column(
        controls=[
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
        
    def format_with_spaces(self, text):
        clean_text = text.replace(" ", "")

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

        elif data in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0", ".", "(", ")"):
            if self.result.value == "0" or self.new_operand:
                self.result.value = data
                self.new_operand = False
            else:
                self.result.value += data

        elif data in ("+", "-", "*", "/"):
            self.result.value += data
            self.new_operand = False

        elif data == "=":
            try:
                math_expr = current.replace("^", "**").replace("√", "sqrt").replace("!", "factorial")
                res = sympy.sympify(math_expr).evalf()

                final_val = float(res)
                if final_val % 1 == 0:
                    final_val = int(final_val)

                self.expression_txt.value = self.format_with_spaces(current) + " ="
                self.result.value = self.format_with_spaces(str(round(final_val, 6)))
                self.new_operand = True
                self.update()
                return
            except:
                self.result.value = "Error"

        elif data == "%":
            try:
                self.result.value = str(float(self.result.value) / 100)
            except:
                self.result.value = "Error"

        elif data == "CE":
            self.result.value = "0"
            self.new_operand = True

        elif data == "\u2B05":
            if len(self.result.value) > 1:
                self.result.value = self.result.value[:-1]
            else:
                self.result.value = "0"

        elif data == "√":
            self.result.value = self.result.value + "sqrt(" if self.result.value != "0" else "sqrt("
            self.new_operand = False

        elif data == "1/x":
            self.result.value = self.result.value + "1/(" if self.result.value != "0" else "1/("
            self.new_operand = False

        elif data == "!":
            self.result.value += "!"

        elif data == "^":
          
            if self.result.value == "0":
                return

            if self.result.value[-1] in "+-*/^":
                self.result.value = self.result.value[:-1] + "^"
            else:
                self.result.value += "^"
            self.new_operand = False

        elif data == "+/-":
            try:
                if float(self.result.value) > 0:
                    self.result.value = "-" + str(self.result.value)
                else:
                    self.result.value = str(abs(float(self.result.value)))
            except:
                pass

        self.result.value = self.format_with_spaces(self.result.value)
        self.update()

    def format_number(self, num):
        num_float = float(num)
        if num_float % 1 == 0:
            return int(num_float)
        else:
            return round(num_float, 8)

    def reset(self):
        self.new_operand = True

def main(page: ft.Page):
    page.title = "Calc App"
    calc = CalculatorApp()
    page.add(calc)

ft.run(main)