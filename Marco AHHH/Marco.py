import customtkinter as ctk
from tkinter import messagebox, filedialog, Canvas, Toplevel
from PIL import Image, ImageEnhance, ImageFilter
import threading
import time
import ctypes
import json
import os
import random
import socket
import math
import requests
from io import BytesIO
import pydirectinput
from pynput.keyboard import Listener

try:
    from pypresence import Presence
except ImportError:
    Presence = None

# ============================================================
# KEY SYSTEM CONFIGURATION (INJECTED FROM EXTERNAL SCRIPT)
# ============================================================
VALID_KEYS = ["maddimov", "123456", "ahontop"]

class KeyWindow(ctk.CTk):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success
        self.title("AHHH Marco — Authentication")
        self.geometry("400x250")
        self.resizable(False, False)
        self.configure(fg_color="#07090f")
        
        # Center window
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"400x250+{(sw-400)//2}+{(sh-250)//2}")

        self.label = ctk.CTkLabel(self, text="ENTER ACCESS KEY", 
                                  font=("Consolas", 18, "bold"), text_color="#3b82f6")
        self.label.pack(pady=(40, 10))

        self.key_entry = ctk.CTkEntry(self, width=250, placeholder_text="Key...", 
                                      show="*", font=("Consolas", 12))
        self.key_entry.pack(pady=10)
        self.key_entry.bind("<Return>", lambda e: self.check_key())

        self.verify_btn = ctk.CTkButton(self, text="VERIFY", fg_color="#3b82f6", 
                                        hover_color="#60a5fa", font=("Consolas", 12, "bold"),
                                        command=self.check_key)
        self.verify_btn.pack(pady=20)

    def check_key(self):
        entered_key = self.key_entry.get().strip()
        if entered_key in VALID_KEYS:
            self.destroy()
            self.on_success()
        else:
            messagebox.showerror("Access Denied", "Invalid Key. Please try again.")

# ============================================================
# END KEY SYSTEM INJECTION
# ============================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CONFIG_FILE = "ahhh_config.json"

THEMES = {
    "Blue":   {"accent": "#3b82f6", "hover": "#60a5fa", "bg": "#07090f", "dim": "#0d1526"},
    "Purple": {"accent": "#a855f7", "hover": "#c084fc", "bg": "#09070f", "dim": "#170d26"},
    "Red":    {"accent": "#ef4444", "hover": "#f87171", "bg": "#0f0707", "dim": "#260d0d"},
    "Cyan":   {"accent": "#06b6d4", "hover": "#22d3ee", "bg": "#07100f", "dim": "#0d2226"},
    "Green":  {"accent": "#22c55e", "hover": "#4ade80", "bg": "#070f09", "dim": "#0d2614"},
    "RGB":    {"accent": "#ff0099", "hover": "#ffffff",  "bg": "#090909", "dim": "#1a0014"},
}

# ─────────────────────────────────────────────────────────────────────────────
# ICON RENDERER
# ─────────────────────────────────────────────────────────────────────────────

def draw_icon(canvas: Canvas, key: str, color: str, size: int = 22):
    canvas.delete("all")
    c = color
    w = h = size
    cx, cy = w / 2, h / 2
    m = size / 22

    if key == "click":
        pts = [
            cx, 3*m,
            cx - 5*m, cy + 7*m,
            cx - 1*m, cy + 5*m,
            cx - 3*m, cy + 9*m,
            cx,       cy + 8*m,
            cx + 3*m, cy + 9*m,
            cx + 1*m, cy + 5*m,
            cx + 5*m, cy + 7*m,
        ]
        canvas.create_polygon(pts, fill=c, outline="", smooth=False)

    elif key == "macro":
        pts = [
            cx + 3*m, 3*m,
            cx - 4*m, cy + 1*m,
            cx + 1*m, cy,
            cx - 2*m, h - 3*m,
            cx + 5*m, cy - 1*m,
            cx,       cy,
        ]
        canvas.create_polygon(pts, fill=c, outline="")

    elif key == "visual":
        canvas.create_arc(3*m, cy-5*m, w-3*m, cy+5*m,
                          start=0, extent=180, fill=c, outline="")
        canvas.create_arc(3*m, cy-5*m, w-3*m, cy+5*m,
                          start=180, extent=180, fill=c, outline="")
        canvas.create_oval(cx-4*m, cy-4*m, cx+4*m, cy+4*m,
                           fill="#09090f", outline="")
        canvas.create_oval(cx-2*m, cy-2*m, cx+2*m, cy+2*m, fill=c, outline="")

    elif key == "accounts":
        canvas.create_oval(cx-4*m, 3*m, cx+4*m, 10*m, fill=c, outline="")
        canvas.create_arc(3*m, 10*m, w-3*m, h+3*m,
                          start=0, extent=180, fill=c, outline="")

    elif key == "settings":
        canvas.create_oval(cx-6*m, cy-6*m, cx+6*m, cy+6*m,
                           outline=c, width=max(1, int(1.5*m)))
        canvas.create_oval(cx-2*m, cy-2*m, cx+2*m, cy+2*m, fill=c, outline="")
        for deg in range(0, 360, 45):
            rx = cx + 8*m * math.cos(math.radians(deg))
            ry = cy + 8*m * math.sin(math.radians(deg))
            canvas.create_oval(rx-1.2*m, ry-1.2*m, rx+1.2*m, ry+1.2*m,
                                fill=c, outline="")

    elif key == "power":
        canvas.create_arc(4*m, 4*m, w-4*m, h-4*m,
                          start=60, extent=240,
                          outline=c, width=max(1, int(2*m)), style="arc")
        canvas.create_line(cx, 3*m, cx, cy+1*m,
                           fill=c, width=max(1, int(2*m)))

    elif key == "roblox":
        canvas.create_text(cx, cy, text="R", fill=c,
                           font=("Consolas", int(size*0.7), "bold"), anchor="center")

    elif key == "friends":
        canvas.create_oval(3*m, 4*m, 12*m, 13*m, fill=c, outline="")
        canvas.create_oval(10*m, 4*m, 19*m, 13*m, fill=c, outline="")
        canvas.create_arc(3*m, 10*m, 12*m, h+2*m, start=0, extent=180, fill=c, outline="")
        canvas.create_arc(10*m, 10*m, 19*m, h+2*m, start=0, extent=180, fill=c, outline="")


# ─────────────────────────────────────────────────────────────────────────────
# SPLASH SCREEN  — uses plain Toplevel so it works before mainloop
# ─────────────────────────────────────────────────────────────────────────────

class SplashScreen(Toplevel):
    W, H = 580, 360

    def __init__(self, master, on_done):
        super().__init__(master)
        self._on_done   = on_done
        self._done      = False
        self._progress  = 0.0
        self._particles = []
        self._glitch_cd = 0

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        try:
            self.attributes("-alpha", 0.0)
        except Exception:
            pass
        self.configure(bg="#000000")
        self.resizable(False, False)

        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{self.W}x{self.H}+{(sw-self.W)//2}+{(sh-self.H)//2}")

        self.canvas = Canvas(self, width=self.W, height=self.H,
                             bg="#000000", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self._draw_static()
        self._init_particles()
        self.after(20, lambda: self._fade_in(0))

    # static elements
    def _draw_static(self):
        W, H = self.W, self.H

        for i, col in enumerate(["#06111f", "#091828", "#0d2040", "#1a3a60"]):
            self.canvas.create_rectangle(i, i, W-i, H-i, outline=col, width=1)

        sz, acc = 20, "#3b82f6"
        for (x1,y1,x2,y2,x3,y3) in [
            (0,sz,  0,0,  sz,0),
            (W-sz,0, W,0, W,sz),
            (0,H-sz, 0,H, sz,H),
            (W-sz,H, W,H, W,H-sz),
        ]:
            self.canvas.create_line(x1,y1, x2,y2, x3,y3, fill=acc, width=2)

        for y in range(0, H, 4):
            self.canvas.create_line(0, y, W, y, fill="#ffffff", stipple="gray12")

        self._title_id = self.canvas.create_text(
            W//2, 108, text="AHHH MARCO",
            font=("Consolas", 36, "bold"), fill="#3b82f6", anchor="center")

        self._sub_id = self.canvas.create_text(
            W//2, 150, text="U L T I M A T E   C L I E N T",
            font=("Consolas", 11), fill="#1e3a5f", anchor="center")

        self.canvas.create_text(
            W-14, H-12, text="v2.0",
            font=("Consolas", 10), fill="#0d2040", anchor="se")

        info_y = 175
        self.canvas.create_text(
            W//2, info_y, text="— ROBLOX RETRO EDITION —",
            font=("Consolas", 9), fill="#0d2a50", anchor="center")

        bx, by, bw, bh = 60, 225, W-120, 4
        self._bx, self._by, self._bw, self._bh = bx, by, bw, bh
        self.canvas.create_rectangle(bx, by, bx+bw, by+bh,
                                     fill="#0a1628", outline="#1e3a5f", width=1)
        self._bar_id = self.canvas.create_rectangle(
            bx, by, bx, by+bh, fill="#3b82f6", outline="")

        self._status_id = self.canvas.create_text(
            W//2, 243, text="Initializing...",
            font=("Consolas", 10), fill="#1e3a5f", anchor="center")

        self._dots = []
        n, sp = 16, 16
        x0 = W//2 - (n*sp)//2
        for i in range(n):
            d = self.canvas.create_oval(
                x0+i*sp, 262, x0+i*sp+6, 268,
                fill="#0a1628", outline="")
            self._dots.append(d)

    def _init_particles(self):
        for _ in range(48):
            self._particles.append({
                "x":  random.uniform(0, self.W),
                "y":  random.uniform(0, self.H),
                "vx": random.uniform(-0.3, 0.3),
                "vy": random.uniform(-0.7, -0.15),
                "r":  random.uniform(1, 2.5),
                "brightness": random.randint(40, 170),
                "id": None,
            })
        self._tick_particles()

    def _tick_particles(self):
        if self._done:
            return
        for p in self._particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            if p["y"] < -4:
                p["y"] = self.H + 2
                p["x"] = random.uniform(0, self.W)
            p["x"] %= self.W
            b = p["brightness"]
            r  = int(59  * b / 255)
            g  = int(130 * b / 255)
            bl = int(246 * b / 255)
            col = f"#{r:02x}{g:02x}{bl:02x}"
            rr = p["r"]
            x, y = p["x"], p["y"]
            if p["id"] is None:
                p["id"] = self.canvas.create_oval(
                    x-rr, y-rr, x+rr, y+rr, fill=col, outline="")
            else:
                self.canvas.coords(p["id"], x-rr, y-rr, x+rr, y+rr)
                self.canvas.itemconfig(p["id"], fill=col)
        self.after(28, self._tick_particles)

    def _fade_in(self, step):
        try:
            self.attributes("-alpha", min(step / 22, 1.0))
        except Exception:
            pass
        if step < 22:
            self.after(16, lambda: self._fade_in(step + 1))
        else:
            self.after(80, self._start_loading)

    _STEPS = [
        (0.08, "Loading core modules..."),
        (0.22, "Initializing click engine..."),
        (0.38, "Mounting macro system..."),
        (0.52, "Configuring hotkeys..."),
        (0.67, "Loading visual layer..."),
        (0.80, "Connecting to services..."),
        (0.93, "Almost ready..."),
        (1.00, "Done."),
    ]

    def _start_loading(self):
        self._step_idx = 0
        self._advance_step()

    def _advance_step(self):
        if self._step_idx >= len(self._STEPS):
            self.after(350, self._fade_out)
            return
        target, status = self._STEPS[self._step_idx]
        self._step_idx += 1
        self.canvas.itemconfig(self._status_id, text=status)
        self._tween(self._progress, target, 0)

    def _tween(self, start, end, tick):
        t    = min(tick / 20, 1.0)
        ease = t * (2 - t)
        cur  = start + (end - start) * ease

        bx, by, bw, bh = self._bx, self._by, self._bw, self._bh
        self.canvas.coords(self._bar_id, bx, by, bx + int(bw * cur), by + bh)

        glow_col = "#60a5fa" if int(time.time() * 8) % 2 == 0 else "#3b82f6"
        self.canvas.itemconfig(self._bar_id, fill=glow_col)

        lit = int(cur * len(self._dots))
        for i, d in enumerate(self._dots):
            if i < lit:
                self.canvas.itemconfig(d, fill="#3b82f6")
            elif i == lit:
                self.canvas.itemconfig(d, fill="#60a5fa")
            else:
                self.canvas.itemconfig(d, fill="#0a1628")

        self._glitch_cd += 1
        if self._glitch_cd % 10 == 0:
            src    = "AHHH MARCO"
            glyphs = "!@#$%<>?/\\|^~*"
            out = "".join(
                random.choice(glyphs) if c != " " and random.random() < 0.09 else c
                for c in src)
            self.canvas.itemconfig(self._title_id, text=out)
            self.after(55, lambda: self.canvas.itemconfig(
                self._title_id, text="AHHH MARCO"))

        if tick < 20:
            self.after(20, lambda: self._tween(start, end, tick + 1))
        else:
            self._progress = end
            self.after(110, self._advance_step)

    def _fade_out(self, step=0):
        try:
            self.attributes("-alpha", max(1.0 - step / 18, 0.0))
        except Exception:
            pass
        if step < 18:
            self.after(14, lambda: self._fade_out(step + 1))
        else:
            self._done = True
            self.destroy()
            self._on_done()


# ─────────────────────────────────────────────────────────────────────────────
# GAME-JOINED TOAST  (shown top-right for 4 seconds)
# ─────────────────────────────────────────────────────────────────────────────

class GameJoinToast(Toplevel):
    W, H = 300, 110

    def __init__(self, master, username: str, game_name: str, region: str, accent: str):
        super().__init__(master)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        try:
            self.attributes("-alpha", 0.0)
        except Exception:
            pass
        self.configure(bg="#07090f")

        sw = self.winfo_screenwidth()
        self.geometry(f"{self.W}x{self.H}+{sw - self.W - 20}+20")

        canvas = Canvas(self, width=self.W, height=self.H,
                        bg="#07090f", highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        canvas.create_rectangle(0, 0, self.W, self.H, outline=accent, width=2)
        canvas.create_rectangle(2, 2, self.W-2, 4, fill=accent, outline="")

        canvas.create_text(14, 16, text="● GAME JOINED",
                           font=("Consolas", 10, "bold"), fill=accent, anchor="w")

        rows = [
            ("USERNAME", username),
            ("GAME",     game_name),
            ("SERVER",   region),
        ]
        for i, (k, v) in enumerate(rows):
            y = 36 + i * 20
            canvas.create_text(14, y, text=k, font=("Consolas", 8),
                                fill="#1e3a5f", anchor="w")
            canvas.create_text(self.W - 14, y, text=v,
                                font=("Consolas", 9, "bold"), fill="#e2e8f0", anchor="e")

        self._fade_in(0)
        self.after(3800, lambda: self._fade_out(0))

    def _fade_in(self, step):
        try:
            self.attributes("-alpha", min(step / 12, 0.96))
        except Exception:
            pass
        if step < 12:
            self.after(14, lambda: self._fade_in(step + 1))

    def _fade_out(self, step):
        try:
            self.attributes("-alpha", max(0.96 - step / 14, 0.0))
        except Exception:
            pass
        if step < 14:
            self.after(14, lambda: self._fade_out(step + 1))
        else:
            try:
                self.destroy()
            except Exception:
                pass


# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────────────────────────

class AHHHMarco(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.withdraw()

        self.title("AHHH Marco Ultimate — Roblox Retro Edition")
        self.geometry("1360x860")
        self.minsize(1000, 640)
        self.resizable(True, True)
        try:
            self.attributes("-alpha", 0.0)
        except Exception:
            pass

        # state
        self.clicking      = False
        self.shift_spam    = False
        self.key_spam      = False
        self.afk_mode      = False
        self.always_on_top = False
        self.cps           = 20
        self.spam_key      = "space"
        self.theme_name    = "Blue"
        self.bg_opacity    = 0.35
        self.bg_blur       = 0
        self.hotkey_char   = "f"
        self.background_path = None
        self._rgb_running  = False
        self._last_frame   = time.perf_counter()
        self._frame_times  = []
        self.rpc           = None
        self._tab_headers  = []

        # Roblox session state
        self.roblox_username  = ""
        self.roblox_game      = "Brookhaven RP"
        self.roblox_region    = "US-East"
        self._auto_rejoin     = False
        self._auto_reconnect  = False
        self._anti_idle_rc    = False

        self._build_bg()
        self._build_sidebar()
        self._build_tabs()

        self.load_config()
        self.apply_theme(self.theme_name)

        for fn in (self._click_engine, self._shift_engine,
                   self._key_engine,   self._afk_engine, self._stats_loop):
            threading.Thread(target=fn, daemon=True).start()

        Listener(on_press=self._on_key).start()
        self._start_rpc()

    def show_after_splash(self):
        self.deiconify()
        self._fade_in(0)

    def _build_bg(self):
        blank = Image.new("RGB", (10, 10), "#060606")
        self._bg_ctk = ctk.CTkImage(light_image=blank, dark_image=blank, size=(1360, 860))
        self.bg_label = ctk.CTkLabel(self, image=self._bg_ctk, text="")
        self.bg_label.place(relwidth=1, relheight=1)
        self.bg_label.lower()
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        if self.background_path and event.widget is self:
            if hasattr(self, "_resize_job"):
                self.after_cancel(self._resize_job)
            self._resize_job = self.after(
                200, lambda: self._set_background(self.background_path))

    def _set_background(self, path):
        try:
            w, h = self.winfo_width(), self.winfo_height()
            if w < 10 or h < 10:
                return
            img = Image.open(path).convert("RGB").resize((w, h), Image.LANCZOS)
            if self.bg_blur > 0:
                img = img.filter(ImageFilter.GaussianBlur(radius=self.bg_blur))
            img = ImageEnhance.Brightness(img).enhance(
                max(0.05, min(1.0, self.bg_opacity)))
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(w, h))
            self.after(0, lambda: self.bg_label.configure(image=ctk_img))
            self._bg_ctk = ctk_img
        except Exception as e:
            print(f"[bg] {e}")

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=230, corner_radius=0, fg_color="#040407")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        logo_f = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_f.pack(pady=(26, 6), fill="x")
        self.logo_top = ctk.CTkLabel(
            logo_f, text="AHHH", font=("Consolas", 30, "bold"))
        self.logo_top.pack()
        self.logo_bot = ctk.CTkLabel(
            logo_f, text="M A R C O  ✦  RETRO",
            font=("Consolas", 10), text_color="#1e3a5f")
        self.logo_bot.pack()

        ctk.CTkFrame(self.sidebar, height=1, fg_color="#0d1526").pack(
            fill="x", padx=14, pady=10)

        nav_defs = [
            ("click",    "AUTOCLICKER", "Autoclicker"),
            ("macro",    "MACROS",      "Macros"),
            ("roblox",   "ROBLOX",      "Roblox"),
            ("friends",  "FRIENDS",     "Friends"),
            ("accounts", "AVATAR",      "Accounts"),
            ("visual",   "VISUAL",      "Visual"),
            ("settings", "SETTINGS",    "Settings"),
        ]
        self.nav_buttons = {}
        for icon_key, label, tab in nav_defs:
            btn = self._nav_btn(icon_key, label, lambda t=tab: self.tabs.set(t))
            btn.pack(padx=10, pady=3, fill="x")
            self.nav_buttons[tab] = btn

        ctk.CTkFrame(self.sidebar, height=1, fg_color="#0d1526").pack(
            fill="x", padx=14, pady=10)

        stat_f = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        stat_f.pack(side="bottom", fill="x", padx=14, pady=14)

        self.status_label = ctk.CTkLabel(
            stat_f, text="● IDLE", font=("Consolas", 11, "bold"),
            text_color="#1e3a5f")
        self.fps_label = ctk.CTkLabel(
            stat_f, text="FPS  —", font=("Consolas", 11),
            text_color="#334155")
        self.ping_label = ctk.CTkLabel(
            stat_f, text="PING —ms", font=("Consolas", 11),
            text_color="#334155")
        self.roblox_info_label = ctk.CTkLabel(
            stat_f, text="PLAYING: —", font=("Consolas", 9),
            text_color="#0d2040", wraplength=200)

        self.status_label.pack(anchor="w", pady=(0, 4))
        self.fps_label.pack(anchor="w")
        self.ping_label.pack(anchor="w")
        self.roblox_info_label.pack(anchor="w", pady=(6, 0))

    def _nav_btn(self, icon_key, label, command):
        frame = ctk.CTkFrame(
            self.sidebar, fg_color="#09090f", corner_radius=10,
            border_width=1, border_color="#0d1526", height=46)
        frame.pack_propagate(False)

        for widget in (frame,):
            widget.bind("<Enter>",
                lambda e, f=frame, k=icon_key: self._nav_hover(f, k, True))
            widget.bind("<Leave>",
                lambda e, f=frame, k=icon_key: self._nav_hover(f, k, False))
            widget.bind("<Button-1>", lambda e: command())

        ic = Canvas(frame, width=22, height=22, bg="#09090f", highlightthickness=0)
        ic.pack(side="left", padx=(12, 8), pady=12)
        ic.bind("<Button-1>", lambda e: command())
        ic.bind("<Enter>",
            lambda e, f=frame, k=icon_key: self._nav_hover(f, k, True))
        ic.bind("<Leave>",
            lambda e, f=frame, k=icon_key: self._nav_hover(f, k, False))
        draw_icon(ic, icon_key, "#283858")

        lbl = ctk.CTkLabel(frame, text=label,
                           font=("Consolas", 11, "bold"),
                           text_color="#334155", anchor="w")
        lbl.pack(side="left", fill="x", expand=True)
        lbl.bind("<Button-1>", lambda e: command())
        lbl.bind("<Enter>",
            lambda e, f=frame, k=icon_key: self._nav_hover(f, k, True))
        lbl.bind("<Leave>",
            lambda e, f=frame, k=icon_key: self._nav_hover(f, k, False))

        frame._ic  = ic
        frame._lbl = lbl
        frame._key = icon_key
        return frame

    def _nav_hover(self, frame, icon_key, entering):
        accent = THEMES[self.theme_name]["accent"]
        if entering:
            bg = THEMES[self.theme_name]["dim"]
            frame.configure(fg_color=bg, border_color=accent + "44")
            frame._ic.configure(bg=bg)
            frame._lbl.configure(text_color=accent)
            draw_icon(frame._ic, icon_key, accent)
        else:
            frame.configure(fg_color="#09090f", border_color="#0d1526")
            frame._ic.configure(bg="#09090f")
            frame._lbl.configure(text_color="#334155")
            draw_icon(frame._ic, icon_key, "#283858")

    def _build_tabs(self):
        self.tabs = ctk.CTkTabview(self, corner_radius=14, fg_color="#06060c")
        self.tabs.pack(expand=True, fill="both", padx=12, pady=12)
        for name in ("Autoclicker", "Macros", "Roblox", "Friends",
                     "Accounts", "Visual", "Settings"):
            self.tabs.add(name)
        self._build_autoclicker()
        self._build_macros()
        self._build_roblox()
        self._build_friends()
        self._build_accounts()
        self._build_visual()
        self._build_settings()

    def _card(self, parent, title=""):
        outer = ctk.CTkFrame(parent, fg_color="#09090f", corner_radius=12,
                              border_width=1, border_color="#0d1526")
        outer.pack(fill="x", padx=26, pady=7)
        if title:
            ctk.CTkLabel(outer, text=title, font=("Consolas", 9),
                         text_color="#1e3a5f").pack(anchor="w", padx=14, pady=(10, 2))
        return outer

    def _tab_header(self, tab, title, icon_key):
        f = ctk.CTkFrame(tab, fg_color="transparent")
        f.pack(fill="x", padx=26, pady=(18, 4))
        accent = THEMES[self.theme_name]["accent"]
        bg_col = THEMES[self.theme_name]["bg"]
        ic = Canvas(f, width=30, height=30, bg=bg_col, highlightthickness=0)
        ic.pack(side="left", padx=(0, 10))
        draw_icon(ic, icon_key, accent, size=30)
        ctk.CTkLabel(f, text=title, font=("Consolas", 20, "bold")).pack(side="left")
        self._tab_headers.append((ic, icon_key, bg_col))

    def _switch(self, parent, text, cmd=None):
        sw = ctk.CTkSwitch(parent, text=text, font=("Consolas", 12),
                           command=cmd if cmd else lambda: None)
        sw.pack(padx=14, pady=(4, 10), anchor="w")
        return sw

    # AUTOCLICKER
    def _build_autoclicker(self):
        tab = self.tabs.tab("Autoclicker")
        self._tab_header(tab, "AUTOCLICKER", "click")

        c1 = self._card(tab, "ENGINE")
        self.click_switch = self._switch(c1, "Enable Autoclicker", self._sync_click)

        c2 = self._card(tab, "CLICKS PER SECOND")
        self.cps_num = ctk.CTkLabel(c2, text=str(self.cps),
                                     font=("Consolas", 42, "bold"))
        self.cps_num.pack(pady=(6, 0))
        ctk.CTkLabel(c2, text="CPS", font=("Consolas", 10),
                     text_color="#1e3a5f").pack()
        self.cps_slider = ctk.CTkSlider(c2, from_=1, to=100,
                                         command=self._update_cps)
        self.cps_slider.set(self.cps)
        self.cps_slider.pack(fill="x", padx=20, pady=(4, 14))

        c3 = self._card(tab, "CLICK MODE")
        mode_row = ctk.CTkFrame(c3, fg_color="transparent")
        mode_row.pack(fill="x", padx=14, pady=(0, 10))
        self.click_mode = ctk.CTkComboBox(
            mode_row,
            values=["Normal", "Jitter", "Butterfly", "Drag Click", "Hold Left", "Hold Right"],
            font=("Consolas", 12), width=200)
        self.click_mode.set("Normal")
        self.click_mode.pack(side="left")

        c4 = self._card(tab, "SMART RANDOMIZER")
        self.rand_switch = self._switch(
            c4, "Humanize clicking (randomizes CPS, delays, patterns)")

        c5 = self._card(tab, "TOGGLE HOTKEY")
        row = ctk.CTkFrame(c5, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=(4, 12))
        self.hotkey_entry = ctk.CTkEntry(row, width=64, font=("Consolas", 13),
                                          placeholder_text="key")
        self.hotkey_entry.insert(0, self.hotkey_char)
        self.hotkey_entry.pack(side="left", padx=(0, 8))
        ctk.CTkButton(row, text="SET", width=60, font=("Consolas", 11, "bold"),
                       command=self._set_hotkey).pack(side="left")
        self.hotkey_label = ctk.CTkLabel(
            row, text=f"[ {self.hotkey_char.upper()} ]",
            font=("Consolas", 13, "bold"), text_color="#334155")
        self.hotkey_label.pack(side="left", padx=10)

    # MACROS
    def _build_macros(self):
        tab = self.tabs.tab("Macros")
        self._tab_header(tab, "MACROS", "macro")

        c1 = self._card(tab, "SHIFT SPAM")
        self.shift_switch = self._switch(
            c1, "Spam SHIFT key continuously", self._toggle_shift)

        c2 = self._card(tab, "KEY SPAMMER")
        self.key_switch = self._switch(
            c2, "Enable Key Spammer", self._toggle_key)
        row = ctk.CTkFrame(c2, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=(0, 12))
        self.key_box = ctk.CTkEntry(
            row, placeholder_text="key name (e.g. space, e, f1)",
            font=("Consolas", 12))
        self.key_box.insert(0, self.spam_key)
        self.key_box.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(row, text="APPLY", width=70, font=("Consolas", 11, "bold"),
                       command=self._apply_spam_key).pack(side="left")

        c3 = self._card(tab, "AFK MODE")
        self.afk_switch = self._switch(
            c3, "Anti-AFK (mouse jitter + SPACE every ~3s)", self._toggle_afk)

        c4 = self._card(tab, "MACRO RECORDER")
        rec_row = ctk.CTkFrame(c4, fg_color="transparent")
        rec_row.pack(fill="x", padx=14, pady=(0, 6))
        ctk.CTkButton(rec_row, text="● REC", width=70, font=("Consolas", 10, "bold"),
                       fg_color="#ef4444").pack(side="left", padx=(0, 6))
        ctk.CTkButton(rec_row, text="▶ PLAY", width=70, font=("Consolas", 10, "bold"),
                       fg_color="#22c55e").pack(side="left", padx=(0, 6))
        ctk.CTkButton(rec_row, text="■ STOP", width=70,
                       font=("Consolas", 10, "bold")).pack(side="left", padx=(0, 6))
        ctk.CTkButton(rec_row, text="⬇ EXPORT", width=80,
                       font=("Consolas", 10, "bold")).pack(side="left")

        c5 = self._card(tab, "AUTO CHAT SPAM")
        self.chat_spam_switch = self._switch(c5, "Enable rotating chat messages")
        self.chat_box = ctk.CTkTextbox(c5, height=80, font=("Consolas", 11),
                                        fg_color="#050508")
        self.chat_box.pack(fill="x", padx=14, pady=(0, 10))
        self.chat_box.insert("0.0", "Hi everyone!\nLet's play!\ngot any tips?")

        c6 = self._card(tab, "AUTO PATH WALKER")
        pw_row = ctk.CTkFrame(c6, fg_color="transparent")
        pw_row.pack(fill="x", padx=14, pady=(0, 10))
        ctk.CTkButton(pw_row, text="● RECORD PATH", font=("Consolas", 10, "bold"),
                       fg_color="#ef4444").pack(side="left", padx=(0, 8))
        ctk.CTkButton(pw_row, text="▶ REPLAY", font=("Consolas", 10, "bold"),
                       fg_color="#22c55e").pack(side="left", padx=(0, 8))
        ctk.CTkButton(pw_row, text="EDIT WAYPOINTS",
                       font=("Consolas", 10, "bold")).pack(side="left")

        c7 = self._card(tab, "INVENTORY AUTOMATION")
        inv_row = ctk.CTkFrame(c7, fg_color="transparent")
        inv_row.pack(fill="x", padx=14, pady=(0, 12))
        for lbl in ("Auto Equip", "Auto Sort", "Auto Click Slots"):
            self._switch(c7, lbl)

    # ROBLOX
    def _build_roblox(self):
        tab = self.tabs.tab("Roblox")
        self._tab_header(tab, "ROBLOX TOOLS", "roblox")

        sf = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        sf.pack(fill="both", expand=True, padx=0, pady=0)

        cj = self._card(sf, "SERVER JOINER")
        ctk.CTkLabel(cj, text="PLAYING:  Brookhaven RP",
                     font=("Consolas", 11), text_color="#3b82f6").pack(
            anchor="w", padx=14, pady=(2, 0))
        ctk.CTkLabel(cj, text="SERVER:   US-East",
                     font=("Consolas", 11), text_color="#3b82f6").pack(
            anchor="w", padx=14, pady=(0, 4))
        server_row = ctk.CTkFrame(cj, fg_color="transparent")
        server_row.pack(fill="x", padx=14, pady=(0, 6))
        self.server_id_entry = ctk.CTkEntry(
            server_row, placeholder_text="Enter Server ID...",
            font=("Consolas", 12))
        self.server_id_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(server_row, text="JOIN", width=70,
                       font=("Consolas", 11, "bold"),
                       fg_color="#22c55e",
                       command=self._join_server).pack(side="left", padx=(0, 6))
        ctk.CTkButton(server_row, text="COPY LINK", width=90,
                       font=("Consolas", 11, "bold"),
                       command=self._copy_join_link).pack(side="left")

        cr = self._card(sf, "SERVER REGION")
        regions = ["US-East", "US-West", "EU-West", "EU-Central",
                   "Asia-Pacific", "South America"]
        self.region_box = ctk.CTkComboBox(
            cr, values=regions, font=("Consolas", 12), width=200,
            command=self._set_region)
        self.region_box.set(self.roblox_region)
        self.region_box.pack(padx=14, pady=(0, 10))

        carc = self._card(sf, "AUTO RECONNECT")
        self.auto_rejoin_sw = self._switch(
            carc, "Auto Rejoin if kicked",
            lambda: setattr(self, "_auto_rejoin",
                            bool(self.auto_rejoin_sw.get())))
        self.auto_reconnect_sw = self._switch(
            carc, "Reconnect on disconnect",
            lambda: setattr(self, "_auto_reconnect",
                            bool(self.auto_reconnect_sw.get())))
        self.anti_idle_rc_sw = self._switch(
            carc, "Anti-idle reconnect",
            lambda: setattr(self, "_anti_idle_rc",
                            bool(self.anti_idle_rc_sw.get())))

        cn = self._card(sf, "GAME JOINED NOTIFICATION")
        ctk.CTkLabel(cn, text="Username:", font=("Consolas", 11)).pack(
            anchor="w", padx=14, pady=(0, 2))
        self.notif_user_entry = ctk.CTkEntry(
            cn, placeholder_text="Your Roblox username",
            font=("Consolas", 12))
        self.notif_user_entry.pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkLabel(cn, text="Game Name:", font=("Consolas", 11)).pack(
            anchor="w", padx=14, pady=(0, 2))
        self.notif_game_entry = ctk.CTkEntry(
            cn, placeholder_text="Game name",
            font=("Consolas", 12))
        self.notif_game_entry.insert(0, "Brookhaven RP")
        self.notif_game_entry.pack(fill="x", padx=14, pady=(0, 4))
        ctk.CTkButton(cn, text="▶ SHOW GAME JOINED NOTIFICATION",
                       font=("Consolas", 11, "bold"),
                       command=self._show_join_toast).pack(
            padx=14, pady=(0, 12))

    def _join_server(self):
        sid = self.server_id_entry.get().strip()
        if sid:
            self._show_join_toast()

    def _copy_join_link(self):
        sid = self.server_id_entry.get().strip()
        link = f"roblox://experiences/start?placeId=0&gameInstanceId={sid or 'XXXXX'}"
        self.clipboard_clear()
        self.clipboard_append(link)

    def _set_region(self, region):
        self.roblox_region = region
        self.after(0, self._update_roblox_sidebar)

    def _update_roblox_sidebar(self):
        game = self.notif_game_entry.get().strip() if hasattr(self, "notif_game_entry") else self.roblox_game
        user = self.notif_user_entry.get().strip() if hasattr(self, "notif_user_entry") else self.roblox_username
        text = f"PLAYING: {game or '—'}\nSERVER: {self.roblox_region}\nUSER: {user or '—'}"
        self.roblox_info_label.configure(text=text)

    def _show_join_toast(self):
        user = ""
        game = ""
        region = self.roblox_region
        if hasattr(self, "notif_user_entry"):
            user = self.notif_user_entry.get().strip()
        if hasattr(self, "notif_game_entry"):
            game = self.notif_game_entry.get().strip()
        if not user:
            user = self.roblox_username or "Player"
        if not game:
            game = self.roblox_game
        accent = THEMES[self.theme_name]["accent"]
        GameJoinToast(self, username=user, game_name=game,
                      region=region, accent=accent)
        self._update_roblox_sidebar()

    # FRIENDS
    def _build_friends(self):
        tab = self.tabs.tab("Friends")
        self._tab_header(tab, "FRIEND TRACKER", "friends")

        c1 = self._card(tab, "ONLINE FRIENDS")
        ctk.CTkLabel(c1, text="Enter your username to load friends (API required)",
                     font=("Consolas", 10), text_color="#334155").pack(
            anchor="w", padx=14, pady=(0, 4))
        row = ctk.CTkFrame(c1, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=(0, 10))
        self.friend_user_entry = ctk.CTkEntry(
            row, placeholder_text="Roblox Username",
            font=("Consolas", 12))
        self.friend_user_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(row, text="LOAD FRIENDS", font=("Consolas", 11, "bold"),
                       command=self._load_friends).pack(side="left")

        self.friend_box = ctk.CTkTextbox(tab, height=220,
                                          font=("Consolas", 11), fg_color="#050508")
        self.friend_box.pack(fill="x", padx=26, pady=8)
        self.friend_box.insert("end",
            "─── ONLINE FRIENDS ───────────────────────\n"
            "  CoolGamer123       [ Brookhaven RP ]   [ JOIN ]\n"
            "  xXSwordMasterXx   [ Blox Fruits   ]   [ JOIN ]\n"
            "  StarBuilder_X      [ Online        ]   [ JOIN ]\n"
            "─── OFFLINE ───────────────────────────────\n"
            "  NightOwl2099       [ Offline       ]\n")
        self.friend_box.configure(state="disabled")

        c2 = self._card(tab, "SETTINGS")
        self._switch(c2, "Show join buttons")
        self._switch(c2, "Notify when friend joins a game")

    def _load_friends(self):
        username = self.friend_user_entry.get().strip()
        if username:
            self.friend_box.configure(state="normal")
            self.friend_box.delete("0.0", "end")
            self.friend_box.insert("end", f"Loading friends for {username}...\n")
            self.friend_box.configure(state="disabled")
            threading.Thread(
                target=self._fetch_friends, args=(username,), daemon=True).start()

    def _fetch_friends(self, username):
        try:
            r   = requests.post(
                "https://users.roblox.com/v1/usernames/users",
                json={"usernames": [username], "excludeBannedUsers": True},
                timeout=6)
            data = r.json()
            if not data.get("data"):
                raise ValueError("User not found")
            uid  = data["data"][0]["id"]
            fr   = requests.get(
                f"https://friends.roblox.com/v1/users/{uid}/friends/online",
                timeout=6).json()
            lines = ["─── ONLINE FRIENDS ─────────────────────────\n"]
            for f in fr.get("data", []):
                name = f.get("name", "?")
                pg   = f.get("userPresence", {})
                game = pg.get("lastLocation", "Online")
                lines.append(f"  {name:<22} [ {game[:18]:<18} ]\n")
            if len(lines) == 1:
                lines.append("  No online friends found.\n")
            def update():
                self.friend_box.configure(state="normal")
                self.friend_box.delete("0.0", "end")
                for l in lines:
                    self.friend_box.insert("end", l)
                self.friend_box.configure(state="disabled")
            self.after(0, update)
        except Exception as e:
            def err():
                self.friend_box.configure(state="normal")
                self.friend_box.delete("0.0", "end")
                self.friend_box.insert("end", f"Error: {e}\nMake sure the username is correct.\n")
                self.friend_box.configure(state="disabled")
            self.after(0, err)

    # ACCOUNTS
    def _build_accounts(self):
        tab = self.tabs.tab("Accounts")
        self._tab_header(tab, "AVATAR INSPECTOR", "accounts")

        self.avatar_label = ctk.CTkLabel(tab, text="", width=130, height=130)
        self.avatar_label.pack(pady=8)

        c1 = self._card(tab, "ROBLOX ACCOUNT")
        self.user_entry = ctk.CTkEntry(
            c1, placeholder_text="Roblox Username", font=("Consolas", 12))
        self.user_entry.pack(fill="x", padx=14, pady=(4, 6))
        self.display_entry = ctk.CTkEntry(
            c1, placeholder_text="Display Name (optional)",
            font=("Consolas", 12))
        self.display_entry.pack(fill="x", padx=14, pady=(0, 8))
        row = ctk.CTkFrame(c1, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=(0, 12))
        ctk.CTkButton(row, text="LOAD AVATAR",
                       font=("Consolas", 11, "bold"),
                       command=self._load_avatar).pack(side="left", padx=(0, 8))
        ctk.CTkButton(row, text="ADD", font=("Consolas", 11, "bold"),
                       width=70, command=self._add_account).pack(side="left")

        c2 = self._card(tab, "AVATAR ITEMS / ACCESSORIES")
        self.avatar_items_box = ctk.CTkTextbox(
            c2, height=80, font=("Consolas", 11), fg_color="#050508")
        self.avatar_items_box.pack(fill="x", padx=14, pady=(0, 6))
        self.avatar_items_box.insert("end", "Load a user to see avatar items.\n")
        self.avatar_items_box.configure(state="disabled")

        self.account_box = ctk.CTkTextbox(
            tab, height=120, font=("Consolas", 11), fg_color="#050508")
        self.account_box.pack(fill="x", padx=26, pady=8)

    # VISUAL
    def _build_visual(self):
        tab = self.tabs.tab("Visual")
        self._tab_header(tab, "VISUAL", "visual")

        c1 = self._card(tab, "THEME")
        self.theme_box = ctk.CTkComboBox(
            c1, values=list(THEMES.keys()),
            command=self.apply_theme, font=("Consolas", 13), width=200)
        self.theme_box.set(self.theme_name)
        self.theme_box.pack(padx=14, pady=(4, 12))

        c2 = self._card(tab, "BACKGROUND IMAGE")
        row = ctk.CTkFrame(c2, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=(4, 12))
        ctk.CTkButton(row, text="BROWSE", font=("Consolas", 11, "bold"),
                       command=self._choose_bg).pack(side="left", padx=(0, 8))
        ctk.CTkButton(row, text="CLEAR", font=("Consolas", 11, "bold"),
                       width=70, command=self._clear_bg).pack(side="left")

        c3 = self._card(tab, "BG OPACITY")
        self.opacity_val = ctk.CTkLabel(
            c3, text=f"{int(self.bg_opacity*100)}%",
            font=("Consolas", 12, "bold"))
        self.opacity_val.pack(anchor="e", padx=20)
        self.opacity_slider = ctk.CTkSlider(
            c3, from_=0.05, to=1.0, command=self._change_opacity)
        self.opacity_slider.set(self.bg_opacity)
        self.opacity_slider.pack(fill="x", padx=20, pady=(0, 14))

        c4 = self._card(tab, "BG BLUR")
        self.blur_val = ctk.CTkLabel(
            c4, text=f"{self.bg_blur}px", font=("Consolas", 12, "bold"))
        self.blur_val.pack(anchor="e", padx=20)
        self.blur_slider = ctk.CTkSlider(
            c4, from_=0, to=20, command=self._change_blur)
        self.blur_slider.set(self.bg_blur)
        self.blur_slider.pack(fill="x", padx=20, pady=(0, 14))

    # SETTINGS
    def _build_settings(self):
        tab = self.tabs.tab("Settings")
        self._tab_header(tab, "SETTINGS", "settings")

        c1 = self._card(tab, "WINDOW")
        self.topmost_switch = self._switch(c1, "Always On Top", self._toggle_topmost)

        c2 = self._card(tab, "DISCORD RICH PRESENCE")
        self.rpc_label = ctk.CTkLabel(
            c2, text="Set CLIENT_ID in source to enable",
            font=("Consolas", 10), text_color="#334155")
        self.rpc_label.pack(anchor="w", padx=14, pady=(0, 10))

        c3 = self._card(tab, "CONFIG")
        row = ctk.CTkFrame(c3, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=(4, 12))
        ctk.CTkButton(row, text="SAVE", font=("Consolas", 11, "bold"),
                       command=self.save_config).pack(side="left", padx=(0, 8))
        ctk.CTkButton(row, text="LOAD", font=("Consolas", 11, "bold"),
                       command=self.load_config).pack(side="left")

    def apply_theme(self, theme):
        if theme not in THEMES:
            return
        self.theme_name = theme
        t = THEMES[theme]
        accent, hover = t["accent"], t["hover"]

        self.configure(fg_color=t["bg"])
        self.sidebar.configure(fg_color="#040407")
        self.tabs.configure(
            fg_color="#06060c",
            segmented_button_selected_color=accent,
            segmented_button_selected_hover_color=hover,
            segmented_button_unselected_color="#0a0a12",
        )
        self.logo_top.configure(text_color=accent)

        for sw in (self.click_switch, self.shift_switch, self.key_switch,
                   self.afk_switch, self.topmost_switch):
            sw.configure(progress_color=accent, button_color="white")

        for sl in (self.cps_slider, self.opacity_slider, self.blur_slider):
            sl.configure(progress_color=accent, button_color=hover,
                         button_hover_color=accent)

        for (ic, key, _) in self._tab_headers:
            ic.configure(bg=t["bg"])
            draw_icon(ic, key, accent, size=30)

        if theme == "RGB" and not self._rgb_running:
            threading.Thread(target=self._rgb_loop, daemon=True).start()

    def _update_cps(self, v):
        self.cps = int(v)
        self.after(0, lambda: self.cps_num.configure(text=str(self.cps)))

    def _sync_click(self):
        self.clicking = bool(self.click_switch.get())
        self._refresh_status()

    def _toggle_shift(self):
        self.shift_spam = bool(self.shift_switch.get())
        self._refresh_status()

    def _toggle_key(self):
        self.key_spam  = bool(self.key_switch.get())
        self.spam_key  = self.key_box.get().strip() or "space"
        self._refresh_status()

    def _apply_spam_key(self):
        self.spam_key = self.key_box.get().strip() or "space"

    def _toggle_afk(self):
        self.afk_mode = bool(self.afk_switch.get())
        self._refresh_status()

    def _toggle_topmost(self):
        self.always_on_top = bool(self.topmost_switch.get())
        self.attributes("-topmost", self.always_on_top)

    def _set_hotkey(self):
        v = self.hotkey_entry.get().strip().lower()
        if v:
            self.hotkey_char = v[0]
            self.after(0, lambda: self.hotkey_label.configure(
                text=f"[ {self.hotkey_char.upper()} ]"))

    def _choose_bg(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.webp")])
        if path:
            self.background_path = path
            threading.Thread(
                target=lambda: self._set_background(path), daemon=True).start()

    def _clear_bg(self):
        self.background_path = None
        blank   = Image.new("RGB", (10, 10), "#050505")
        ctk_img = ctk.CTkImage(light_image=blank, dark_image=blank,
                                size=(self.winfo_width(), self.winfo_height()))
        self.after(0, lambda: self.bg_label.configure(image=ctk_img))

    def _change_opacity(self, v):
        self.bg_opacity = float(v)
        self.after(0, lambda: self.opacity_val.configure(
            text=f"{int(self.bg_opacity*100)}%"))
        if self.background_path:
            threading.Thread(
                target=lambda: self._set_background(self.background_path),
                daemon=True).start()

    def _change_blur(self, v):
        self.bg_blur = int(v)
        self.after(0, lambda: self.blur_val.configure(
            text=f"{self.bg_blur}px"))
        if self.background_path:
            threading.Thread(
                target=lambda: self._set_background(self.background_path),
                daemon=True).start()

    def _refresh_status(self):
        active = [k for k, v in [
            ("CLICK", self.clicking), ("SHIFT", self.shift_spam),
            ("KEY",   self.key_spam), ("AFK",   self.afk_mode)] if v]
        text  = "● " + " · ".join(active) if active else "● IDLE"
        color = THEMES[self.theme_name]["accent"] if active else "#1e3a5f"
        self.after(0, lambda: self.status_label.configure(
            text=text, text_color=color))

    def _add_account(self):
        user    = self.user_entry.get().strip()
        display = self.display_entry.get().strip()
        if user:
            self.account_box.insert("end", f"[{display or user}]  @{user}\n")

    def _load_avatar(self):
        username = self.user_entry.get().strip()
        if username:
            threading.Thread(
                target=self._fetch_avatar, args=(username,), daemon=True).start()

    def _fetch_avatar(self, username):
        try:
            r   = requests.post(
                "https://users.roblox.com/v1/usernames/users",
                json={"usernames": [username], "excludeBannedUsers": True},
                timeout=6)
            uid = r.json()["data"][0]["id"]
            th  = requests.get(
                f"https://thumbnails.roblox.com/v1/users/avatar-headshot"
                f"?userIds={uid}&size=420x420&format=Png&isCircular=false",
                timeout=6).json()
            url = th["data"][0]["imageUrl"]
            img = Image.open(
                BytesIO(requests.get(url, timeout=8).content)).resize(
                (130, 130), Image.LANCZOS)
            ctk_img = ctk.CTkImage(
                light_image=img, dark_image=img, size=(130, 130))

            items_r = requests.get(
                f"https://inventory.roblox.com/v2/users/{uid}"
                f"/inventory?assetTypes=Hat,HairAccessory&limit=10",
                timeout=6)
            items_text = "─── EQUIPPED ITEMS ──────────────────\n"
            try:
                items_data = items_r.json().get("data", [])
                for item in items_data[:8]:
                    items_text += f"  {item.get('assetName','?')}\n"
                if not items_data:
                    items_text += "  (No items or private inventory)\n"
            except Exception:
                items_text += "  (Could not load items)\n"

            def apply():
                self.avatar_label.configure(image=ctk_img, text="")
                self.avatar_label.image = ctk_img
                self.account_box.insert("end", f"Avatar loaded: {username}\n")
                self.avatar_items_box.configure(state="normal")
                self.avatar_items_box.delete("0.0", "end")
                self.avatar_items_box.insert("end", items_text)
                self.avatar_items_box.configure(state="disabled")
            self.after(0, apply)
        except Exception as e:
            print(f"[avatar] {e}")

    def _start_rpc(self):
        if Presence is None:
            return
        CLIENT_ID = "YOUR_DISCORD_CLIENT_ID"
        if CLIENT_ID == "YOUR_DISCORD_CLIENT_ID":
            return
        try:
            self.rpc = Presence(CLIENT_ID)
            self.rpc.connect()
            self.rpc.update(details="AHHH Marco", state="Ultimate Client",
                            start=time.time())
        except Exception as e:
            print(f"[rpc] {e}")

    def save_config(self):
        data = {
            "cps":        self.cps,
            "theme":      self.theme_name,
            "bg_opacity": self.bg_opacity,
            "bg_blur":    self.bg_blur,
            "background": self.background_path,
            "hotkey":     self.hotkey_char,
            "spam_key":   self.spam_key,
            "topmost":    self.always_on_top,
            "region":     self.roblox_region,
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            return
        try:
            with open(CONFIG_FILE, "r") as f:
                d = json.load(f)
        except Exception:
            return

        self.cps           = d.get("cps", 20)
        self.theme_name    = d.get("theme", "Blue")
        self.bg_opacity    = d.get("bg_opacity", 0.35)
        self.bg_blur       = d.get("bg_blur", 0)
        self.hotkey_char   = d.get("hotkey", "f")
        self.spam_key      = d.get("spam_key", "space")
        self.always_on_top = d.get("topmost", False)
        self.roblox_region = d.get("region", "US-East")

        try:
            self.cps_slider.set(self.cps)
            self.opacity_slider.set(self.bg_opacity)
            self.blur_slider.set(self.bg_blur)
            self.theme_box.set(self.theme_name)
            self.hotkey_entry.delete(0, "end")
            self.hotkey_entry.insert(0, self.hotkey_char)
            self.key_box.delete(0, "end")
            self.key_box.insert(0, self.spam_key)
            self.cps_num.configure(text=str(self.cps))
            self.hotkey_label.configure(text=f"[ {self.hotkey_char.upper()} ]")
            self.attributes("-topmost", self.always_on_top)
            if self.always_on_top:
                self.topmost_switch.select()
            if hasattr(self, "region_box"):
                self.region_box.set(self.roblox_region)
        except Exception as e:
            print(f"[load_config widget update] {e}")

        self.apply_theme(self.theme_name)

        bg = d.get("background")
        if bg and os.path.exists(bg):
            self.background_path = bg
            threading.Thread(
                target=lambda: self._set_background(bg), daemon=True).start()

    def _click_engine(self):
        while True:
            if self.clicking:
                ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)
                ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)
                time.sleep(1.0 / max(1, self.cps))
            else:
                time.sleep(0.05)

    def _shift_engine(self):
        while True:
            if self.shift_spam:
                pydirectinput.press("shift")
                time.sleep(0.05)
            else:
                time.sleep(0.05)

    def _key_engine(self):
        while True:
            if self.key_spam:
                try:
                    pydirectinput.press(self.spam_key)
                except Exception:
                    pass
                time.sleep(0.05)
            else:
                time.sleep(0.05)

    def _afk_engine(self):
        while True:
            if self.afk_mode:
                pydirectinput.moveRel(
                    random.randint(-4, 4), random.randint(-4, 4))
                pydirectinput.press("space")
                time.sleep(random.uniform(2.5, 4.0))
            else:
                time.sleep(0.1)

    def _stats_loop(self):
        while True:
            now = time.perf_counter()
            dt  = now - self._last_frame
            self._last_frame = now
            self._frame_times.append(dt)
            if len(self._frame_times) > 30:
                self._frame_times.pop(0)
            avg  = sum(self._frame_times) / len(self._frame_times)
            fps  = int(1.0 / avg) if avg > 0 else 0
            ping = self._get_ping()
            self.after(0, lambda f=fps, p=ping: (
                self.fps_label.configure(text=f"FPS  {f}"),
                self.ping_label.configure(text=f"PING {p}ms"),
            ))
            time.sleep(1)

    def _get_ping(self):
        try:
            t0 = time.perf_counter()
            socket.create_connection(("1.1.1.1", 80), timeout=1).close()
            return int((time.perf_counter() - t0) * 1000)
        except Exception:
            return 999

    def _rgb_loop(self):
        self._rgb_running = True
        palette = ["#ff0044", "#ff6600", "#ffee00",
                   "#00ff88", "#00ccff", "#8800ff", "#ff0099"]
        idx = 0
        while self.theme_name == "RGB":
            c = palette[idx % len(palette)]
            idx += 1
            self.after(0, lambda col=c: self._rgb_tick(col))
            time.sleep(0.18)
        self._rgb_running = False

    def _rgb_tick(self, color):
        try:
            self.logo_top.configure(text_color=color)
            self.tabs.configure(segmented_button_selected_color=color)
            for sw in (self.click_switch, self.shift_switch, self.key_switch,
                       self.afk_switch, self.topmost_switch):
                sw.configure(progress_color=color)
            for sl in (self.cps_slider, self.opacity_slider, self.blur_slider):
                sl.configure(progress_color=color)
        except Exception:
            pass

    def _fade_in(self, step):
        try:
            self.attributes("-alpha", min(step / 32, 1.0))
        except Exception:
            pass
        if step < 32:
            self.after(14, lambda: self._fade_in(step + 1))

    def _on_key(self, key):
        try:
            ch = key.char.lower() if hasattr(key, "char") and key.char else None
            if ch == self.hotkey_char:
                if self.clicking:
                    self.after(0, self.click_switch.deselect)
                else:
                    self.after(0, self.click_switch.select)
                self.after(0, self._sync_click)
        except Exception:
            pass

# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT WITH KEY SYSTEM
# ─────────────────────────────────────────────────────────────────────────────

def start_app():
    app = AHHHMarco()
    SplashScreen(master=app, on_done=app.show_after_splash)
    app.mainloop()

if __name__ == "__main__":
    key_gate = KeyWindow(on_success=start_app)
    key_gate.mainloop()