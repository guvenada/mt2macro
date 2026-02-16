"""
External Automation Tool v1.0
=============================
Educational use only.
"""

import cv2
import numpy as np
import mss
import time
import ctypes
import os
import random
import string
import math
from threading import Thread, Lock

# ============================================
# SECURITY & UTILS (Obfuscation)
# ============================================

def _junk_math_operation(a, b):
    # Basic math noise
    return math.sqrt(a**2 + b**2) * math.sin(a)

class _MemoryManager:
    # Junk class for structure
    def __init__(self):
        self.allocated = []
    def _allocate_dummy(self):
        self.allocated.append("0x" + "".join(random.choices("0123456789ABCDEF", k=8)))

def set_random_title():
    """Changes console title periodically to random system names."""
    titles = [
        "Command Prompt", "Windows PowerShell", "System Service", 
        "Calculator", "Notepad", "Task Manager", "Explorer",
        "Runtime Broker", "Service Host", "Application Frame Host"
    ]
    chars = string.ascii_letters + string.digits
    
    while True:
        if random.random() < 0.3:
            # Random hex string
            title = "0x" + "".join(random.choices("0123456789ABCDEF", k=random.randint(8, 16)))
        else:
            # System-like name
            title = random.choice(titles)
        
        ctypes.windll.kernel32.SetConsoleTitleW(title)
        
        # Junk calculation
        _junk_math_operation(random.randint(1, 100), random.randint(1, 100))
        
        time.sleep(random.uniform(2.0, 15.0))

def check_security():
    """Basic environment check."""
    # Check for simple debuggers
    if ctypes.windll.kernel32.IsDebuggerPresent() != 0:
        print("System Error: 0xC0000005") # Fake error
        time.sleep(1)
        os._exit(0)

# ============================================
# CONFIGURATION
# ============================================

CONFIG = {
    'target_threshold': 0.55,
    'elite_threshold': 0.75,
    'input_offset': 80,
    'action_delay': 1.0, 
    'elite_timeout': 300, 
    'check_interval': 2, 
    'stuck_limit': 3,     
}

# ============================================
# SYSTEM INTERFACE
# ============================================

user32 = ctypes.windll.user32
keybd_event = user32.keybd_event
mouse_event = user32.mouse_event
SetCursorPos = user32.SetCursorPos
GetAsyncKeyState = user32.GetAsyncKeyState
GetSystemMetrics = user32.GetSystemMetrics

VK_E, SCAN_E = 0x45, 0x12
VK_SPACE, SCAN_SPACE = 0x20, 0x39
VK_F11, VK_F12, VK_ESCAPE = 0x7A, 0x7B, 0x1B

def input_key(vk, scan, down=True):
    flag = 0 if down else 2
    keybd_event(vk, scan, flag, 0)

def rotate_camera():
    input_key(VK_E, SCAN_E, True)
    time.sleep(0.6)
    input_key(VK_E, SCAN_E, False)

def simulate_click(x, y):
    SetCursorPos(int(x), int(y))
    time.sleep(0.08)
    mouse_event(0x0008, 0, 0, 0, 0) 
    time.sleep(0.04)
    mouse_event(0x0010, 0, 0, 0, 0) 
    time.sleep(0.08)
    mouse_event(0x0002, 0, 0, 0, 0) 
    time.sleep(0.04)
    mouse_event(0x0004, 0, 0, 0, 0) 

# ============================================
# CAPTURE ENGINE
# ============================================

class CaptureStream:
    def __init__(self):
        self.frame = None
        self.lock = Lock()
        self.active = True
        self._junk = _MemoryManager() # Junk usage
        
    def start(self):
        Thread(target=self._stream, daemon=True).start()
        time.sleep(0.1)
        
    def _stream(self):
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            while self.active:
                try:
                    raw = sct.grab(monitor)
                    img = np.array(raw)
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    with self.lock:
                        self.frame = img
                    # Obfuscation: occasional dummy alloc within thread
                    if random.random() < 0.01:
                        self._junk._allocate_dummy()
                except:
                    pass
                time.sleep(0.03) 
    
    def read(self):
        with self.lock:
            return self.frame.copy() if self.frame is not None else None
    
    def stop(self):
        self.active = False

stream = None

def init_stream():
    global stream
    stream = CaptureStream()
    stream.start()

# ============================================
# VISION CORE
# ============================================

def load_assets():
    main_target = None
    if os.path.exists("target.png"):
        main_target = cv2.imread("target.png")
    
    elites = []
    i = 1
    while os.path.exists(f"elite{i}.png"):
        t = cv2.imread(f"elite{i}.png")
        if t is not None:
            gray = cv2.cvtColor(t, cv2.COLOR_BGR2GRAY)
            elites.append((f"elite{i}", t, gray))
        i += 1
    
    target_gray = cv2.cvtColor(main_target, cv2.COLOR_BGR2GRAY) if main_target is not None else None
    return main_target, target_gray, elites

def scan_image(gray_scene, gray_template, detection_threshold):
    if gray_template is None: return []
    
    th, tw = gray_template.shape[:2]
    ih, iw = gray_scene.shape[:2]
    
    if tw > iw or th > ih: return []
    
    res = cv2.matchTemplate(gray_scene, gray_template, cv2.TM_CCOEFF_NORMED)
    locs = np.where(res >= detection_threshold)
    
    pts = []
    for pt in zip(*locs[::-1]):
        pts.append((pt[0] + tw//2, pt[1] + th//2, res[pt[1], pt[0]]))
    
    final_pts = []
    for p in sorted(pts, key=lambda x: -x[2]):
        if not any(abs(p[0]-f[0]) < 40 and abs(p[1]-f[1]) < 40 for f in final_pts):
            final_pts.append(p)
    return final_pts

def get_nearest(points, center_x, center_y, min_dist=80):
    valid = [p for p in points if (p[0]-center_x)**2 + (p[1]-center_y)**2 > min_dist**2]
    if not valid: return None
    return min(valid, key=lambda p: (p[0]-center_x)**2 + (p[1]-center_y)**2)

# ============================================
# EXECUTION LOOP
# ============================================

def execute_logic(tgt_img, tgt_gray, elites, y_offset=80):
    sw = GetSystemMetrics(0)
    sh = GetSystemMetrics(1)
    cx, cy = sw // 2, sh // 2
    
    active = False
    
    print("\n" + "-"*50)
    print("  STATUS: READY")
    print("  Controls: F11 (Start) | F12 (Pause) | ESC (Exit)")
    print("-"*50)
    print("\nWaiting for signal...")
    
    check_security() # Run anti-debug check
    
    # Start Title Changer Thread
    Thread(target=set_random_title, daemon=True).start()
    
    while True:
        if GetAsyncKeyState(VK_ESCAPE) & 0x0001:
            break
        
        if GetAsyncKeyState(VK_F11) & 0x8000:
            if not active:
                active = True
                print("\n[>>] ACTIVE")
            time.sleep(0.2)
        
        if GetAsyncKeyState(VK_F12) & 0x8000:
            if active:
                active = False
                print("\n[||] PAUSED")
            time.sleep(0.2)
        
        if not active:
            time.sleep(0.05)
            continue
            
        try:
            curr_frame = stream.read()
            if curr_frame is None: continue
            
            curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
            
            # ELITE DETECTION
            elite_detected = False
            for _, _, e_gray in elites:
                if scan_image(curr_gray, e_gray, CONFIG['elite_threshold']):
                    elite_detected = True
                    break
            
            if elite_detected:
                print(">> Elite Detected")
                input_key(VK_SPACE, SCAN_SPACE, True) # Down
                
                timer = 0
                no_target = 0
                
                while timer < CONFIG['elite_timeout']:
                    time.sleep(CONFIG['check_interval'])
                    timer += CONFIG['check_interval']
                    
                    if GetAsyncKeyState(VK_ESCAPE) & 0x0001:
                        input_key(VK_SPACE, SCAN_SPACE, False)
                        return
                    
                    if GetAsyncKeyState(VK_F12) & 0x8000:
                        input_key(VK_SPACE, SCAN_SPACE, False)
                        active = False
                        print("\n[||] PAUSED")
                        break
                        
                    f2 = stream.read()
                    if f2 is None: continue
                    g2 = cv2.cvtColor(f2, cv2.COLOR_BGR2GRAY)
                    
                    is_present = any(scan_image(g2, eg, CONFIG['elite_threshold']) for _, _, eg in elites)
                    
                    if not is_present:
                        no_target += 1
                        if no_target >= 7:
                            input_key(VK_SPACE, SCAN_SPACE, False)
                            print(f">> Cleared ({timer}s)")
                            break
                    else:
                        no_target = 0
                else:
                    input_key(VK_SPACE, SCAN_SPACE, False)
                    print(">> Timeout")
                
                continue
            
            # STANDARD TARGET
            targets = scan_image(curr_gray, tgt_gray, CONFIG['target_threshold'])
            
            if targets:
                target = get_nearest(targets, cx, cy)
                if target:
                    tx, ty = target[0], target[1] + y_offset
                    simulate_click(tx, ty)
                    time.sleep(CONFIG['action_delay'])
                else:
                    rotate_camera()
            else:
                rotate_camera()
                
        except Exception:
            pass

# ============================================
# HELPERS
# ============================================

def capture_template(fname):
    print(f"\nCapturing '{fname}' in 3s...")
    time.sleep(3)
    with mss.mss() as sct:
        raw = np.array(sct.grab(sct.monitors[1]))
        img = cv2.cvtColor(raw, cv2.COLOR_BGRA2BGR)
    cv2.imwrite(f"{fname}.png", img)
    print(f"Saved {fname}.png")

def main():
    # Fake error to confuse simple analysis
    if len(os.listdir('.')) > 10000:
        _junk_math_operation(1, 1)

    print("\nExternal Automation Tool v1.2")
    
    tgt_img, tgt_gray, elites = load_assets()
    
    print(f"Stats: Target={'YES' if tgt_img is not None else 'NO'}, SubTargets={len(elites)}")
    print("\n[1] Setup Main Target")
    print("[2] Setup Sub Target")
    print("[3] Execute")
    
    opt = input("\nOption: ").strip()
    
    if opt == '1':
        capture_template("target")
        input("Crop 'target.png' and press Enter...")
        return main()
    
    if opt == '2':
        capture_template(f"elite{len(elites)+1}")
        input(f"Crop 'elite{len(elites)+1}.png' and press Enter...")
        return main()
    
    if opt == '3':
        init_stream()
        try:
            execute_logic(tgt_img, tgt_gray, elites, CONFIG['input_offset'])
        finally:
            if stream: stream.stop()

if __name__ == "__main__":
    main()
