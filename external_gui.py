"""
Harici Sistem İzleyici v4.1 (Stable Premium)
============================================
Sadece eğitim amaçlıdır (Educational use only).
"""

import sys
import threading
import queue
import time
import random
import math
import os
import ctypes
import webbrowser
from datetime import datetime

import tkinter
import customtkinter
from PIL import Image, ImageTk

# Çekirdek Kütüphaneler
import cv2
import numpy as np
import mss

# ============================================
# ULTRA PREMIUM PALETTE
# ============================================
C_BG_MAIN = "#0b0c15"       
C_SIDEBAR = "#11121c"       
C_CARD    = "#1a1b26"       
C_ACCENT  = "#7aa2f7"       
C_DANGER  = "#f7768e"       
C_SUCCESS = "#9ece6a"       
C_TEXT    = "#c0caf5"       
C_TEXT_DIM= "#565f89"       

# ============================================
# HELPER FUNCTIONS & CLASSES
# ============================================
def _junk_math():
    return math.sqrt(random.random()) * math.sin(random.random())

class _ServiceWorker:
    def __init__(self):
        self.mem = []
    def _allocate(self):
        self.mem.append(random.getrandbits(128))

def set_random_title(app_root):
    titles = [
        "System Monitor", "Background Service", "Task Executor", 
        "Runtime Broker", "Service Host", "DirectX Diagnostics"
    ]
    while True:
        try:
            if random.random() < 0.2:
                title = "svc_" + "".join(random.choices("0123456789ABCDEF", k=8))
            else:
                title = random.choice(titles)
            ctypes.windll.kernel32.SetConsoleTitleW(title)
            _junk_math()
            time.sleep(random.uniform(5.0, 30.0))
        except:
            pass

# Inputs
user32 = ctypes.windll.user32
keybd_event = user32.keybd_event
mouse_event = user32.mouse_event
SetCursorPos = user32.SetCursorPos
GetSystemMetrics = user32.GetSystemMetrics

VK_SPACE, SCAN_SPACE = 0x20, 0x39
VK_E, SCAN_E = 0x45, 0x12

def input_key(vk, scan, down=True):
    flag = 0 if down else 2
    keybd_event(vk, scan, flag, 0)

def click(x, y):
    SetCursorPos(int(x), int(y))
    time.sleep(0.05)
    mouse_event(0x0008, 0, 0, 0, 0)
    time.sleep(0.03)
    mouse_event(0x0010, 0, 0, 0, 0)
    time.sleep(0.05)
    mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.03)
    mouse_event(0x0004, 0, 0, 0, 0)

def rotate_cam():
    input_key(VK_E, SCAN_E, True)
    time.sleep(0.6)
    input_key(VK_E, SCAN_E, False)

# Vision
class VisionEngine:
    def __init__(self):
        self.template_target = None
        self.target_gray = None
        self.boss_templates = []
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1]
        
    def load_assets(self):
        if os.path.exists("target.png"):
            self.template_target = cv2.imread("target.png")
            if self.template_target is not None:
                self.target_gray = cv2.cvtColor(self.template_target, cv2.COLOR_BGR2GRAY)
        
        self.boss_templates = []
        i = 1
        while os.path.exists(f"elite{i}.png"):
            t = cv2.imread(f"elite{i}.png")
            if t is not None:
                g = cv2.cvtColor(t, cv2.COLOR_BGR2GRAY)
                self.boss_templates.append((f"elite{i}", t, g))
            i += 1
        return self.template_target is not None, len(self.boss_templates)

    def grab_screen(self):
        try:
            raw = np.array(self.sct.grab(self.monitor))
            return cv2.cvtColor(raw, cv2.COLOR_BGRA2BGR)
        except:
            return None

    def find_matches(self, scene_gray, template, thresh=0.55):
        if template is None: return []
        res = cv2.matchTemplate(scene_gray, template, cv2.TM_CCOEFF_NORMED)
        locs = np.where(res >= thresh)
        th, tw = template.shape[:2]
        candidates = [(pt[0] + tw//2, pt[1] + th//2, res[pt[1], pt[0]]) for pt in zip(*locs[::-1])]
        final = []
        for c in sorted(candidates, key=lambda x: -x[2]):
            if not any(abs(c[0]-f[0]) < 20 and abs(c[1]-f[1]) < 20 for f in final):
                final.append(c)
        return final

class WorkerThread(threading.Thread):
    def __init__(self, log_queue, status_callback, config):
        super().__init__()
        self.log_queue = log_queue
        self.status = status_callback
        self.config = config
        self.running = False
        self.paused = True
        self.daemon = True
        self.vision = VisionEngine()
        
    def log(self, msg):
        self.log_queue.put(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    def run(self):
        loaded, n_boss = self.vision.load_assets()
        if not loaded:
            self.log("HATA: target.png eksik!")
            self.status("Durum: Hata")
            return
        
        self.log(f"Sistem Hazır. Hedefler: {n_boss+1}")
        cx, cy = GetSystemMetrics(0) // 2, GetSystemMetrics(1) // 2
        offset = int(self.config.get('offset', 80))
        thresh = float(self.config.get('threshold', 0.55))
        delay = float(self.config.get('delay', 1.0))
        
        while self.running:
            if self.paused:
                time.sleep(0.2); continue
            try:
                frame = self.vision.grab_screen()
                if frame is None: continue
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Boss
                boss_found = False
                for _, _, b_gray in self.vision.boss_templates:
                    if self.vision.find_matches(gray, b_gray, 0.75):
                        boss_found = True; break
                
                if boss_found:
                    self.log(">> ELİT BULUNDU"); self.status("ELİT SAVAŞI")
                    input_key(VK_SPACE, SCAN_SPACE, True)
                    for _ in range(150):
                        time.sleep(2)
                        if self.paused or not self.running: break
                        f2 = self.vision.grab_screen()
                        if f2 and not any(self.vision.find_matches(cv2.cvtColor(f2, cv2.COLOR_BGR2GRAY), bg, 0.75) for _, _, bg in self.vision.boss_templates):
                            self.log(">> Elit Temizlendi"); break
                    input_key(VK_SPACE, SCAN_SPACE, False)
                    self.status("ARANIYOR")
                    continue
                
                # Target
                targets = self.vision.find_matches(gray, self.vision.target_gray, thresh)
                if targets:
                    valid = [t for t in targets if (t[0]-cx)**2 + (t[1]-cy)**2 > 80**2]
                    if valid:
                        best = min(valid, key=lambda t: (t[0]-cx)**2 + (t[1]-cy)**2)
                        tx, ty = best[0], best[1] + offset
                        self.log(f"Hedef -> ({tx}, {ty})"); self.status("SALDIRI")
                        click(tx, ty)
                        time.sleep(delay)
                    else:
                        rotate_cam()
                else:
                    self.status("TARAMA"); rotate_cam()
                time.sleep(0.1)
            except Exception as e:
                self.log(f"Hata: {e}"); time.sleep(1)

# ============================================
# GUI APPLICATION
# ============================================
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        # 1. Window Config
        self.title("MT2 MACRO Pro")
        self.geometry("950x600")
        self.configure(fg_color=C_BG_MAIN)
        
        # Center Window safely
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = max(0, (sw - 950) // 2)
        y = max(0, (sh - 600) // 2)
        self.geometry(f"950x600+{x}+{y}")

        # 2. Custom Title Bar
        self.overrideredirect(True) # Remove system decoration
        
        self.title_bar = customtkinter.CTkFrame(self, corner_radius=0, fg_color=C_SIDEBAR, height=35)
        self.title_bar.pack(fill="x", side="top")
        self.title_bar.bind("<ButtonPress-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)
        
        t_lbl = customtkinter.CTkLabel(self.title_bar, text="  MT2 MACRO  |  v4.1 Pro", font=("Segoe UI", 11, "bold"), text_color=C_TEXT_DIM)
        t_lbl.pack(side="left", padx=10)
        t_lbl.bind("<ButtonPress-1>", self.start_move)
        t_lbl.bind("<B1-Motion>", self.do_move)
        
        # Exit Button
        customtkinter.CTkButton(
            self.title_bar, text="✕", width=40, font=("Arial", 14), 
            fg_color="transparent", hover_color=C_DANGER, command=self.close_app
        ).pack(side="right")
        
        # Minimize Button (Simplified: just iconify, might need taskbar fix but okay for now)
        customtkinter.CTkButton(
            self.title_bar, text="—", width=40, font=("Arial", 14),
            fg_color="transparent", hover_color="#333", command=self.iconify
        ).pack(side="right")

        # 3. Main Layout
        self.main_container = customtkinter.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)
        self.main_container.grid_columnconfigure(1, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = customtkinter.CTkFrame(self.main_container, width=240, corner_radius=0, fg_color=C_SIDEBAR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(5, weight=1)
        
        # Branding
        customtkinter.CTkLabel(self.sidebar, text="∞", font=("Arial", 60), text_color=C_ACCENT).grid(row=0, column=0, pady=(20,0))
        customtkinter.CTkLabel(self.sidebar, text="UNLEASHED", font=("Segoe UI", 12, "bold"), text_color=C_TEXT).grid(row=1, column=0, pady=(0,30))
        
        # Nav Buttons
        self.menu_buttons = []
        self.add_menu_btn("Dashboard", "⏱", self.show_dashboard, 2)
        self.add_menu_btn("Settings", "⚙", self.show_settings, 3)
        self.add_menu_btn("Info", "ℹ", self.show_info, 4)
        
        # User Tag
        p_frame = customtkinter.CTkFrame(self.sidebar, fg_color="#0f1019", corner_radius=8)
        p_frame.grid(row=6, column=0, padx=20, pady=20, sticky="ew")
        customtkinter.CTkLabel(p_frame, text="GuvenAda", font=("Segoe UI", 12, "bold"), text_color=C_ACCENT).pack(side="left", padx=10, pady=10)
        customtkinter.CTkLabel(p_frame, text="PRO", font=("Segoe UI", 10, "bold"), text_color=C_BG_MAIN, fg_color=C_ACCENT, corner_radius=4).pack(side="right", padx=10)

        # Content Area
        self.content = customtkinter.CTkFrame(self.main_container, corner_radius=0, fg_color=C_BG_MAIN)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)
        
        # Pages
        self.f_dash = customtkinter.CTkFrame(self.content, fg_color="transparent")
        self.f_set = customtkinter.CTkFrame(self.content, fg_color="transparent")
        self.f_info = customtkinter.CTkFrame(self.content, fg_color="transparent")
        
        self.init_dashboard()
        self.init_settings()
        self.init_info()
        
        self.show_dashboard()
        
        # Logic
        self.log_queue = queue.Queue()
        self.worker = None
        self.is_running = False
        threading.Thread(target=set_random_title, args=(self,), daemon=True).start()
        self.after(100, self.update_logs)
        
        # Force Visibility
        self.lift()
        self.focus_force()

    def start_move(self, event):
        self.x, self.y = event.x, event.y

    def do_move(self, event):
        x = self.winfo_x() + event.x - self.x
        y = self.winfo_y() + event.y - self.y
        self.geometry(f"+{x}+{y}")

    def close_app(self):
        self.destroy()
        sys.exit()

    def add_menu_btn(self, text, icon, cmd, r):
        btn = customtkinter.CTkButton(
            self.sidebar, text=f"  {icon}  {text}", anchor="w",
            font=("Segoe UI", 14), fg_color="transparent", text_color=C_TEXT_DIM,
            hover_color="#1f2335", height=50, corner_radius=0, command=cmd
        )
        btn.grid(row=r, column=0, sticky="ew")
        self.menu_buttons.append(btn)
        return btn

    def set_active_btn(self, index):
        for i, btn in enumerate(self.menu_buttons):
            if i == index:
                btn.configure(fg_color="#1f2335", text_color=C_ACCENT)
            else:
                btn.configure(fg_color="transparent", text_color=C_TEXT_DIM)

    def init_dashboard(self):
        f = self.f_dash
        f.grid_columnconfigure(0, weight=1); f.grid_columnconfigure(1, weight=1)
        
        # Stats
        c_stat = customtkinter.CTkFrame(f, fg_color=C_CARD, corner_radius=15)
        c_stat.grid(row=0, column=0, columnspan=2, sticky="ew", padx=40, pady=(40, 20))
        
        customtkinter.CTkLabel(c_stat, text="SYSTEM STATUS", font=("Segoe UI", 12, "bold"), text_color=C_TEXT_DIM).pack(pady=(15,5), padx=20, anchor="w")
        self.lbl_status = customtkinter.CTkLabel(c_stat, text="READY", font=("Segoe UI", 20, "bold"), text_color=C_SUCCESS)
        self.lbl_status.pack(pady=(0,15), padx=20, anchor="w")
        
        self.btn_run = customtkinter.CTkButton(
            c_stat, text="ENGAGE PROTOCOL", font=("Segoe UI", 14, "bold"), height=50,
            fg_color=C_ACCENT, text_color=C_BG_MAIN, hover_color="#fff", corner_radius=8,
            command=self.toggle_power
        )
        self.btn_run.pack(side="right", padx=20, pady=20)
        
        # Logs
        self.log_box = customtkinter.CTkTextbox(f, fg_color=C_CARD, text_color="#a9b1d6", font=("Consolas", 11), corner_radius=10)
        self.log_box.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=40, pady=(0,20))
        self.log_box.insert("0.0", ">> System module loaded.\n")
        self.log_box.configure(state="disabled")

        # Actions
        f_act = customtkinter.CTkFrame(f, fg_color="transparent")
        f_act.grid(row=2, column=0, columnspan=2, padx=40, pady=(0,40), sticky="ew")
        customtkinter.CTkButton(f_act, text="Capture Target", fg_color=C_CARD, hover_color="#292e42", command=lambda: self.capture("target")).pack(side="left", expand=True, fill="x", padx=(0,10))
        customtkinter.CTkButton(f_act, text="Capture Elite", fg_color=C_CARD, hover_color="#292e42", command=lambda: self.capture("elite", True)).pack(side="left", expand=True, fill="x", padx=(10,0))

    def init_settings(self):
        f = self.f_set
        customtkinter.CTkLabel(f, text="Configuration", font=("Segoe UI", 26, "bold"), text_color=C_TEXT).pack(anchor="w", padx=40, pady=(40,20))
        self.slider_card(f, "Sensitivity", 0.1, 1.0, 0.55, "thresh")
        self.slider_card(f, "Offset", 0, 200, 80, "offset")
        self.slider_card(f, "Delay", 0.1, 5.0, 1.0, "delay")

    def slider_card(self, parent, title, min_v, max_v, def_v, tag):
        c = customtkinter.CTkFrame(parent, fg_color=C_CARD, corner_radius=10)
        c.pack(fill="x", padx=40, pady=10)
        customtkinter.CTkLabel(c, text=title, font=("Segoe UI", 12, "bold"), text_color=C_TEXT).pack(pady=(15,5), padx=20, anchor="w")
        sl = customtkinter.CTkSlider(c, from_=min_v, to=max_v, number_of_steps=100, progress_color=C_ACCENT, button_color=C_TEXT, button_hover_color=C_ACCENT)
        sl.set(def_v)
        sl.pack(fill="x", padx=20, pady=(0,10))
        lbl = customtkinter.CTkLabel(c, text=str(def_v), text_color=C_TEXT_DIM)
        lbl.pack(padx=20, pady=(0,15), anchor="e")
        sl.configure(command=lambda v: lbl.configure(text=f"{v:.2f}"))
        setattr(self, f"sl_{tag}", sl)

    def init_info(self):
        f = self.f_info
        customtkinter.CTkLabel(f, text="Information", font=("Segoe UI", 26, "bold"), text_color=C_TEXT).pack(anchor="w", padx=40, pady=(40,20))
        c = customtkinter.CTkFrame(f, fg_color=C_CARD, corner_radius=15)
        c.pack(fill="both", expand=True, padx=40, pady=0)
        customtkinter.CTkLabel(c, text="MT2 MACRO", font=("Segoe UI", 40, "bold"), text_color=C_ACCENT).pack(pady=(60,10))
        customtkinter.CTkLabel(c, text="v4.1.0 Premium", font=("Consolas", 12), text_color=C_TEXT_DIM).pack()
        customtkinter.CTkButton(c, text="GitHub", fg_color=C_SIDEBAR, hover_color="#222", command=lambda: webbrowser.open("https://github.com/guvenada")).pack(pady=40)

    def show_dashboard(self):
        self.f_set.pack_forget(); self.f_info.pack_forget()
        self.f_dash.pack(fill="both", expand=True)
        self.set_active_btn(0)

    def show_settings(self):
        self.f_dash.pack_forget(); self.f_info.pack_forget()
        self.f_set.pack(fill="both", expand=True)
        self.set_active_btn(1)

    def show_info(self):
        self.f_dash.pack_forget(); self.f_set.pack_forget()
        self.f_info.pack(fill="both", expand=True)
        self.set_active_btn(2)

    def update_logs(self):
        while not self.log_queue.empty():
            msg = self.log_queue.get()
            self.log_box.configure(state="normal")
            self.log_box.insert("end", msg + "\n")
            self.log_box.see("end")
            self.log_box.configure(state="disabled")
        self.after(100, self.update_logs)

    def toggle_power(self):
        if not self.is_running:
            self.is_running = True
            self.btn_run.configure(text="TERMINATE", fg_color=C_DANGER)
            self.lbl_status.configure(text="RUNNING", text_color=C_ACCENT)
            cfg = {'threshold': self.sl_thresh.get(), 'offset': self.sl_offset.get(), 'delay': self.sl_delay.get()}
            self.worker = WorkerThread(self.log_queue, lambda t: None, cfg)
            self.worker.running = True; self.worker.paused = False; self.worker.start()
        else:
            self.is_running = False
            self.btn_run.configure(text="ENGAGE PROTOCOL", fg_color=C_ACCENT)
            self.lbl_status.configure(text="READY", text_color=C_SUCCESS)
            if self.worker: self.worker.running = False

    def capture(self, name, sub=False):
        self.log_queue.put(f"[{datetime.now().strftime('%H:%M:%S')}] Snapshot in 3s...")
        self.after(3000, lambda: self._cap(name, sub))

    def _cap(self, name, sub):
        with mss.mss() as sct:
            raw = np.array(sct.grab(sct.monitors[1]))
            img = cv2.cvtColor(raw, cv2.COLOR_BGRA2BGR)
        fname = name
        if sub:
            i = 1
            while os.path.exists(f"{name}{i}.png"): i += 1
            fname = f"{name}{i}"
        cv2.imwrite(f"{fname}.png", img)
        self.log_queue.put(f"[{datetime.now().strftime('%H:%M:%S')}] Saved: {fname}")
        try: os.startfile(os.path.abspath(f"{fname}.png")) 
        except: pass

if __name__ == "__main__":
    app = App()
    app.mainloop()
