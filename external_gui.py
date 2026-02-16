"""
Harici Sistem İzleyici v4.2 (Ultra-Premium + RGB Splash)
========================================================
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
import colorsys
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

def set_random_title(app_root):
    titles = ["System Monitor", "Background Service", "Service Host", "DirectX Diagnostics"]
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

class _ServiceWorker:
    def __init__(self): self.mem = []
    def _allocate(self): self.mem.append(random.getrandbits(128))

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
    time.sleep(0.05); mouse_event(0x0008, 0, 0, 0, 0)
    time.sleep(0.03); mouse_event(0x0010, 0, 0, 0, 0)
    time.sleep(0.05); mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.03); mouse_event(0x0004, 0, 0, 0, 0)

def rotate_cam():
    input_key(VK_E, SCAN_E, True); time.sleep(0.6); input_key(VK_E, SCAN_E, False)

# Vision
class VisionEngine:
    def __init__(self):
        self.template_target = None; self.boss_templates = []
        self.sct = mss.mss(); self.monitor = self.sct.monitors[1]
        if os.path.exists("target.png"):
            self.template_target = cv2.imread("target.png")
            if self.template_target is not None:
                self.target_gray = cv2.cvtColor(self.template_target, cv2.COLOR_BGR2GRAY)
        i = 1
        while os.path.exists(f"elite{i}.png"):
            t = cv2.imread(f"elite{i}.png")
            if t is not None:
                self.boss_templates.append((f"elite{i}", t, cv2.cvtColor(t, cv2.COLOR_BGR2GRAY)))
            i += 1

    def grab_screen(self):
        try: return cv2.cvtColor(np.array(self.sct.grab(self.monitor)), cv2.COLOR_BGRA2BGR)
        except: return None

    def find_matches(self, scene_gray, template, thresh=0.55):
        if template is None: return []
        res = cv2.matchTemplate(scene_gray, template, cv2.TM_CCOEFF_NORMED)
        locs = np.where(res >= thresh)
        th, tw = template.shape[:2]
        candidates = [(pt[0] + tw//2, pt[1] + th//2, res[pt[1], pt[0]]) for pt in zip(*locs[::-1])]
        final = []
        for c in sorted(candidates, key=lambda x: -x[2]):
            if not any(abs(c[0]-f[0]) < 20 and abs(c[1]-f[1]) < 20 for f in final): final.append(c)
        return final

class WorkerThread(threading.Thread):
    def __init__(self, log_queue, status_callback, config):
        super().__init__(); self.log_queue = log_queue; self.status = status_callback; self.config = config; self.running = False; self.paused = True; self.daemon = True; self.vision = VisionEngine()
    def log(self, msg): self.log_queue.put(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    def run(self):
        if self.vision.template_target is None: self.log("Error: target.png missing!"); return
        self.log(f"System Ready. Elites: {len(self.vision.boss_templates)}")
        cx, cy = GetSystemMetrics(0) // 2, GetSystemMetrics(1) // 2
        offset = int(self.config.get('offset', 80)); thresh = float(self.config.get('threshold', 0.55)); delay = float(self.config.get('delay', 1.0))
        while self.running:
            if self.paused: time.sleep(0.2); continue
            try:
                frame = self.vision.grab_screen()
                if frame is None: continue
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                boss_found = False
                for _, _, b_gray in self.vision.boss_templates:
                    if self.vision.find_matches(gray, b_gray, 0.75): boss_found = True; break
                if boss_found:
                    self.log(">> ELITE DETECTED"); self.status("COMBAT MODE")
                    input_key(VK_SPACE, SCAN_SPACE, True)
                    for _ in range(150):
                        time.sleep(2); 
                        if self.paused or not self.running: break
                        f2 = self.vision.grab_screen()
                        if f2 and not any(self.vision.find_matches(cv2.cvtColor(f2, cv2.COLOR_BGR2GRAY), bg, 0.75) for _, _, bg in self.vision.boss_templates): self.log(">> Elite Cleared"); break
                    input_key(VK_SPACE, SCAN_SPACE, False); self.status("SEARCHING"); continue
                targets = self.vision.find_matches(gray, self.vision.template_target and self.vision.target_gray, thresh)
                valid = [t for t in targets if (t[0]-cx)**2 + (t[1]-cy)**2 > 80**2] if targets else []
                if valid:
                    best = min(valid, key=lambda t: (t[0]-cx)**2 + (t[1]-cy)**2)
                    self.log(f"Target -> {best[:2]}"); self.status("ATTACKING"); click(best[0], best[1] + offset); time.sleep(delay)
                else: self.status("SCANNING"); rotate_cam()
                time.sleep(0.1)
            except Exception as e: self.log(f"Error: {e}"); time.sleep(1)

# ============================================
# SPLASH SCREEN (RGB + SMOOTH)
# ============================================
class SplashScreen(customtkinter.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.geometry("400x250")
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.attributes('-alpha', 0.0)
        self.wm_attributes("-transparentcolor", "#000001")
        self.configure(fg_color="#000001")
        
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"+{(sw-400)//2}+{(sh-250)//2}")
        
        # RGB Border Frame
        self.rgb_hue = 0.0
        self.border_frame = customtkinter.CTkFrame(self, bg_color="#000001", corner_radius=20, border_width=3)
        self.border_frame.pack(fill="both", expand=True)
        
        # Inner Content
        self.inner = customtkinter.CTkFrame(self.border_frame, fg_color=C_BG_MAIN, corner_radius=17, border_width=0)
        self.inner.pack(fill="both", expand=True, padx=3, pady=3)
        
        # Logo Text
        customtkinter.CTkLabel(self.inner, text="MT2 MACRO", font=("Segoe UI", 40, "bold"), text_color="white").pack(pady=(60, 5))
        customtkinter.CTkLabel(self.inner, text="UNLEASHED PROTOCOL", font=("Segoe UI", 10, "bold"), text_color=C_ACCENT).pack(pady=0)
        
        # Loading Bar
        self.progress = customtkinter.CTkProgressBar(self.inner, width=200, height=4, progress_color=C_ACCENT, fg_color="#222")
        self.progress.pack(pady=40)
        self.progress.set(0)
        
        self.animate_rgb()
        self.fade_in()

    def animate_rgb(self):
        try:
            self.rgb_hue += 0.02
            if self.rgb_hue > 1.0: self.rgb_hue = 0.0
            rgb = colorsys.hsv_to_rgb(self.rgb_hue, 1.0, 1.0)
            color = "#%02x%02x%02x" % (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
            self.border_frame.configure(border_color=color)
            self.after(20, self.animate_rgb)
        except: pass

    def fade_in(self):
        try:
            alpha = self.attributes('-alpha')
            if alpha < 1.0:
                self.attributes('-alpha', alpha + 0.05)
                self.after(20, self.fade_in)
            else:
                self.load_modules()
        except: self.destroy()

    def load_modules(self):
        try:
            val = self.progress.get()
            if val < 1.0:
                self.progress.set(val + 0.015)
                self.after(10, self.load_modules) # Smooth loading simulation
            else:
                self.fade_out()
        except: self.destroy()
            
    def fade_out(self):
        try:
            alpha = self.attributes('-alpha')
            if alpha > 0.0:
                self.attributes('-alpha', alpha - 0.05)
                self.after(20, self.fade_out)
            else:
                self.destroy()
                self.master.deiconify() # Show main app
                self.master.lift()
                self.master.focus_force()
        except: 
            self.destroy()
            self.master.deiconify()

# ============================================
# MAIN APPLICATION
# ============================================
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        # Setup Main Window (Hidden initially)
        self.withdraw() 
        self.title("MT2 MACRO Pro")
        self.geometry("950x600")
        self.configure(fg_color=C_BG_MAIN)
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"950x600+{max(0, (sw-950)//2)}+{max(0, (sh-600)//2)}")

        # Custom Title Bar
        self.overrideredirect(True)
        self.title_bar = customtkinter.CTkFrame(self, corner_radius=0, fg_color=C_SIDEBAR, height=35)
        self.title_bar.pack(fill="x", side="top")
        self.title_bar.bind("<ButtonPress-1>", self.start_move); self.title_bar.bind("<B1-Motion>", self.do_move)
        
        # Title Content
        t_lbl = customtkinter.CTkLabel(self.title_bar, text="  MT2 MACRO  |  v4.2 Pro", font=("Segoe UI", 11, "bold"), text_color=C_TEXT_DIM)
        t_lbl.pack(side="left", padx=10)
        t_lbl.bind("<ButtonPress-1>", self.start_move); t_lbl.bind("<B1-Motion>", self.do_move)
        
        # Buttons
        customtkinter.CTkButton(self.title_bar, text="✕", width=40, font=("Arial", 14), fg_color="transparent", hover_color=C_DANGER, command=self.close_app).pack(side="right")
        customtkinter.CTkButton(self.title_bar, text="—", width=40, font=("Arial", 14), fg_color="transparent", hover_color="#333", command=self.minimize_window).pack(side="right")

        # Layout
        self.main_container = customtkinter.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)
        self.main_container.grid_columnconfigure(1, weight=1); self.main_container.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = customtkinter.CTkFrame(self.main_container, width=240, corner_radius=0, fg_color=C_SIDEBAR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(5, weight=1)
        
        customtkinter.CTkLabel(self.sidebar, text="∞", font=("Arial", 60), text_color=C_ACCENT).grid(row=0, column=0, pady=(20,0))
        
        self.menu_buttons = []
        self.add_menu_btn("Dashboard", "⏱", "dash", 2)
        self.add_menu_btn("Settings", "⚙", "set", 3)
        self.add_menu_btn("Info", "ℹ", "info", 4)
        
        p_frame = customtkinter.CTkFrame(self.sidebar, fg_color="#0f1019", corner_radius=8)
        p_frame.grid(row=6, column=0, padx=20, pady=20, sticky="ew")
        customtkinter.CTkLabel(p_frame, text="Developer Account", font=("Segoe UI", 12, "bold"), text_color=C_ACCENT).pack(side="left", padx=10, pady=10)

        # Content Zone (Using PLACE for animations)
        self.content_area = customtkinter.CTkFrame(self.main_container, corner_radius=0, fg_color=C_BG_MAIN)
        self.content_area.grid(row=0, column=1, sticky="nsew")
        
        # Initialize Pages
        self.frames = {}
        for name in ["dash", "set", "info"]:
            f = customtkinter.CTkFrame(self.content_area, fg_color="transparent")
            self.frames[name] = f
            if name == "dash": self.init_dashboard(f)
            elif name == "set": self.init_settings(f)
            elif name == "info": self.init_info(f)
        
        self.current_frame = None
        self.show_frame("dash") # Initial show
        
        # System
        self.log_queue = queue.Queue()
        self.worker = None; self.is_running = False
        threading.Thread(target=set_random_title, args=(self,), daemon=True).start()
        self.after(100, self.update_logs)
        
        # Launch Splash
        self.after(100, lambda: SplashScreen(self))

    def set_app_window(self):
        GWL_EXSTYLE = -20
        WS_EX_APPWINDOW = 0x00040000
        WS_EX_TOOLWINDOW = 0x00000080
        hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        style = style & ~WS_EX_TOOLWINDOW
        style = style | WS_EX_APPWINDOW
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        self.wm_withdraw()
        self.after(10, lambda: self.wm_deiconify())

    def start_move(self, event): self.x, self.y = event.x, event.y
    def do_move(self, event): self.geometry(f"+{self.winfo_x() + event.x - self.x}+{self.winfo_y() + event.y - self.y}")
    def close_app(self): self.destroy(); sys.exit()
    def minimize_window(self):
        # With WS_EX_APPWINDOW, iconify works better, but we stick to safe hide/show
        self.withdraw()
        self.overrideredirect(False)
        self.iconify()
        self.bind("<FocusIn>", self.restore_window)
        
    def restore_window(self, event):
        self.overrideredirect(True)
        self.set_app_window() # Re-apply style on restore
        self.unbind("<FocusIn>")
        self.lift()

    # --- Navigation with Fade Animation ---
    def add_menu_btn(self, text, icon, name, r):
        btn = customtkinter.CTkButton(self.sidebar, text=f"  {icon}  {text}", anchor="w", font=("Segoe UI", 14), 
                                      fg_color="transparent", text_color=C_TEXT_DIM, hover_color="#1f2335", 
                                      height=50, corner_radius=0, command=lambda: self.show_frame(name))
        btn.grid(row=r, column=0, sticky="ew")
        btn.name = name
        self.menu_buttons.append(btn)

    def show_frame(self, name):
        if self.current_frame == name: return
        
        # Update buttons
        for btn in self.menu_buttons:
            if btn.name == name: btn.configure(fg_color="#1f2335", text_color=C_ACCENT)
            else: btn.configure(fg_color="transparent", text_color=C_TEXT_DIM)
            
        new_f = self.frames[name]
        old_f = self.frames[self.current_frame] if self.current_frame else None
        
        # Slide Animation
        if old_f:
            self.animate_slide(old_f, new_f)
        else:
            new_f.place(x=0, y=0, relwidth=1, relheight=1)
        
        self.current_frame = name

    def animate_slide(self, f1, f2):
        # f1 slides out left, f2 slides in from right
        f2.place(x=950, y=0, relwidth=1, relheight=1)
        f2.lift()
        
        def _step(i):
            if i >= 101:
                f1.place_forget()
                f2.place(x=0, y=0, relwidth=1, relheight=1)
                return
            
            # Easing function (ease out)
            p = 1 - math.pow(1 - i/100, 3)
            
            offset_x = int(950 * p)
            f2.place(x=950-offset_x, y=0)
            # f1.place(x=-offset_x, y=0) # Optional: Slide old out too, but overlapping is safer for perf
            
            self.after(5, lambda: _step(i+4))
            
        _step(0)

    # --- Pages ---
    def init_dashboard(self, f):
        f.grid_columnconfigure(0, weight=1); f.grid_columnconfigure(1, weight=1)
        c_stat = customtkinter.CTkFrame(f, fg_color=C_CARD, corner_radius=15)
        c_stat.grid(row=0, column=0, columnspan=2, sticky="ew", padx=40, pady=(40, 20))
        customtkinter.CTkLabel(c_stat, text="SYSTEM STATUS", font=("Segoe UI", 12, "bold"), text_color=C_TEXT_DIM).pack(pady=(15,5), padx=20, anchor="w")
        self.lbl_status = customtkinter.CTkLabel(c_stat, text="READY", font=("Segoe UI", 20, "bold"), text_color=C_SUCCESS)
        self.lbl_status.pack(pady=(0,15), padx=20, anchor="w")
        self.btn_run = customtkinter.CTkButton(c_stat, text="ENGAGE PROTOCOL", font=("Segoe UI", 14, "bold"), height=50, fg_color=C_ACCENT, text_color=C_BG_MAIN, hover_color="#fff", corner_radius=8, command=self.toggle_power)
        self.btn_run.pack(side="right", padx=20, pady=20)
        
        self.log_box = customtkinter.CTkTextbox(f, fg_color=C_CARD, text_color="#a9b1d6", font=("Consolas", 11), corner_radius=10)
        self.log_box.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=40, pady=(0,20))
        self.log_box.insert("0.0", ">> System Init...\n"); self.log_box.configure(state="disabled")
        
        f_act = customtkinter.CTkFrame(f, fg_color="transparent")
        f_act.grid(row=2, column=0, columnspan=2, padx=40, pady=(0,40), sticky="ew")
        customtkinter.CTkButton(f_act, text="Capture Target", fg_color=C_CARD, hover_color="#292e42", command=lambda: self.capture("target")).pack(side="left", expand=True, fill="x", padx=(0,10))
        customtkinter.CTkButton(f_act, text="Capture Elite", fg_color=C_CARD, hover_color="#292e42", command=lambda: self.capture("elite", True)).pack(side="left", expand=True, fill="x", padx=(10,0))

    def init_settings(self, f):
        customtkinter.CTkLabel(f, text="Configuration", font=("Segoe UI", 26, "bold"), text_color=C_TEXT).pack(anchor="w", padx=40, pady=(40,20))
        self.slider_card(f, "Sensitivity", 0.1, 1.0, 0.55, "thresh")
        self.slider_card(f, "Offset", 0, 200, 80, "offset")
        self.slider_card(f, "Delay", 0.1, 5.0, 1.0, "delay")

    def slider_card(self, parent, title, min_v, max_v, def_v, tag):
        c = customtkinter.CTkFrame(parent, fg_color=C_CARD, corner_radius=10)
        c.pack(fill="x", padx=40, pady=10)
        customtkinter.CTkLabel(c, text=title, font=("Segoe UI", 12, "bold"), text_color=C_TEXT).pack(pady=(15,5), padx=20, anchor="w")
        sl = customtkinter.CTkSlider(c, from_=min_v, to=max_v, number_of_steps=100, progress_color=C_ACCENT, button_color=C_TEXT, button_hover_color=C_ACCENT)
        sl.set(def_v); sl.pack(fill="x", padx=20, pady=(0,10))
        lbl = customtkinter.CTkLabel(c, text=str(def_v), text_color=C_TEXT_DIM); lbl.pack(padx=20, pady=(0,15), anchor="e")
        sl.configure(command=lambda v: lbl.configure(text=f"{v:.2f}")); setattr(self, f"sl_{tag}", sl)

    def init_info(self, f):
        customtkinter.CTkLabel(f, text="Information", font=("Segoe UI", 26, "bold"), text_color=C_TEXT).pack(anchor="w", padx=40, pady=(40,20))
        c = customtkinter.CTkFrame(f, fg_color=C_CARD, corner_radius=15)
        c.pack(fill="both", expand=True, padx=40, pady=0)
        customtkinter.CTkLabel(c, text="MT2 MACRO", font=("Segoe UI", 40, "bold"), text_color=C_ACCENT).pack(pady=(60,10))
        customtkinter.CTkLabel(c, text="v4.2.0 Premium", font=("Consolas", 12), text_color=C_TEXT_DIM).pack()
        
        bf = customtkinter.CTkFrame(c, fg_color="transparent"); bf.pack(pady=40)
        customtkinter.CTkButton(bf, text="GitHub", fg_color=C_SIDEBAR, hover_color="#222", width=120, command=lambda: webbrowser.open("https://github.com/guvenada")).pack(side="left", padx=10)
        customtkinter.CTkButton(bf, text="LinkedIn", fg_color="#0077b5", hover_color="#006097", width=120, command=lambda: webbrowser.open("https://linkedin.com/in/guvenada")).pack(side="left", padx=10)

    def update_logs(self):
        while not self.log_queue.empty():
            msg = self.log_queue.get()
            self.log_box.configure(state="normal"); self.log_box.insert("end", msg + "\n"); self.log_box.see("end"); self.log_box.configure(state="disabled")
        self.after(100, self.update_logs)

    def toggle_power(self):
        if not self.is_running:
            self.is_running = True; self.btn_run.configure(text="TERMINATE", fg_color=C_DANGER); self.lbl_status.configure(text="RUNNING", text_color=C_ACCENT)
            cfg = {'threshold': self.sl_thresh.get(), 'offset': self.sl_offset.get(), 'delay': self.sl_delay.get()}
            self.worker = WorkerThread(self.log_queue, lambda t: None, cfg); self.worker.running = True; self.worker.paused = False; self.worker.start()
        else:
            self.is_running = False; self.btn_run.configure(text="ENGAGE PROTOCOL", fg_color=C_ACCENT); self.lbl_status.configure(text="READY", text_color=C_SUCCESS)
            if self.worker: self.worker.running = False; self.worker.join(0.1)

    def capture(self, name, sub=False): self.log_queue.put(f"[{datetime.now().strftime('%H:%M:%S')}] Snapshot in 3s..."); self.after(3000, lambda: self._cap(name, sub))
    def _cap(self, name, sub):
        with mss.mss() as sct: img = cv2.cvtColor(np.array(sct.grab(sct.monitors[1])), cv2.COLOR_BGRA2BGR)
        fname = f"{name}{1 if sub else ''}.png"
        if sub: 
            i=1; 
            while os.path.exists(f"{name}{i}.png"): i+=1
            fname = f"{name}{i}.png"
        cv2.imwrite(fname, img); self.log_queue.put(f"Saved: {fname}")
        try: os.startfile(os.path.abspath(fname))
        except: pass

if __name__ == "__main__":
    app = App()
    app.after(100, app.set_app_window) # Ensure taskbar icon appears
    app.mainloop()
