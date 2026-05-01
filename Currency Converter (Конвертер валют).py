import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

# ---------- Настройка API ----------
API_KEY = "ВАШ_API_КЛЮЧ"  # Замените на ваш ключ с https://app.exchangerate-api.com/sign-up
BASE_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/"

# ---------- Файл истории ----------
HISTORY_FILE = "conversion_history.json"

# ---------- Загрузка/сохранение истории ----------
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)

# ---------- Получение курса валют ----------
def get_exchange_rate(from_currency, to_currency):
    try:
        response = requests.get(BASE_URL + from_currency)
        data = response.json()
        if data["result"] == "success":
            return data["conversion_rates"].get(to_currency)
        else:
            return None
    except Exception as e:
        messagebox.showerror("Ошибка API", f"Не удалось получить курс: {e}")
        return None

# ---------- Конвертация и сохранение ----------
def convert_currency():
    try:
        amount = float(amount_entry.get())
        if amount <= 0:
            messagebox.showerror("Ошибка ввода", "Сумма должна быть положительным числом.")
            return
    except ValueError:
        messagebox.showerror("Ошибка ввода", "Введите корректное число.")
        return

    from_currency = from_currency_var.get()
    to_currency = to_currency_var.get()

    if from_currency == to_currency:
        result = amount
    else:
        rate = get_exchange_rate(from_currency, to_currency)
        if rate is None:
            messagebox.showerror("Ошибка конвертации", f"Не удалось получить курс {from_currency} -> {to_currency}.")
            return
        result = amount * rate

    # Отображение результата
    result_label.config(text=f"{amount:.2f} {from_currency} = {result:.2f} {to_currency}")

    # Сохранение в историю
    history_entry = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "from_currency": from_currency,
        "to_currency": to_currency,
        "amount": amount,
        "result": result
    }
    history.append(history_entry)
    save_history(history)
    update_history_table()

# ---------- Обновление таблицы истории ----------
def update_history_table():
    for row in history_table.get_children():
        history_table.delete(row)
    for entry in history[-10:]:  # показываем последние 10 записей
        history_table.insert("", tk.END, values=(
            entry["date"],
            f"{entry['amount']} {entry['from_currency']}",
            f"{entry['result']:.2f} {entry['to_currency']}"
        ))

# ---------- Загружаем существующую историю ----------
history = load_history()

# ---------- GUI ----------
root = tk.Tk()
root.title("Конвертер валют")
root.geometry("700x500")
root.resizable(False, False)

# Список валют
currencies = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "INR", "RUB"]

# Переменные для выбора валют
from_currency_var = tk.StringVar(value="USD")
to_currency_var = tk.StringVar(value="EUR")

# Рамка ввода
input_frame = ttk.LabelFrame(root, text="Конвертация", padding=10)
input_frame.pack(fill="x", padx=10, pady=5)

ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
amount_entry = ttk.Entry(input_frame, width=15)
amount_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(input_frame, text="Из:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
from_currency_menu = ttk.Combobox(input_frame, textvariable=from_currency_var, values=currencies, width=7)
from_currency_menu.grid(row=0, column=3, padx=5, pady=5)

ttk.Label(input_frame, text="В:").grid(row=0, column=4, padx=5, pady=5, sticky="w")
to_currency_menu = ttk.Combobox(input_frame, textvariable=to_currency_var, values=currencies, width=7)
to_currency_menu.grid(row=0, column=5, padx=5, pady=5)

convert_btn = ttk.Button(input_frame, text="Конвертировать", command=convert_currency)
convert_btn.grid(row=0, column=6, padx=10, pady=5)

# Метка результата
result_label = ttk.Label(input_frame, text="", font=("Arial", 10, "bold"))
result_label.grid(row=1, column=0, columnspan=7, pady=10)

# Рамка истории
history_frame = ttk.LabelFrame(root, text="История конвертаций (последние 10)", padding=10)
history_frame.pack(fill="both", expand=True, padx=10, pady=5)

columns = ("Дата", "Конвертация", "Результат")
history_table = ttk.Treeview(history_frame, columns=columns, show="headings", height=12)
history_table.heading("Дата", text="Дата")
history_table.heading("Конвертация", text="Конвертация")
history_table.heading("Результат", text="Результат")
history_table.column("Дата", width=150)
history_table.column("Конвертация", width=150)
history_table.column("Результат", width=150)
history_table.pack(fill="both", expand=True)

# Загрузка начальной истории
update_history_table()

# Запуск GUI
root.mainloop()
