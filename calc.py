from dataclasses import field
import flet as ft
import sympy
import re
from datetime import datetime
import duckdb
import os
import json

from calc_history import HistoryItem

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
    def __init__(self):
        super().__init__()
        self.reset()
        self.width = 400
        self.bgcolor = ft.Colors.BLACK
        self.border_radius = ft.BorderRadius.all(20)
        self.padding = 20
        
        self.db_path = "calc_history.parquet"
        self.history_loaded = False 
        
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

    def load_history(self, page):
        self.history_loaded = True
        saved_data = None
        

        if os.path.exists(self.db_path):
            try:
                con = duckdb.connect(':memory:')
                res = con.execute(f"SELECT expr, res FROM read_parquet('{self.db_path}')").fetchall()
                saved_data = [{"expr": r[0], "res": r[1]} for r in res]
                con.close()
            except Exception as e:
                print(f"Erro a ler ficheiro Parquet: {e}")

 
        if not saved_data and page and hasattr(page, "client_storage"):
            try:
                saved_data = page.client_storage.get("calc_history")
            except Exception:
                pass

       
        if saved_data:
            for item in reversed(saved_data):
                self.add_to_history(item["expr"], item["res"], page, sync=False)
            self.update()

    def save_and_sync(self, page):
        current_history = [
            {"expr": c.expression, "res": c.result_val} 
            for c in self.history_column.controls 
            if isinstance(c, HistoryItem)
        ]
        

        if not current_history:
            if os.path.exists(self.db_path): 
                os.remove(self.db_path)
        else:
            try:
                con = duckdb.connect(':memory:')
                con.execute("CREATE TABLE temp_history (expr VARCHAR, res VARCHAR)")
                for item in current_history:
                    con.execute("INSERT INTO temp_history VALUES (?, ?)", [item["expr"], item["res"]])
                con.execute(f"COPY temp_history TO '{self.db_path}' (FORMAT PARQUET)")
                con.close()
            except Exception as e:
                print(f"Erro ao escrever no Parquet: {e}")

        if page and hasattr(page, "client_storage"):
            try:
                page.client_storage.set("calc_history", current_history)
            except Exception:
                pass 

    def toggle_history(self, e):
            if not self.history_loaded:
                self.load_history(e.page)
                
            if self.history_column.height == 0:
                self.history_column.visible = True
                self.history_column.height = 300
                try:
                    e.page.window.height += 300  
                except Exception:
                    pass
            else:
                self.history_column.height = 0
                self.history_column.visible = False
                try:
                    e.page.window.height -= 300 
                except Exception:
                    pass
                    
            self.update()
            e.page.update()

    def delete_history_item(self, item):
        page_ref = item.page or self.page
        self.history_column.controls.remove(item)
        self.save_and_sync(page_ref)
        self.update()

    def add_to_history(self, expr, res, page, sync=True):
        if self.is_continuation: return 
        
        self.history_index += 1
        item = HistoryItem(self.history_index, expr, res, self.delete_history_item, page)
        self.history_column.controls.insert(0, item)
        
        if len(self.history_column.controls) > 10:
            self.history_column.controls.pop()
            
        if sync:
            self.save_and_sync(page)
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
        if not self.history_loaded:
            self.load_history(e.page)
            
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
        
                self.add_to_history(f"{raw_expr} =", res_str, e.page)

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
    page.title = "Calc CM A85245"
    page.horizontal_alignment = ft.MainAxisAlignment.CENTER
    calc = CalculatorApp()
    page.add(calc)

if __name__ == "__main__":
    ft.app(
        target=main,
        view=ft.AppView.WEB_BROWSER, 
        host="0.0.0.0",               
        port=8080,                    
        assets_dir="assets"          
    )