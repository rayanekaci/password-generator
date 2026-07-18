import secrets
import string
import tkinter as tk
from tkinter import messagebox

MAX_LENGTH = 256


def generate_password(length: int) -> str:
    upper = secrets.choice(string.ascii_uppercase)
    lower = secrets.choice(string.ascii_lowercase)
    digit = secrets.choice(string.digits)
    symbol = secrets.choice(string.punctuation)
    rest = (secrets.choice(string.ascii_letters + string.digits + string.punctuation)
            for _ in range(length - 4))
    password = list(upper + lower + digit + symbol) + list(rest)
    secrets.SystemRandom().shuffle(password)
    return "".join(password)


def on_generate():
    raw = entry.get().strip()
    if not raw.isdigit():
        messagebox.showerror("Invalid Input", "Please enter a number.")
        return
    length = int(raw)
    if length < 4:
        messagebox.showerror("Invalid Input", "Password length must be >= 4.")
        return
    if length > MAX_LENGTH:
        messagebox.showerror("Invalid Input", f"Password length must be <= {MAX_LENGTH}.")
        return
    result.set(generate_password(length))


root = tk.Tk()
root.title("Password Generator")
root.resizable(False, False)

tk.Label(root, text="Password length:").pack(padx=10, pady=(10, 0))

entry = tk.Entry(root)
entry.pack(padx=10, pady=5)
entry.bind("<Return>", lambda e: on_generate())
entry.focus_set()

tk.Button(root, text="Generate", command=on_generate).pack(padx=10, pady=5)

result = tk.StringVar()
output = tk.Entry(root, textvariable=result, width=40)
output.pack(padx=10, pady=(5, 10))
output.config(state="readonly")

root.mainloop()
