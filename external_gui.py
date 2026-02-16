"""
External System Monitor v2.0
============================
Educational use only.
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
from datetime import datetime

# GUI Libs (may require pip install customtkinter)
import tkinter
import customtkinter
from PIL import Image, ImageTk

# Core Libs
import cv2
import numpy as np
import mss

# ============================================
# SECURITY & UTILS (Obfuscation)
# ============================================

def _junk_math():
    return math.sqrt(random.random()) * math.sin(random.random())

class _ServiceWorker:
    def __init__(self):
        self.mem = []
    def _allocate(self):
        self.mem.append(random.getrandbits(128))

def set_random_title(app_root):
    """Changes window title periodically."""
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
            
            # Update Tkinter title safely? No, must be main thread.
            # Using ctypes instead to force change if possible or just rely on main thread update
            ctypes.windll.kernel32.SetConsoleTitleW(title)
            
            # Junk calcs
            _junk_math()
            time.sleep(random.uniform(5.0, 30.0))
        except:
            pass

# ============================================
# SYSTEM INPUT
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
    mouse_event(0x0008, 0, 0, 0, 0) # R Dn
    time.sleep(0.04)
    mouse_event(0x0010, 0, 0, 0, 0) # R Up
    time.sleep(0.08)
    mouse_event(0x0002, 0, 0, 0, 0) # L Dn
    time.sleep(0.04)
    mouse_event(0x0004, 0, 0, 0, 0) # L Up

def rotate_cam():
    input_key(VK_E, SCAN_E, True)
    time.sleep(0.6)
    input_key(VK_E, SCAN_E, False)

# ============================================
# VISION ENGINE
# ============================================

class VisionEngine:
    def __init__(self):
        self.template_target = None
        self.target_gray = None
        self.boss_templates = []
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1]
        
    def load_assets(self):
        # Load main
        if os.path.exists("target.png"):
            self.template_target = cv2.imread("target.png")
            if self.template_target is not None:
                self.target_gray = cv2.cvtColor(self.template_target, cv2.COLOR_BGR2GRAY)
        
        # Load bosses
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
        
        # Filter duplicates
        final = []
        for c in sorted(candidates, key=lambda x: -x[2]):
            if not any(abs(c[0]-f[0]) < 20 and abs(c[1]-f[1]) < 20 for f in final):
                final.append(c)
        return final

# ============================================
# BOT WORKER THREAD
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
            self.log("ERROR: No target.png found!")
            self.status("Status: Error")
            return
            
        self.log(f"Assets Loaded: Target={loaded}, SubTargets={n_boss}")
        
        sw = GetSystemMetrics(0)
        sh = GetSystemMetrics(1)
        cx, cy = sw // 2, sh // 2
        offset = int(self.config.get('offset', 80))
        
        while self.running:
            if self.paused:
                time.sleep(0.2)
                continue
            
            try:
                frame = self.vision.grab_screen()
                if frame is None: continue
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # 1. BOSS CHECK
                boss_found = False
                for _, _, b_gray in self.vision.boss_templates:
                    if self.vision.find_matches(gray, b_gray, 0.75):
                        boss_found = True
                        break
                
                if boss_found:
                    self.log(">> ELITE DETECTED -> Engaging")
                    self.status("Status: Engaging Elite")
                    input_key(VK_SPACE, SCAN_SPACE, True)
                    
                    waited = 0
                    no_boss = 0
                    while waited < 300: # 5 min timeout
                        time.sleep(2)
                        waited += 2
                        
                        if self.paused or not self.running:
                            input_key(VK_SPACE, SCAN_SPACE, False)
                            break
                            
                        # Re-scan
                        f2 = self.vision.grab_screen()
                        if f2 is None: continue
                        g2 = cv2.cvtColor(f2, cv2.COLOR_BGR2GRAY)
                        
                        still_here = any(self.vision.find_matches(g2, bg, 0.75) for _, _, bg in self.vision.boss_templates)
                        
                        if still_here:
                            no_boss = 0
                        else:
                            no_boss += 1
                            if no_boss >= 7:
                                self.log(f">> Elite Cleared ({waited}s)")
                                break
                    
                    input_key(VK_SPACE, SCAN_SPACE, False)
                    self.status("Status: Searching")
                    continue
                
                # 2. TARGET CHECK
                targets = self.vision.find_matches(gray, self.vision.target_gray, float(self.config.get('threshold', 0.55)))
                
                if targets:
                    # Filter distance
                    valid = [t for t in targets if (t[0]-cx)**2 + (t[1]-cy)**2 > 80**2]
                    
                    if valid:
                        best = min(valid, key=lambda t: (t[0]-cx)**2 + (t[1]-cy)**2)
                        tx, ty = best[0], best[1] + offset
                        
                        self.log(f"Target Found -> ({tx}, {ty})")
                        self.status("Status: Action")
                        click(tx, ty)
                        time.sleep(float(self.config.get('delay', 1.0)))
                    else:
                        rotate_cam()
                else:
                    self.status("Status: Scanning")
                    rotate_cam()
                    
                time.sleep(0.1)
                
            except Exception as e:
                self.log(f"Error: {e}")
                time.sleep(1)

# ============================================
# GUI CLASS (CustomTkinter)
# ============================================

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        # Security junk
        self._junk = _ServiceWorker()
        threading.Thread(target=set_random_title, args=(self,), daemon=True).start()

        # Window Config
        self.title("External System Monitor")
        self.geometry("700x500")
        self.resizable(False, False)
        
        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        self.sidebar = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)
        
        self.logo_label = customtkinter.CTkLabel(self.sidebar, text="EXT TOOL", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.btn_dashboard = customtkinter.CTkButton(self.sidebar, text="Dashboard", command=self.show_dashboard)
        self.btn_dashboard.grid(row=1, column=0, padx=20, pady=10)
        
        self.btn_settings = customtkinter.CTkButton(self.sidebar, text="Properties", command=self.show_settings)
        self.btn_settings.grid(row=2, column=0, padx=20, pady=10)
        
        self.status_label = customtkinter.CTkLabel(self.sidebar, text="Status: IDLE", text_color="gray")
        self.status_label.grid(row=5, column=0, padx=20, pady=20)

        # Content Areas
        self.frame_dash = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.frame_settings = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        
        self.setup_dashboard()
        self.setup_settings()
        
        self.show_dashboard()
        
        # Worker Vars
        self.log_queue = queue.Queue()
        self.worker = None
        self.is_running = False
        
        # Start Log Polling
        self.after(100, self.update_logs)

    def setup_dashboard(self):
        # Power Button
        self.btn_power = customtkinter.CTkButton(self.frame_dash, text="START SERVICE", 
                                                 font=customtkinter.CTkFont(size=16, weight="bold"),
                                                 height=50, fg_color="green", hover_color="darkgreen",
                                                 command=self.toggle_power)
        self.btn_power.pack(pady=20, padx=20, fill="x")
        
        # Log Console
        self.log_box = customtkinter.CTkTextbox(self.frame_dash, height=300)
        self.log_box.pack(pady=10, padx=20, fill="both", expand=True)
        self.log_box.insert("0.0", ">> System Ready...\n")
        self.log_box.configure(state="disabled")
        
        # Capture Controls
        frame_caps = customtkinter.CTkFrame(self.frame_dash)
        frame_caps.pack(pady=10, padx=20, fill="x")
        
        self.btn_cap_main = customtkinter.CTkButton(frame_caps, text="Capture Main", command=lambda: self.capture_asset("target"))
        self.btn_cap_main.pack(side="left", padx=5, expand=True)
        
        self.btn_cap_sub = customtkinter.CTkButton(frame_caps, text="Capture Sub", command=lambda: self.capture_asset("elite", sub=True))
        self.btn_cap_sub.pack(side="right", padx=5, expand=True)

    def setup_settings(self):
        lbl = customtkinter.CTkLabel(self.frame_settings, text="Configuration Properties", font=customtkinter.CTkFont(size=18))
        lbl.pack(pady=20)
        
        # Threshold
        self.lbl_th = customtkinter.CTkLabel(self.frame_settings, text="Match Threshold (0.1 - 1.0)")
        self.lbl_th.pack()
        self.entry_th = customtkinter.CTkEntry(self.frame_settings)
        self.entry_th.insert(0, "0.55")
        self.entry_th.pack(pady=5)
        
        # Offset
        self.lbl_off = customtkinter.CTkLabel(self.frame_settings, text="Y-Axis Offset (px)")
        self.lbl_off.pack()
        self.entry_off = customtkinter.CTkEntry(self.frame_settings)
        self.entry_off.insert(0, "80")
        self.entry_off.pack(pady=5)
        
        # Delay
        self.lbl_del = customtkinter.CTkLabel(self.frame_settings, text="Action Delay (sec)")
        self.lbl_del.pack()
        self.entry_del = customtkinter.CTkEntry(self.frame_settings)
        self.entry_del.insert(0, "1.0")
        self.entry_del.pack(pady=5)

    def show_dashboard(self):
        self.frame_settings.grid_forget()
        self.frame_dash.grid(row=0, column=1, rowspan=4, sticky="nsew", padx=20, pady=20)

    def show_settings(self):
        self.frame_dash.grid_forget()
        self.frame_settings.grid(row=0, column=1, rowspan=4, sticky="nsew", padx=20, pady=20)

    def log_msg(self, msg):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def update_logs(self):
        while not self.log_queue.empty():
            msg = self.log_queue.get()
            self.log_msg(msg)
        self.after(100, self.update_logs)

    def update_status(self, text):
        self.status_label.configure(text=text)

    def toggle_power(self):
        if not self.is_running:
            # Start
            self.is_running = True
            self.btn_power.configure(text="STOP SERVICE", fg_color="red", hover_color="darkred")
            self.log_msg(">> Service Started")
            
            cfg = {
                'threshold': self.entry_th.get(),
                'offset': self.entry_off.get(),
                'delay': self.entry_del.get()
            }
            
            self.worker = WorkerThread(self.log_queue, self.update_status, cfg)
            self.worker.running = True
            self.worker.paused = False
            self.worker.start()
        else:
            # Stop
            self.is_running = False
            self.btn_power.configure(text="START SERVICE", fg_color="green", hover_color="darkgreen")
            self.log_msg(">> Service Stopped")
            self.update_status("Status: IDLE")
            
            if self.worker:
                self.worker.running = False
                self.worker.paused = True
    
    def capture_asset(self, name, sub=False):
        self.log_msg(f"Capturing {name} in 3 seconds...")
        self.after(3000, lambda: self._do_capture(name, sub))
        
    def _do_capture(self, name, sub):
        with mss.mss() as sct:
            raw = np.array(sct.grab(sct.monitors[1]))
            img = cv2.cvtColor(raw, cv2.COLOR_BGRA2BGR)
            
        fname = name
        if sub:
            i = 1
            while os.path.exists(f"{name}{i}.png"): i += 1
            fname = f"{name}{i}"
            
        cv2.imwrite(f"{fname}.png", img)
        self.log_msg(f"Saved: {fname}.png")
        
        # Open paint
        try:
            import subprocess
            subprocess.Popen(["mspaint", os.path.abspath(f"{fname}.png")])
        except: pass

if __name__ == "__main__":
    app = App()
    app.mainloop()
