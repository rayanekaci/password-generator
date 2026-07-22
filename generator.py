import math
import secrets
import string
import tkinter as tk
from datetime import datetime

import customtkinter as ctk

# ── Configuration ──────────────────────────────────────────────────────────────
MAX_LENGTH = 256
MAX_HISTORY = 20

AMBIGUOUS_CHARS = set("0OoIl1|!;'\"`")

# ── Theme ──────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLORS = {
    "bg": "#0f0f1a",
    "surface": "#1a1a2e",
    "surface_alt": "#16213e",
    "accent": "#0f3460",
    "accent_light": "#1a4a7a",
    "button": "#e94560",
    "button_hover": "#ff6b81",
    "text": "#eaeaea",
    "text_dim": "#8892a4",
    "output_bg": "#0a0a1a",
    "strength_weak": "#e74c3c",
    "strength_medium": "#f39c12",
    "strength_strong": "#27ae60",
    "strength_very_strong": "#2ecc71",
    "toggle_on": "#e94560",
    "toggle_off": "#3a3a5c",
    "card": "#141428",
    "card_border": "#252545",
    "copy_success": "#27ae60",
    "history_bg": "#0d0d1e",
}

FONTS = {
    "title": ("Segoe UI", 22, "bold"),
    "section": ("Segoe UI", 13, "bold"),
    "body": ("Segoe UI", 13),
    "slider_label": ("Segoe UI", 16, "bold"),
    "password": ("Consolas", 14),
    "small": ("Segoe UI", 11),
    "strength_label": ("Segoe UI", 12, "bold"),
    "history_time": ("Consolas", 11),
    "copy_btn": ("Segoe UI", 11, "bold"),
}

# ── Password Generation ────────────────────────────────────────────────────────

def _build_pool(
    use_upper: bool,
    use_lower: bool,
    use_digits: bool,
    use_symbols: bool,
    exclude_ambiguous: bool,
) -> str:
    pool = ""
    if use_upper:
        pool += string.ascii_uppercase
    if use_lower:
        pool += string.ascii_lowercase
    if use_digits:
        pool += string.digits
    if use_symbols:
        pool += string.punctuation
    if exclude_ambiguous:
        pool = "".join(c for c in pool if c not in AMBIGUOUS_CHARS)
    return pool


def _required_chars(
    use_upper: bool,
    use_lower: bool,
    use_digits: bool,
    use_symbols: bool,
    exclude_ambiguous: bool,
) -> list[str]:
    required = []
    char_sets = [
        (use_upper, string.ascii_uppercase),
        (use_lower, string.ascii_lowercase),
        (use_digits, string.digits),
        (use_symbols, string.punctuation),
    ]
    for enabled, charset in char_sets:
        if enabled:
            chars = [c for c in charset if c not in AMBIGUOUS_CHARS] if exclude_ambiguous else list(charset)
            if chars:
                required.append(secrets.choice(chars))
    return required


def generate_password(
    length: int,
    use_upper: bool = True,
    use_lower: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
    exclude_ambiguous: bool = False,
) -> str:
    pool = _build_pool(use_upper, use_lower, use_digits, use_symbols, exclude_ambiguous)
    if not pool:
        return ""

    required = _required_chars(use_upper, use_lower, use_digits, use_symbols, exclude_ambiguous)
    remaining = max(0, length - len(required))
    password_chars = required + [secrets.choice(pool) for _ in range(remaining)]
    secrets.SystemRandom().shuffle(password_chars)
    return "".join(password_chars)


def calculate_strength(password: str) -> tuple[str, float]:
    """Returns (label, progress 0.0-1.0) based on entropy."""
    if not password:
        return ("None", 0.0)

    pool_size = 0
    if any(c in string.ascii_uppercase for c in password):
        pool_size += 26
    if any(c in string.ascii_lowercase for c in password):
        pool_size += 26
    if any(c in string.digits for c in password):
        pool_size += 10
    if any(c in string.punctuation for c in password):
        pool_size += len(string.punctuation)

    entropy = len(password) * math.log2(pool_size) if pool_size > 0 else 0

    if entropy < 28:
        return ("Very Weak", 0.1)
    elif entropy < 36:
        return ("Weak", 0.25)
    elif entropy < 60:
        return ("Medium", 0.5)
    elif entropy < 80:
        return ("Strong", 0.75)
    else:
        return ("Very Strong", 1.0)


def strength_color(label: str) -> str:
    mapping = {
        "Very Weak": COLORS["strength_weak"],
        "Weak": COLORS["strength_weak"],
        "Medium": COLORS["strength_medium"],
        "Strong": COLORS["strength_strong"],
        "Very Strong": COLORS["strength_very_strong"],
    }
    return mapping.get(label, COLORS["text_dim"])


# ── UI ─────────────────────────────────────────────────────────────────────────

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SecurePass Generator")
        self.configure(fg_color=COLORS["bg"])
        self.resizable(False, False)
        self.geometry("480x720")
        self.minsize(480, 720)
        self.history: list[tuple[str, str]] = []
        self._build_ui()

    # ── Layout ─────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_title()

        scrollable = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["bg"],
            scrollbar_button_color=COLORS["accent"],
            scrollbar_button_hover_color=COLORS["accent_light"],
        )
        scrollable.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self._build_length_section(scrollable)
        self._build_char_type_section(scrollable)
        self._build_quantity_section(scrollable)
        self._build_generate_button(scrollable)
        self._build_strength_section(scrollable)
        self._build_output_section(scrollable)
        self._build_history_section(scrollable)

    def _build_title(self):
        frame = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=0)
        frame.pack(fill="x", ipady=12)
        ctk.CTkLabel(
            frame,
            text="  SecurePass Generator",
            font=FONTS["title"],
            text_color=COLORS["text"],
        ).pack(anchor="w", padx=20)

    def _build_length_section(self, parent):
        card = self._card(parent)
        ctk.CTkLabel(
            card, text="PASSWORD LENGTH", font=FONTS["section"],
            text_color=COLORS["text_dim"], anchor="w",
        ).pack(fill="x", padx=16, pady=(12, 4))

        slider_row = ctk.CTkFrame(card, fg_color="transparent")
        slider_row.pack(fill="x", padx=16, pady=(0, 8))

        self.length_var = tk.IntVar(value=16)
        self.length_label = ctk.CTkLabel(
            slider_row, textvariable=self.length_var, font=FONTS["slider_label"],
            text_color=COLORS["button"], width=40,
        )
        self.length_label.pack(side="right")

        self.length_slider = ctk.CTkSlider(
            slider_row,
            from_=4,
            to=MAX_LENGTH,
            number_of_steps=MAX_LENGTH - 4,
            variable=self.length_var,
            command=self._on_slider_change,
            progress_color=COLORS["button"],
            button_color=COLORS["button"],
            button_hover_color=COLORS["button_hover"],
            fg_color=COLORS["toggle_off"],
            height=20,
        )
        self.length_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.min_length_label = ctk.CTkLabel(
            card, text="Min length adapts to selected character types",
            font=FONTS["small"], text_color=COLORS["text_dim"], anchor="w",
        )
        self.min_length_label.pack(fill="x", padx=16, pady=(0, 10))

    def _build_char_type_section(self, parent):
        card = self._card(parent)
        ctk.CTkLabel(
            card, text="CHARACTER TYPES", font=FONTS["section"],
            text_color=COLORS["text_dim"], anchor="w",
        ).pack(fill="x", padx=16, pady=(12, 8))

        self.use_upper = ctk.BooleanVar(value=True)
        self.use_lower = ctk.BooleanVar(value=True)
        self.use_digits = ctk.BooleanVar(value=True)
        self.use_symbols = ctk.BooleanVar(value=True)
        self.exclude_ambiguous = ctk.BooleanVar(value=False)

        toggles = [
            ("Uppercase  A-Z", self.use_upper),
            ("Lowercase  a-z", self.use_lower),
            ("Numbers    0-9", self.use_digits),
            ("Symbols    !@#$%^&*", self.use_symbols),
        ]

        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=16)
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        for i, (label, var) in enumerate(toggles):
            sw = ctk.CTkSwitch(
                grid, text=label, font=FONTS["body"],
                variable=var, onvalue=True, offvalue=False,
                button_color=COLORS["button"],
                button_hover_color=COLORS["button_hover"],
                progress_color=COLORS["button"],
                fg_color=COLORS["toggle_off"],
                text_color=COLORS["text"],
                command=self._on_toggle_change,
            )
            sw.grid(row=i // 2, column=i % 2, sticky="w", padx=4, pady=6)

        sep = ctk.CTkFrame(card, fg_color=COLORS["card_border"], height=1)
        sep.pack(fill="x", padx=16, pady=8)

        ctk.CTkSwitch(
            card, text="Exclude ambiguous  (0, O, l, 1, I)", font=FONTS["body"],
            variable=self.exclude_ambiguous, onvalue=True, offvalue=False,
            button_color=COLORS["button"],
            button_hover_color=COLORS["button_hover"],
            progress_color=COLORS["button"],
            fg_color=COLORS["toggle_off"],
            text_color=COLORS["text"],
        ).pack(fill="x", padx=16, pady=(0, 12))

    def _build_quantity_section(self, parent):
        card = self._card(parent)
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(
            row, text="QUANTITY", font=FONTS["section"],
            text_color=COLORS["text_dim"],
        ).pack(side="left")

        self.qty_var = tk.IntVar(value=1)

        ctk.CTkButton(
            row, text="−", width=36, height=36, font=FONTS["slider_label"],
            fg_color=COLORS["accent"], hover_color=COLORS["accent_light"],
            command=lambda: self._change_qty(-1),
        ).pack(side="right", padx=(4, 0))

        self.qty_label = ctk.CTkLabel(
            row, textvariable=self.qty_var, font=FONTS["slider_label"],
            text_color=COLORS["text"], width=30,
        )
        self.qty_label.pack(side="right")

        ctk.CTkButton(
            row, text="+", width=36, height=36, font=FONTS["slider_label"],
            fg_color=COLORS["accent"], hover_color=COLORS["accent_light"],
            command=lambda: self._change_qty(1),
        ).pack(side="right")

    def _build_generate_button(self, parent):
        self.generate_btn = ctk.CTkButton(
            parent,
            text="Generate",
            font=("Segoe UI", 15, "bold"),
            height=48,
            corner_radius=12,
            fg_color=COLORS["button"],
            hover_color=COLORS["button_hover"],
            command=self._on_generate,
        )
        self.generate_btn.pack(fill="x", pady=(4, 8), padx=2)

    def _build_strength_section(self, parent):
        card = self._card(parent)
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(12, 4))

        ctk.CTkLabel(
            row, text="STRENGTH", font=FONTS["section"],
            text_color=COLORS["text_dim"],
        ).pack(side="left")

        self.strength_text = ctk.CTkLabel(
            row, text="—", font=FONTS["strength_label"],
            text_color=COLORS["text_dim"],
        )
        self.strength_text.pack(side="right")

        self.strength_bar = ctk.CTkProgressBar(
            card, height=8, corner_radius=4,
            fg_color=COLORS["toggle_off"],
            progress_color=COLORS["text_dim"],
        )
        self.strength_bar.pack(fill="x", padx=16, pady=(4, 12))
        self.strength_bar.set(0)

    def _build_output_section(self, parent):
        card = self._card(parent)
        ctk.CTkLabel(
            card, text="GENERATED PASSWORDS", font=FONTS["section"],
            text_color=COLORS["text_dim"], anchor="w",
        ).pack(fill="x", padx=16, pady=(12, 4))

        self.output_box = ctk.CTkTextbox(
            card,
            font=FONTS["password"],
            height=80,
            fg_color=COLORS["output_bg"],
            text_color=COLORS["text"],
            corner_radius=8,
            border_width=1,
            border_color=COLORS["card_border"],
            activate_scrollbars=False,
            state="disabled",
        )
        self.output_box.pack(fill="x", padx=16, pady=(0, 4))

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=(0, 12))

        self.copy_btn = ctk.CTkButton(
            btn_row,
            text="Copy All",
            font=FONTS["copy_btn"],
            height=32,
            width=100,
            corner_radius=8,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_light"],
            command=self._on_copy,
        )
        self.copy_btn.pack(side="left")

        self.copy_feedback = ctk.CTkLabel(
            btn_row, text="", font=FONTS["small"],
            text_color=COLORS["copy_success"],
        )
        self.copy_feedback.pack(side="left", padx=10)

    def _build_history_section(self, parent):
        card = self._card(parent)
        ctk.CTkLabel(
            card, text="HISTORY", font=FONTS["section"],
            text_color=COLORS["text_dim"], anchor="w",
        ).pack(fill="x", padx=16, pady=(12, 4))

        self.history_box = ctk.CTkTextbox(
            card,
            font=FONTS["history_time"],
            height=100,
            fg_color=COLORS["history_bg"],
            text_color=COLORS["text_dim"],
            corner_radius=8,
            border_width=1,
            border_color=COLORS["card_border"],
            state="disabled",
        )
        self.history_box.pack(fill="x", padx=16, pady=(0, 12))

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _card(self, parent) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(
            parent,
            fg_color=COLORS["card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["card_border"],
        )
        frame.pack(fill="x", pady=4)
        return frame

    def _selected_count(self) -> int:
        return sum([
            self.use_upper.get(),
            self.use_lower.get(),
            self.use_digits.get(),
            self.use_symbols.get(),
        ])

    def _min_length(self) -> int:
        return max(self._selected_count(), 1)

    def _active_pool(self) -> str:
        return _build_pool(
            self.use_upper.get(),
            self.use_lower.get(),
            self.use_digits.get(),
            self.use_symbols.get(),
            self.exclude_ambiguous.get(),
        )

    # ── Event Handlers ─────────────────────────────────────────────────────────

    def _on_slider_change(self, _value):
        self.length_var.set(int(float(_value)))

    def _on_toggle_change(self):
        min_len = self._min_length()
        current = self.length_slider.get()
        if current < min_len:
            self.length_slider.set(min_len)
            self.length_var.set(min_len)

    def _change_qty(self, delta: int):
        current = self.qty_var.get()
        new_val = max(1, min(5, current + delta))
        self.qty_var.set(new_val)

    def _on_generate(self):
        pool = self._active_pool()
        if not pool:
            self._show_output("Select at least one character type.")
            return

        length = int(self.length_slider.get())
        min_len = self._min_length()
        if length < min_len:
            length = min_len
            self.length_slider.set(min_len)
            self.length_var.set(min_len)

        qty = self.qty_var.get()
        passwords = []
        for _ in range(qty):
            pw = generate_password(
                length,
                self.use_upper.get(),
                self.use_lower.get(),
                self.use_digits.get(),
                self.use_symbols.get(),
                self.exclude_ambiguous.get(),
            )
            passwords.append(pw)

        display = "\n".join(passwords)
        self._show_output(display)

        label, progress = calculate_strength(passwords[0])
        self.strength_bar.set(progress)
        self.strength_bar.configure(progress_color=strength_color(label))
        self.strength_text.configure(text=label, text_color=strength_color(label))

        now = datetime.now().strftime("%H:%M:%S")
        for pw in passwords:
            self.history.insert(0, (now, pw))
        self.history = self.history[:MAX_HISTORY]
        self._refresh_history()

    def _on_copy(self):
        text = self._get_output_text()
        if not text:
            return
        self.clipboard_clear()
        self.clipboard_append(text)
        self.copy_btn.configure(text="Copied!", fg_color=COLORS["copy_success"])
        self.copy_feedback.configure(text="Copied to clipboard")
        self.after(1500, self._reset_copy_btn)

    def _reset_copy_btn(self):
        self.copy_btn.configure(text="Copy All", fg_color=COLORS["accent"])
        self.copy_feedback.configure(text="")

    # ── Output Helpers ─────────────────────────────────────────────────────────

    def _show_output(self, text: str):
        self.output_box.configure(state="normal")
        self.output_box.delete("1.0", "end")
        self.output_box.insert("1.0", text)
        self.output_box.configure(state="disabled")

    def _get_output_text(self) -> str:
        self.output_box.configure(state="normal")
        text = self.output_box.get("1.0", "end").strip()
        self.output_box.configure(state="disabled")
        return text

    def _refresh_history(self):
        self.history_box.configure(state="normal")
        self.history_box.delete("1.0", "end")
        if not self.history:
            self.history_box.insert("1.0", "No passwords generated yet.")
        else:
            lines = [f"{time}   {pw}" for time, pw in self.history]
            self.history_box.insert("1.0", "\n".join(lines))
        self.history_box.configure(state="disabled")


if __name__ == "__main__":
    App().mainloop()
