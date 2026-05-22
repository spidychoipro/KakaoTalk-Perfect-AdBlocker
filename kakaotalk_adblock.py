
import ctypes
from ctypes import wintypes
import time
import threading

user32 = ctypes.windll.user32
SW_HIDE = 0
SW_SHOW = 5

def get_window_text(hwnd):
    length = user32.GetWindowTextLengthW(hwnd)
    if length > 0:
        buff = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        return buff.value
    return ""

def get_window_class(hwnd):
    buff = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buff, 256)
    return buff.value

def get_window_rect(hwnd):
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    return rect.left, rect.top, rect.right, rect.bottom

def is_ad_window(hwnd, main_rect):
    cls = get_window_class(hwnd)
    if cls != "EVA_Window_Dblclk" and cls != "EVA_Window":
        return False
    
    text = get_window_text(hwnd)
    if text != "": # Ads usually have no title or specific internal titles
        if "ContactListView" in text or "ChatRoomListView" in text or "MoreView" in text or "카카오톡" in text:
            return False
            
    rect = get_window_rect(hwnd)
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]
    
    # Typical banner size is around 80-100 height
    if 50 < h < 150 and w > 200:
        # Check if it's inside or near the bottom of the main window
        if main_rect[0] <= rect[0] <= main_rect[2] and rect[3] <= main_rect[3] + 10:
            return True
            
    # Popup ads are usually small and at the bottom right of the screen
    # But for now, let's focus on the banner.
    return False

def block_ads():
    while True:
        main_hwnd = user32.FindWindowW("EVA_Window_Dblclk", "카카오톡")
        if main_hwnd:
            main_rect = get_window_rect(main_hwnd)
            
            def callback(hwnd, lparam):
                if is_ad_window(hwnd, main_rect):
                    # Hide the window
                    if user32.IsWindowVisible(hwnd):
                        user32.ShowWindow(hwnd, SW_HIDE)
                        # Also move it out of the way just in case
                        user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 0x0080) # SWP_HIDEWINDOW
                return True
            
            WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
            user32.EnumWindows(WNDENUMPROC(callback), 0)
            user32.EnumChildWindows(main_hwnd, WNDENUMPROC(callback), 0)
            
        time.sleep(2) # Check every 2 seconds

if __name__ == "__main__":
    print("KakaoTalk Perfect AdBlocker started...")
    block_ads()
