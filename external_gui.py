"""
Harici Sistem İzleyici v3.2 (Premium Edition)
=============================================
Sadece eğitim amaçlıdır (Educational use only).
"""

import sys
import threading
import queue
import time
import random
import string
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
# TEMALAR VE RENKLER
# ============================================
COLOR_BG = "#0F0F0F"
COLOR_CARD = "#1A1A1A"
COLOR_ACCENT = "#00E5FF"
COLOR_TEXT_MAIN = "#FFFFFF"
COLOR_TEXT_SUB = "#AAAAAA"
COLOR_BORDER = "#333333"

# ============================================
# GÜVENLİK VE ARAÇLAR
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
        "Runtime Broker", "Service Host", "DirectX Diagnostics",
        "Performance Monitor", "Network Service", "Update Worker"
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

# ============================================
# SİSTEM GİRDİSİ
# ============================================

user32 = ctypes.windll.user32
keybd_event = user32.keybd_event
mouse_event = user32.mouse_event
SetCursorPos = user32.SetCursorPos
GetAsyncKeyState = user32.GetAsyncKeyState
GetSystemMetrics = user32.GetSystemMetrics

VK_E, SCAN_E = 0x45, 0x12
VK_SPACE, SCAN_SPACE = 0x20, 0x39
VK_ESC = 0x1B

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

# ============================================
# GÖRÜNTÜ VE BOT MOTORU
# ============================================

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
        
        self.log(f"Sistem Aktif. Hedefler: {n_boss+1}")
        cx, cy = GetSystemMetrics(0) // 2, GetSystemMetrics(1) // 2
        offset = int(self.config.get('offset', 80))
        
        while self.running:
            if self.paused:
                time.sleep(0.2)
                continue
            
            try:
                frame = self.vision.grab_screen()
                if frame is None: continue
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Boss Check
                boss_found = False
                for _, _, b_gray in self.vision.boss_templates:
                    if self.vision.find_matches(gray, b_gray, 0.75):
                        boss_found = True
                        break
                
                if boss_found:
                    self.log(">> ELİT TESPİT EDİLDİ")
                    self.status("Durum: Elit Savaş")
                    input_key(VK_SPACE, SCAN_SPACE, True)
                    
                    for _ in range(150):
                        time.sleep(2)
                        if self.paused or not self.running: break
                        
                        f2 = self.vision.grab_screen()
                        if f2 is None: continue
                        g2 = cv2.cvtColor(f2, cv2.COLOR_BGR2GRAY)
                        if not any(self.vision.find_matches(g2, bg, 0.75) for _, _, bg in self.vision.boss_templates):
                            no_boss_chk = 0
                            for _ in range(5):
                                time.sleep(0.2)
                                f3 = self.vision.grab_screen()
                                if f3 is None: continue
                                g3 = cv2.cvtColor(f3, cv2.COLOR_BGR2GRAY)
                                if not any(self.vision.find_matches(g3, bg, 0.75) for _, _, bg in self.vision.boss_templates):
                                    no_boss_chk += 1
                            if no_boss_chk >= 4:
                                self.log(">> Elit Temizlendi")
                                break
                    input_key(VK_SPACE, SCAN_SPACE, False)
                    self.status("Durum: Arama")
                    continue
                
                # Target Check
                targets = self.vision.find_matches(gray, self.vision.target_gray, float(self.config.get('threshold', 0.55)))
                if targets:
                    valid = [t for t in targets if (t[0]-cx)**2 + (t[1]-cy)**2 > 80**2]
                    if valid:
                        best = min(valid, key=lambda t: (t[0]-cx)**2 + (t[1]-cy)**2)
                        tx, ty = best[0], best[1] + offset
                        self.log(f"Hedef -> ({tx}, {ty})")
                        self.status("Durum: Saldırı")
                        click(tx, ty)
                        time.sleep(float(self.config.get('delay', 1.0)))
                    else:
                        rotate_cam()
                else:
                    self.status("Durum: Tarama")
                    rotate_cam()
                time.sleep(0.1)
            except Exception as e:
                self.log(f"Hata: {e}")
                time.sleep(1)

# ============================================
# SPLASH SCREEN
# ============================================
class SplashScreen(customtkinter.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.geometry("400x250")
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.attributes('-alpha', 0.0)
        
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"+{(sw-400)//2}+{(sh-250)//2}")
        
        self.frame = customtkinter.CTkFrame(self, fg_color="#0F0F0F", corner_radius=20, border_width=1, border_color="#333333")
        self.frame.pack(fill="both", expand=True)
        
        customtkinter.CTkLabel(self.frame, text="MT2 MACRO", font=("Roboto", 45, "bold"), text_color="white").pack(pady=(60, 5))
        customtkinter.CTkLabel(self.frame, text="PREMIUM AUTOMATION SUITE", font=("Roboto", 10, "bold"), text_color=COLOR_ACCENT).pack(pady=0)
        
        self.progress = customtkinter.CTkProgressBar(self.frame, width=200, height=4, progress_color=COLOR_ACCENT, fg_color="#222")
        self.progress.pack(pady=40)
        self.progress.set(0)
        
        self.fade_in()

    def fade_in(self):
        alpha = self.attributes('-alpha')
        if alpha < 1.0:
            self.attributes('-alpha', alpha + 0.05)
            self.after(20, self.fade_in)
        else:
            self.load_modules()
            
    def load_modules(self):
        val = self.progress.get()
        if val < 1.0:
            self.progress.set(val + 0.02)
            self.after(15, self.load_modules)
        else:
            self.fade_out()
            
    def fade_out(self):
        alpha = self.attributes('-alpha')
        if alpha > 0.0:
            self.attributes('-alpha', alpha - 0.05)
            self.after(20, self.fade_out)
        else:
            self.destroy()
            self.master.deiconify()

# ============================================
# MAIN GUI (PREMIUM)
# ============================================

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("green")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        
        self._junk = _ServiceWorker()
        threading.Thread(target=set_random_title, args=(self,), daemon=True).start()

        self.title("mt2macro - Premium")
        self.geometry("900x600")
        self.overrideredirect(True) # Özel Başlık Çubuğu için sistem başlığını kapat
        self.configure(fg_color=COLOR_BG)
        
        # Ekranı Ortala
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"+{(sw-900)//2}+{(sh-600)//2}")
        
        # RGB Kapsayıcı
        self.rgb_hue = 0.5
        self.rgb_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color=COLOR_BG)
        self.rgb_frame.pack(fill="both", expand=True) 
        
        # === ANA GRID DÜZENİ ===
        self.rgb_frame.grid_columnconfigure(1, weight=1)
        self.rgb_frame.grid_rowconfigure(1, weight=1) # İçerik satırı
        
        # === ÖZEL BAŞLIK ÇUBUĞU (Custom Title Bar) ===
        self.title_bar = customtkinter.CTkFrame(self.rgb_frame, corner_radius=0, fg_color="#0F0F0F", height=35)
        self.title_bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        # Başlık sürükleme olayları
        self.title_bar.bind("<ButtonPress-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)
        
        title_lbl = customtkinter.CTkLabel(self.title_bar, text="  MT2 MACRO Premium", font=("Roboto", 12, "bold"), text_color="#888")
        title_lbl.pack(side="left", padx=10)
        title_lbl.bind("<ButtonPress-1>", self.start_move)
        title_lbl.bind("<B1-Motion>", self.do_move)
        
        # Pencere Kontrol Butonları
        self.btn_close = customtkinter.CTkButton(self.title_bar, text="✕", width=40, font=("Roboto", 15), 
                                                 fg_color="transparent", hover_color="#C0392B", 
                                                 command=self.close_app)
        self.btn_close.pack(side="right")
        
        self.btn_min = customtkinter.CTkButton(self.title_bar, text="—", width=40, font=("Roboto", 15), 
                                               fg_color="transparent", hover_color="#333", 
                                               command=self.iconify)
        self.btn_min.pack(side="right")
        
        # === SIDEBAR ===
        self.sidebar = customtkinter.CTkFrame(self.rgb_frame, width=220, corner_radius=0, fg_color=COLOR_CARD, border_width=0)
        self.sidebar.grid(row=1, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)
        
        customtkinter.CTkLabel(self.sidebar, text="KONTROL MERKEZİ", font=("Roboto", 18, "bold"), text_color="white").grid(row=0, column=0, padx=20, pady=(30, 10))
        
        self.btn_dash = self.create_menu_btn("Panel", "🏠", self.show_dashboard, 2)
        self.btn_set = self.create_menu_btn("Ayarlar", "⚙️", self.show_settings, 3)
        self.btn_info = self.create_menu_btn("Hakkında", "ℹ️", self.show_info, 4)
        
        f_social = customtkinter.CTkFrame(self.sidebar, fg_color="transparent")
        f_social.grid(row=7, column=0, padx=20, pady=20, sticky="s")
        self.create_link(f_social, "GitHub", "https://github.com/guvenada")
        self.create_link(f_social, "LinkedIn", "https://linkedin.com/in/guvenada")
        
        # === İÇERİK ===
        self.content = customtkinter.CTkFrame(self.rgb_frame, corner_radius=20, fg_color="#141414")
        self.content.grid(row=1, column=1, sticky="nsew", padx=20, pady=20)
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)
        
        # Sayfalar
        self.frame_dash = customtkinter.CTkFrame(self.content, fg_color="transparent")
        self.frame_set = customtkinter.CTkFrame(self.content, fg_color="transparent")
        self.frame_info = customtkinter.CTkFrame(self.content, fg_color="transparent")
        
        self.setup_dashboard()
        self.setup_settings()
        self.setup_info()
        
        self.show_dashboard()
        
        # Bot & Log
        self.log_queue = queue.Queue()
        self.worker = None
        self.is_running = False
        self.after(100, self.update_logs)
        
        # Anim & Splash
        self.animate_border()
        self.after(200, lambda: SplashScreen(self))

    def create_menu_btn(self, text, icon, cmd, r):
        btn = customtkinter.CTkButton(
            self.sidebar, text=f"{icon}   {text}", anchor="w", 
            fg_color="transparent", text_color="#DDD", hover_color="#333", 
            height=45, corner_radius=10, font=("Roboto", 14), command=cmd
        )
        btn.grid(row=r, column=0, padx=15, pady=5, sticky="ew")
        return btn

    def create_link(self, parent, text, url):
        lbl = customtkinter.CTkLabel(parent, text=f"🔗 {text}", text_color="#555", cursor="hand2", font=("Roboto", 11))
        lbl.pack(pady=2)
        lbl.bind("<Button-1>", lambda e: webbrowser.open(url))

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def close_app(self):
        self.destroy()
        sys.exit()

    def animate_border(self):
        self.rgb_hue += 0.002
        if self.rgb_hue > 1.0: self.rgb_hue = 0.0
        rgb = colorsys.hsv_to_rgb(self.rgb_hue, 0.8, 1.0)
        color = "#%02x%02x%02x" % (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
        self.sidebar.configure(border_width=2, border_color=color)
        self.after(50, self.animate_border)

    def setup_dashboard(self):
        f = self.frame_dash
        f.pack(fill="both", expand=True, padx=30, pady=30)
        
        top_bar = customtkinter.CTkFrame(f, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 20))
        customtkinter.CTkLabel(top_bar, text="Kontrol Paneli", font=("Roboto", 24, "bold")).pack(side="left")
        self.lbl_status = customtkinter.CTkLabel(top_bar, text="HAZIR", font=("Roboto", 12, "bold"), text_color="#777", fg_color="#222", corner_radius=5, padx=10, pady=5)
        self.lbl_status.pack(side="right")
        
        self.btn_power = customtkinter.CTkButton(
            f, text="SERVİSİ BAŞLAT", font=("Roboto", 16, "bold"), height=60, corner_radius=30, 
            fg_color=COLOR_ACCENT, text_color="black", hover_color="white", command=self.toggle_power
        )
        self.btn_power.pack(fill="x", pady=20)
        
        log_card = customtkinter.CTkFrame(f, fg_color=COLOR_CARD, corner_radius=15, border_width=1, border_color=COLOR_BORDER)
        log_card.pack(fill="both", expand=True, pady=10)
        
        customtkinter.CTkLabel(log_card, text="Sistem Kayıtları", font=("Roboto", 12, "bold"), text_color="#555").pack(pady=10, padx=15, anchor="w")
        self.log_box = customtkinter.CTkTextbox(log_card, fg_color="transparent", text_color="#CCC", font=("Consolas", 12))
        self.log_box.pack(fill="both", expand=True, padx=10, pady=(0,10))
        self.log_box.insert("0.0", f"[{datetime.now().strftime('%H:%M')}] Sistem hazır ve bekliyor...\n")
        self.log_box.configure(state="disabled")

        tool_grid = customtkinter.CTkFrame(f, fg_color="transparent")
        tool_grid.pack(fill="x", pady=10)
        self.create_tool_btn(tool_grid, "🎯 Ana Hedef Tanımla", lambda: self.capture("target"), 0)
        self.create_tool_btn(tool_grid, "👹 Elit Hedef Tanımla", lambda: self.capture("elite", True), 1)

    def create_tool_btn(self, parent, text, cmd, col):
        b = customtkinter.CTkButton(parent, text=text, fg_color="#222", hover_color="#333", border_width=1, border_color="#444", height=40, corner_radius=10, command=cmd)
        b.pack(side="left", fill="x", expand=True, padx=5 if col==1 else (0,5))

    def setup_settings(self):
        f = self.frame_set
        f.pack(fill="both", expand=True, padx=40, pady=40)
        customtkinter.CTkLabel(f, text="Yapılandırma", font=("Roboto", 24, "bold")).pack(anchor="w", pady=(0,30))
        self.in_th = self.add_param(f, "Algılama Hassasiyeti (Threshold)", "0.55")
        self.in_off = self.add_param(f, "Tıklama Kaydırma (Offset Y)", "80")
        self.in_del = self.add_param(f, "İşlem Aralığı (Delay)", "1.0")
        customtkinter.CTkLabel(f, text="* Değişiklikler için servisi yeniden başlatın.", text_color="gray", font=("Roboto", 10)).pack(pady=20)

    def add_param(self, parent, title, val):
        card = customtkinter.CTkFrame(parent, fg_color=COLOR_CARD, corner_radius=10)
        card.pack(fill="x", pady=10)
        customtkinter.CTkLabel(card, text=title, font=("Roboto", 12)).pack(side="left", padx=20, pady=15)
        e = customtkinter.CTkEntry(card, width=100, border_color="#333", fg_color="#111")
        e.insert(0, val)
        e.pack(side="right", padx=20, pady=15)
        return e

    def setup_info(self):
        f = self.frame_info
        f.pack(fill="both", expand=True, padx=40, pady=40)
        
        customtkinter.CTkLabel(f, text="Hakkında", font=("Roboto", 24, "bold")).pack(anchor="w", pady=(0,20))
        
        card = customtkinter.CTkFrame(f, fg_color=COLOR_CARD, corner_radius=15, border_width=1, border_color=COLOR_BORDER)
        card.pack(fill="both", expand=True, pady=10)
        
        customtkinter.CTkLabel(card, text="MT2 MACRO", font=("Roboto", 30, "bold"), text_color="white").pack(pady=(40, 5))
        customtkinter.CTkLabel(card, text="Version 3.2.0 (Premium Build)", font=("Roboto", 12), text_color=COLOR_ACCENT).pack(pady=0)
        
        desc = """
        Bu yazılım, görüntü işleme tabanlı bir otomasyon aracıdır.
        Tamamen eğitim amaçlı geliştirilmiştir (Educational Use Only).
        
        Geliştirici: @guvenada
        Lisans: MIT License
        """
        customtkinter.CTkLabel(card, text=desc, font=("Roboto", 14), text_color="#AAA", justify="center").pack(pady=20)
        
        btn_g = customtkinter.CTkButton(card, text="GitHub Profilini Ziyaret Et", command=lambda: webbrowser.open("https://github.com/guvenada"), fg_color="#333", hover_color="#444")
        btn_g.pack(pady=10)

    def show_dashboard(self):
        self.frame_set.pack_forget()
        self.frame_info.pack_forget()
        self.frame_dash.pack(fill="both", expand=True, padx=30, pady=30)
        self.btn_dash.configure(fg_color="#333"); self.btn_set.configure(fg_color="transparent"); self.btn_info.configure(fg_color="transparent")

    def show_settings(self):
        self.frame_dash.pack_forget()
        self.frame_info.pack_forget()
        self.frame_set.pack(fill="both", expand=True, padx=40, pady=40)
        self.btn_dash.configure(fg_color="transparent"); self.btn_set.configure(fg_color="#333"); self.btn_info.configure(fg_color="transparent")

    def show_info(self):
        self.frame_dash.pack_forget()
        self.frame_set.pack_forget()
        self.frame_info.pack(fill="both", expand=True, padx=40, pady=40)
        self.btn_dash.configure(fg_color="transparent"); self.btn_set.configure(fg_color="transparent"); self.btn_info.configure(fg_color="#333")

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
            self.btn_power.configure(text="SERVİSİ DURDUR", fg_color="#FF3D00", hover_color="#DD2C00")
            self.lbl_status.configure(text="AKTİF", text_color="#00E5FF")
            cfg = {'threshold': self.in_th.get(), 'offset': self.in_off.get(), 'delay': self.in_del.get()}
            self.worker = WorkerThread(self.log_queue, lambda t: None, cfg)
            self.worker.running = True; self.worker.paused = False; self.worker.start()
        else:
            self.is_running = False
            self.btn_power.configure(text="SERVİSİ BAŞLAT", fg_color=COLOR_ACCENT, hover_color="white")
            self.lbl_status.configure(text="DURDURULDU", text_color="#777")
            if self.worker: self.worker.running = False

    def capture(self, name, sub=False):
        self.log_queue.put(f"[{datetime.now().strftime('%H:%M:%S')}] Yakalama 3sn içinde...")
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
        self.log_queue.put(f"[{datetime.now().strftime('%H:%M:%S')}] Kaydedildi: {fname}")
        try:
            import subprocess
            subprocess.Popen(["mspaint", os.path.abspath(f"{fname}.png")])
        except: pass

if __name__ == "__main__":
    app = App()
    app.mainloop()
