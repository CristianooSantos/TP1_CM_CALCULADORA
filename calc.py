from dataclasses import field
import flet as ft
import sympy

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
        self.width = 350
        self.bgcolor = ft.Colors.BLACK
        self.border_radius = ft.BorderRadius.all(20)
        self.padding = 20
        

        self.full_expression = ft.Text(value="", color=ft.Colors.WHITE_54, size=15)

        self.result = ft.Text(value="0", color=ft.Colors.WHITE, size=30)

        self.content = ft.Column(
            controls=[
                ft.Column(
                    controls=[
                        ft.Row(controls=[self.full_expression], alignment=ft.MainAxisAlignment.END),
                        ft.Row(controls=[self.result], alignment=ft.MainAxisAlignment.END),
                    ],
                    spacing=0,
                ),
                ft.Row(
                    controls=[
                        ExtraActionButton(content="AC", on_click=self.button_clicked),
                        ExtraActionButton(content="(", on_click=self.button_clicked), 
                        ExtraActionButton(content=")", on_click=self.button_clicked), 
                        ActionButton(content="/", on_click=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(content="7", on_click=self.button_clicked),
                        DigitButton(content="8", on_click=self.button_clicked),
                        DigitButton(content="9", on_click=self.button_clicked),
                        ActionButton(content="*", on_click=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(content="4", on_click=self.button_clicked),
                        DigitButton(content="5", on_click=self.button_clicked),
                        DigitButton(content="6", on_click=self.button_clicked),
                        ActionButton(content="-", on_click=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(content="1", on_click=self.button_clicked),
                        DigitButton(content="2", on_click=self.button_clicked),
                        DigitButton(content="3", on_click=self.button_clicked),
                        ActionButton(content="+", on_click=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        DigitButton(
                            content="0", expand=2, on_click=self.button_clicked
                        ),
                        DigitButton(content=".", on_click=self.button_clicked),
                        ActionButton(content="=", on_click=self.button_clicked),
                    ]
                ),
            ]
        )

    def button_clicked(self, e):
        data = e.control.content if hasattr(e.control, 'content') else e.control.text
        
        if self.result.value == "Error" or data == "AC":
            self.result.value = "0"
            self.full_expression.value = ""
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
                raw_expression = self.result.value
                calculation = sympy.sympify(raw_expression).evalf()
                
                result_val = self.format_number(calculation)
                
                self.full_expression.value = f"{raw_expression} ="
                self.result.value = str(result_val)
                self.new_operand = True
            except Exception:
                self.result.value = "Error"

        elif data == "%":
            try:
                self.result.value = str(float(self.result.value) / 100)
            except:
                self.result.value = "Error"

        elif data == "+/-":
            try:
                if float(self.result.value) > 0:
                    self.result.value = "-" + str(self.result.value)
                else:
                    self.result.value = str(abs(float(self.result.value)))
            except:
                pass

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