"""
Harici Sistem İzleyici v2.1 (Pro GUI)
=====================================
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
import colorsys  # RGB efekti için
from datetime import datetime

# GUI Kütüphaneleri
import tkinter
import customtkinter
from PIL import Image, ImageTk

# Çekirdek Kütüphaneler
import cv2
import numpy as np
import mss

# ============================================
# GÜVENLİK VE ARAÇLAR (Obfuscation)
# ============================================

def _junk_math():
    return math.sqrt(random.random()) * math.sin(random.random())

class _ServiceWorker:
    def __init__(self):
        self.mem = []
    def _allocate(self):
        self.mem.append(random.getrandbits(128))

def set_random_title(app_root):
    """Pencere başlığını belirli aralıklarla değiştirir."""
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
# SİSTEM GİRDİSİ (SYSTEM INPUT)
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
    time.sleep(0.08)
    mouse_event(0x0008, 0, 0, 0, 0) 
    time.sleep(0.04)
    mouse_event(0x0010, 0, 0, 0, 0)
    time.sleep(0.08)
    mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.04)
    mouse_event(0x0004, 0, 0, 0, 0)

def rotate_cam():
    input_key(VK_E, SCAN_E, True)
    time.sleep(0.6)
    input_key(VK_E, SCAN_E, False)

# ============================================
# GÖRÜNTÜ MOTORU (VISION ENGINE)
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
        th, tw = template.shape[:2]
        res = cv2.matchTemplate(scene_gray, template, cv2.TM_CCOEFF_NORMED)
        locs = np.where(res >= thresh)
        candidates = []
        for pt in zip(*locs[::-1]):
            candidates.append((pt[0] + tw//2, pt[1] + th//2, res[pt[1], pt[0]]))
        final = []
        for c in sorted(candidates, key=lambda x: -x[2]):
            if not any(abs(c[0]-f[0]) < 20 and abs(c[1]-f[1]) < 20 for f in final):
                final.append(c)
        return final

# ============================================
# BOT İŞÇİ PARÇACIĞI (WORKER THREAD)
# ============================================

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
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_queue.put(f"[{ts}] {msg}")

    def run(self):
        loaded, n_boss = self.vision.load_assets()
        if not loaded:
            self.log("HATA: target.png bulunamadı! (ERROR)")
            self.status("Durum: Hata (Error)")
            return
            
        self.log(f"Varlıklar Yüklendi: Hedef={loaded}, YanHedefler={n_boss}")
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
                
                # Check Elites
                boss_found = False
                for _, _, b_gray in self.vision.boss_templates:
                    if self.vision.find_matches(gray, b_gray, 0.75):
                        boss_found = True
                        break
                
                if boss_found:
                    self.log(">> ELİT TESPİT EDİLDİ -> Saldırılıyor")
                    self.status("Durum: Elit Saldırısı")
                    input_key(VK_SPACE, SCAN_SPACE, True)
                    waited, no_boss = 0, 0
                    while waited < 300:
                        time.sleep(2)
                        waited += 2
                        if self.paused or not self.running:
                            input_key(VK_SPACE, SCAN_SPACE, False)
                            break
                        f2 = self.vision.grab_screen()
                        if f2 is None: continue
                        g2 = cv2.cvtColor(f2, cv2.COLOR_BGR2GRAY)
                        if any(self.vision.find_matches(g2, bg, 0.75) for _, _, bg in self.vision.boss_templates):
                            no_boss = 0
                        else:
                            no_boss += 1
                            if no_boss >= 7:
                                self.log(f">> Elit Temizlendi ({waited}s)")
                                break
                    input_key(VK_SPACE, SCAN_SPACE, False)
                    self.status("Durum: Aranıyor")
                    continue
                
                # Check Targets
                targets = self.vision.find_matches(gray, self.vision.target_gray, float(self.config.get('threshold', 0.55)))
                if targets:
                    valid = [t for t in targets if (t[0]-cx)**2 + (t[1]-cy)**2 > 80**2]
                    if valid:
                        best = min(valid, key=lambda t: (t[0]-cx)**2 + (t[1]-cy)**2)
                        tx, ty = best[0], best[1] + offset
                        self.log(f"Hedef Bulundu -> ({tx}, {ty})")
                        self.status("Durum: İşlem")
                        click(tx, ty)
                        time.sleep(float(self.config.get('delay', 1.0)))
                    else:
                        rotate_cam()
                else:
                    self.status("Durum: Taranıyor")
                    rotate_cam()
                time.sleep(0.1)
                
            except Exception as e:
                self.log(f"Hata: {e}")
                time.sleep(1)

# ============================================
# SPLASH SCREEN (AÇILIŞ EKRANI)
# ============================================

class SplashScreen(customtkinter.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.geometry("400x300")
        self.overrideredirect(True) # Çerçevesiz
        self.attributes('-topmost', True)
        self.attributes('-alpha', 0.0) # Başlangıçta görünmez
        
        # Ekranı ortala
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - 400) // 2
        y = (sh - 300) // 2
        self.geometry(f"+{x}+{y}")
        
        # İçerik
        self.frame = customtkinter.CTkFrame(self, fg_color="#1a1a1a", corner_radius=20, border_width=2, border_color="#333")
        self.frame.pack(fill="both", expand=True)
        
        lbl_title = customtkinter.CTkLabel(self.frame, text="MT2 MACRO", font=("Roboto", 40, "bold"), text_color="white")
        lbl_title.pack(pady=(80, 10))
        
        lbl_sub = customtkinter.CTkLabel(self.frame, text="Loading System Modules...", font=("Roboto", 12), text_color="#aaaaaa")
        lbl_sub.pack(pady=5)
        
        self.progress = customtkinter.CTkProgressBar(self.frame, width=200, height=10, progress_color="#00ff00")
        self.progress.pack(pady=20)
        self.progress.set(0)
        
        # Animasyon Başlat
        self.fade_in()

    def fade_in(self):
        alpha = self.attributes('-alpha')
        if alpha < 1.0:
            alpha += 0.05
            self.attributes('-alpha', alpha)
            self.after(20, self.fade_in)
        else:
            self.load_modules()
            
    def load_modules(self):
        # Yükleme simülasyonu
        val = self.progress.get()
        if val < 1.0:
            val += 0.02
            self.progress.set(val)
            self.after(20, self.load_modules) # Hızlı geçiş
        else:
            self.fade_out()
            
    def fade_out(self):
        alpha = self.attributes('-alpha')
        if alpha > 0.0:
            alpha -= 0.05
            self.attributes('-alpha', alpha)
            self.after(20, self.fade_out)
        else:
            self.destroy()
            self.master.deiconify() # Ana pencereyi göster

# ============================================
# MAIN GUI (RGB & PRO)
# ============================================

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw() # İlk başta gizle (Splash için)
        
        # Güvenlik
        self._junk = _ServiceWorker()
        threading.Thread(target=set_random_title, args=(self,), daemon=True).start()

        self.title("mt2macro - Pro Edition")
        self.geometry("800x600")
        
        # RGB Frame (Ana kapsayıcı)
        self.rgb_hue = 0
        self.rgb_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.rgb_frame.pack(fill="both", expand=True)
        
        # İçerik Frame (RGB içinde biraz küçük durarak kenarlık efekti verir)
        self.main_container = customtkinter.CTkFrame(self.rgb_frame, corner_radius=10, fg_color="#1a1a1a")
        self.main_container.pack(fill="both", expand=True, padx=3, pady=3)
        
        # === Layout Ayarları ===
        self.main_container.grid_columnconfigure(1, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)
        
        # === SIDEBAR ===
        self.sidebar = customtkinter.CTkFrame(self.main_container, width=200, corner_radius=10)
        self.sidebar.grid(row=0, column=0, rowspan=4, sticky="nsew", padx=10, pady=10)
        self.sidebar.grid_rowconfigure(5, weight=1)
        
        logo = customtkinter.CTkLabel(self.sidebar, text="MT2 MACRO", font=customtkinter.CTkFont(size=24, weight="bold"))
        logo.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.btn_dash = customtkinter.CTkButton(self.sidebar, text="Panel (Dashboard)", command=self.show_dashboard)
        self.btn_dash.grid(row=1, column=0, padx=20, pady=10)
        
        self.btn_set = customtkinter.CTkButton(self.sidebar, text="Ayarlar (Settings)", command=self.show_settings)
        self.btn_set.grid(row=2, column=0, padx=20, pady=10)
        
        # === REKLAM / SOSYAL LİNKLER ===
        lbl_dev = customtkinter.CTkLabel(self.sidebar, text="Geliştirici (Dev)", text_color="gray", font=("Arial", 10))
        lbl_dev.grid(row=5, column=0, padx=20, pady=(10,0), sticky="s")
        
        link_gh = customtkinter.CTkLabel(self.sidebar, text="GitHub: @guvenada", text_color="#3B8ED0", cursor="hand2")
        link_gh.grid(row=6, column=0, padx=20, pady=2)
        link_gh.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/guvenada"))
        
        link_li = customtkinter.CTkLabel(self.sidebar, text="LinkedIn: @guvenada", text_color="#3B8ED0", cursor="hand2")
        link_li.grid(row=7, column=0, padx=20, pady=(2, 20))
        link_li.bind("<Button-1>", lambda e: webbrowser.open("https://linkedin.com/in/guvenada"))
        
        # === İÇERİK ===
        self.frame_dash = customtkinter.CTkFrame(self.main_container, corner_radius=0, fg_color="transparent")
        self.frame_set = customtkinter.CTkFrame(self.main_container, corner_radius=0, fg_color="transparent")
        
        self.setup_dashboard()
        self.setup_settings()
        
        self.show_dashboard()
        
        # === SİSTEMLER ===
        self.log_queue = queue.Queue()
        self.worker = None
        self.is_running = False
        self.after(100, self.update_logs)
        
        # RGB Döngüsü Başlat
        self.animate_rgb()
        
        # Splash Screen Göster
        self.after(100, lambda: SplashScreen(self))

    def animate_rgb(self):
        # Smooth RGB border animation
        self.rgb_hue += 0.005 # Hız
        if self.rgb_hue > 1.0: self.rgb_hue = 0.0
        
        rgb = colorsys.hsv_to_rgb(self.rgb_hue, 1.0, 1.0)
        color_hex = "#%02x%02x%02x" % (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
        
        self.rgb_frame.configure(fg_color=color_hex)
        self.sidebar.configure(border_width=1, border_color=color_hex)
        
        self.after(20, self.animate_rgb)

    def setup_dashboard(self):
        self.btn_power = customtkinter.CTkButton(self.frame_dash, text="SERVİSİ BAŞLAT", height=60, fg_color="#2ecc71", hover_color="#27ae60", font=("Arial", 16, "bold"), command=self.toggle_power)
        self.btn_power.pack(pady=20, padx=20, fill="x")
        
        self.log_box = customtkinter.CTkTextbox(self.frame_dash, height=300)
        self.log_box.pack(pady=10, padx=20, fill="both", expand=True)
        self.log_box.insert("0.0", ">> Sistem Hazır...\n")
        self.log_box.configure(state="disabled")
        
        f_caps = customtkinter.CTkFrame(self.frame_dash, fg_color="transparent")
        f_caps.pack(pady=10, padx=20, fill="x")
        
        customtkinter.CTkButton(f_caps, text="Ana Hedef Yakala", command=lambda: self.capture("target")).pack(side="left", padx=5, expand=True)
        customtkinter.CTkButton(f_caps, text="Alt Hedef Yakala", command=lambda: self.capture("elite", True)).pack(side="right", padx=5, expand=True)
        
        self.lbl_stat = customtkinter.CTkLabel(self.frame_dash, text="Durum: BOŞTA", font=("Arial", 14))
        self.lbl_stat.pack(pady=10)

    def setup_settings(self):
        customtkinter.CTkLabel(self.frame_set, text="Ayarlar", font=("Arial", 20)).pack(pady=20)
        
        self.in_th = self.add_setting("Hassasiyet (0.1 - 1.0)", "0.55")
        self.in_off = self.add_setting("Y-Ofset (px)", "80")
        self.in_del = self.add_setting("Gecikme (sn)", "1.0")

    def add_setting(self, text, val):
        customtkinter.CTkLabel(self.frame_set, text=text).pack(pady=(10,0))
        entry = customtkinter.CTkEntry(self.frame_set)
        entry.insert(0, val)
        entry.pack(pady=5)
        return entry

    def show_dashboard(self):
        self.frame_set.grid_forget()
        self.frame_dash.grid(row=0, column=1, rowspan=4, sticky="nsew", padx=20, pady=20)

    def show_settings(self):
        self.frame_dash.grid_forget()
        self.frame_set.grid(row=0, column=1, rowspan=4, sticky="nsew", padx=20, pady=20)

    def log_msg(self, msg):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def update_logs(self):
        while not self.log_queue.empty():
            self.log_msg(self.log_queue.get())
        self.after(100, self.update_logs)

    def toggle_power(self):
        if not self.is_running:
            self.is_running = True
            self.btn_power.configure(text="SERVİSİ DURDUR", fg_color="#e74c3c", hover_color="#c0392b")
            self.log_msg(">> Servis Başlatıldı")
            cfg = {'threshold': self.in_th.get(), 'offset': self.in_off.get(), 'delay': self.in_del.get()}
            self.worker = WorkerThread(self.log_queue, lambda t: self.lbl_stat.configure(text=t), cfg)
            self.worker.running = True; self.worker.paused = False; self.worker.start()
        else:
            self.is_running = False
            self.btn_power.configure(text="SERVİSİ BAŞLAT", fg_color="#2ecc71", hover_color="#27ae60")
            self.log_msg(">> Servis Durduruldu")
            self.lbl_stat.configure(text="Durum: BOŞTA")
            if self.worker: self.worker.running = False

    def capture(self, name, sub=False):
        self.log_msg(f"'{name}' 3s içinde yakalanıyor...")
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
        self.log_msg(f"Kaydedildi: {fname}")
        try:
            import subprocess
            subprocess.Popen(["mspaint", os.path.abspath(f"{fname}.png")])
        except: pass

if __name__ == "__main__":
    app = App()
    app.mainloop()
