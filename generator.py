import secrets
import string

import customtkinter as ctk
from tkinter import messagebox

MAX_LENGTH = 256

# --- Theme ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLORS = {
    "bg": "#1a1a2e",
    "surface": "#16213e",
    "accent": "#0f3460",
    "button": "#e94560",
    "button_hover": "#ff6b81",
    "text": "#eaeaea",
    "output_bg": "#0f3460",
}

FONT = ("Segoe UI", 14)
FONT_TITLE = ("Segoe UI", 20, "bold")


def generate_password(length: int) -> str:
    upper = secrets.choice(string.ascii_uppercase)
    lower = secrets.choice(string.ascii_lowercase)
    digit = secrets.choice(string.digits)
    symbol = secrets.choice(string.punctuation)
    rest = (
        secrets.choice(string.ascii_letters + string.digits + string.punctuation)
        for _ in range(length - 4)
    )
    password = list(upper + lower + digit + symbol) + list(rest)
    secrets.SystemRandom().shuffle(password)
    return "".join(password)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Password Generator")
        self.configure(fg_color=COLORS["bg"])
        self.resizable(False, False)
        self._build_ui()

    def _build_ui(self):
        container = ctk.CTkFrame(self, fg_color=COLORS["bg"])
        container.pack(padx=30, pady=30, fill="both", expand=True)

        ctk.CTkLabel(
            container, text="Password Generator", font=FONT_TITLE, text_color=COLORS["text"]
        ).pack(pady=(0, 20))

        ctk.CTkLabel(
            container, text="Password Length", font=FONT, text_color=COLORS["text"], anchor="w"
        ).pack(fill="x")

        self.entry = ctk.CTkEntry(
            container,
            placeholder_text="Enter length (min 4)",
            font=FONT,
            height=40,
            corner_radius=10,
            fg_color=COLORS["surface"],
            border_color=COLORS["accent"],
        )
        self.entry.pack(fill="x", pady=(5, 15))
        self.entry.bind("<Return>", lambda e: self._on_generate())
        self.entry.focus_set()

        self.generate_btn = ctk.CTkButton(
            container,
            text="Generate",
            font=FONT,
            height=44,
            corner_radius=10,
            fg_color=COLORS["button"],
            hover_color=COLORS["button_hover"],
            command=self._on_generate,
        )
        self.generate_btn.pack(fill="x", pady=(0, 15))

        self.output = ctk.CTkEntry(
            container,
            font=("Consolas", 16),
            height=44,
            corner_radius=10,
            fg_color=COLORS["output_bg"],
            border_color=COLORS["accent"],
            state="readonly",
        )
        self.output.pack(fill="x")

    def _on_generate(self):
        raw = self.entry.get().strip()
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
        password = generate_password(length)
        self.output.configure(state="normal")
        self.output.delete(0, "end")
        self.output.insert(0, password)
        self.output.configure(state="readonly")


if __name__ == "__main__":
    App().mainloop()
