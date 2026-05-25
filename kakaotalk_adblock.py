from __future__ import annotations

import argparse
import ctypes
import os
import time
from ctypes import wintypes
from dataclasses import dataclass


user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

SW_HIDE = 0
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_NOZORDER = 0x0004
SWP_NOACTIVATE = 0x0010
SWP_HIDEWINDOW = 0x0080

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
MONITOR_DEFAULTTONEAREST = 2
ERROR_ALREADY_EXISTS = 183
MUTEX_NAME = "Local\\KakaoTalkPerfectAdBlocker"

KAKAO_PROCESS = "kakaotalk.exe"
KAKAO_WINDOW_CLASSES = {
    "EVA_Window",
    "EVA_Window_Dblclk",
    "EVA_ChildWindow",
    "EVA_Window_Dblclk_C",
}
AD_TEXT_KEYWORDS = (
    "광고",
    "advert",
    "advertisement",
    "adfit",
    "kakao business",
    "kakao ad",
    "sponsored",
)
SAFE_TEXT_KEYWORDS = (
    "ContactListView",
    "ChatRoomListView",
    "MoreView",
    "BuddyListView",
    "LoginView",
    "SettingView",
    "ProfileView",
)


class RECT(ctypes.Structure):
    _fields_ = (
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    )


class MONITORINFO(ctypes.Structure):
    _fields_ = (
        ("cbSize", wintypes.DWORD),
        ("rcMonitor", RECT),
        ("rcWork", RECT),
        ("dwFlags", wintypes.DWORD),
    )


EnumProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

user32.EnumWindows.argtypes = (EnumProc, wintypes.LPARAM)
user32.EnumWindows.restype = wintypes.BOOL
user32.EnumChildWindows.argtypes = (wintypes.HWND, EnumProc, wintypes.LPARAM)
user32.EnumChildWindows.restype = wintypes.BOOL
user32.GetWindowTextLengthW.argtypes = (wintypes.HWND,)
user32.GetWindowTextLengthW.restype = ctypes.c_int
user32.GetWindowTextW.argtypes = (wintypes.HWND, wintypes.LPWSTR, ctypes.c_int)
user32.GetWindowTextW.restype = ctypes.c_int
user32.GetClassNameW.argtypes = (wintypes.HWND, wintypes.LPWSTR, ctypes.c_int)
user32.GetClassNameW.restype = ctypes.c_int
user32.GetWindowRect.argtypes = (wintypes.HWND, ctypes.POINTER(RECT))
user32.GetWindowRect.restype = wintypes.BOOL
user32.IsWindowVisible.argtypes = (wintypes.HWND,)
user32.IsWindowVisible.restype = wintypes.BOOL
user32.GetWindowThreadProcessId.argtypes = (wintypes.HWND, ctypes.POINTER(wintypes.DWORD))
user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.ShowWindow.argtypes = (wintypes.HWND, ctypes.c_int)
user32.ShowWindow.restype = wintypes.BOOL
user32.SetWindowPos.argtypes = (
    wintypes.HWND,
    wintypes.HWND,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_uint,
)
user32.SetWindowPos.restype = wintypes.BOOL
user32.MonitorFromWindow.argtypes = (wintypes.HWND, wintypes.DWORD)
user32.MonitorFromWindow.restype = wintypes.HMONITOR
user32.GetMonitorInfoW.argtypes = (wintypes.HMONITOR, ctypes.POINTER(MONITORINFO))
user32.GetMonitorInfoW.restype = wintypes.BOOL
user32.GetSystemMetrics.argtypes = (ctypes.c_int,)
user32.GetSystemMetrics.restype = ctypes.c_int

kernel32.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
kernel32.OpenProcess.restype = wintypes.HANDLE
kernel32.QueryFullProcessImageNameW.argtypes = (
    wintypes.HANDLE,
    wintypes.DWORD,
    wintypes.LPWSTR,
    ctypes.POINTER(wintypes.DWORD),
)
kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
kernel32.CloseHandle.restype = wintypes.BOOL
kernel32.CreateMutexW.argtypes = (wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR)
kernel32.CreateMutexW.restype = wintypes.HANDLE


@dataclass(frozen=True)
class WindowInfo:
    hwnd: int
    cls: str
    text: str
    rect: tuple[int, int, int, int]
    visible: bool
    pid: int
    process: str

    @property
    def left(self):
        return self.rect[0]

    @property
    def top(self):
        return self.rect[1]

    @property
    def right(self):
        return self.rect[2]

    @property
    def bottom(self):
        return self.rect[3]

    @property
    def width(self):
        return max(0, self.right - self.left)

    @property
    def height(self):
        return max(0, self.bottom - self.top)


def get_window_text(hwnd):
    length = user32.GetWindowTextLengthW(hwnd)
    if length <= 0:
        return ""

    buff = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buff, length + 1)
    return buff.value


def get_window_class(hwnd):
    buff = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buff, 256)
    return buff.value


def get_window_rect(hwnd):
    rect = RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        return 0, 0, 0, 0
    return rect.left, rect.top, rect.right, rect.bottom


def get_process_id(hwnd):
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return pid.value


def get_process_name(pid):
    if not pid:
        return ""

    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not handle:
        return ""

    try:
        size = wintypes.DWORD(32768)
        buff = ctypes.create_unicode_buffer(size.value)
        if kernel32.QueryFullProcessImageNameW(handle, 0, buff, ctypes.byref(size)):
            return os.path.basename(buff.value).lower()
    finally:
        kernel32.CloseHandle(handle)

    return ""


def get_window_info(hwnd):
    pid = get_process_id(hwnd)
    return WindowInfo(
        hwnd=hwnd,
        cls=get_window_class(hwnd),
        text=get_window_text(hwnd),
        rect=get_window_rect(hwnd),
        visible=bool(user32.IsWindowVisible(hwnd)),
        pid=pid,
        process=get_process_name(pid),
    )


def enum_windows():
    handles = []

    def callback(hwnd, _lparam):
        handles.append(hwnd)
        return True

    user32.EnumWindows(EnumProc(callback), 0)
    return handles


def enum_child_windows(parent_hwnd):
    handles = []

    def callback(hwnd, _lparam):
        handles.append(hwnd)
        return True

    user32.EnumChildWindows(parent_hwnd, EnumProc(callback), 0)
    return handles


def get_monitor_work_area(hwnd):
    monitor = user32.MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST)
    info = MONITORINFO()
    info.cbSize = ctypes.sizeof(MONITORINFO)

    if monitor and user32.GetMonitorInfoW(monitor, ctypes.byref(info)):
        rect = info.rcWork
        return rect.left, rect.top, rect.right, rect.bottom

    return 0, 0, user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


def has_ad_text(info):
    haystack = f"{info.cls} {info.text}".lower()
    return any(keyword.lower() in haystack for keyword in AD_TEXT_KEYWORDS)


def has_safe_text(info):
    return any(keyword in info.text for keyword in SAFE_TEXT_KEYWORDS)


def is_kakao_window(info):
    if info.process:
        return info.process == KAKAO_PROCESS
    return info.cls in KAKAO_WINDOW_CLASSES


def is_probable_main_window(info):
    if not info.visible:
        return False
    if not is_kakao_window(info):
        return False
    if info.width < 260 or info.height < 300:
        return False
    if has_ad_text(info):
        return False
    return True


def overlap_width(a, b):
    return max(0, min(a.right, b.right) - max(a.left, b.left))


def is_bottom_right_popup_ad(info):
    if not info.visible or not is_kakao_window(info):
        return False
    if info.text.strip() in ("카카오톡", "KakaoTalk"):
        return False
    if has_safe_text(info):
        return False

    # Recent KakaoTalk popup ads can appear while the main chat window is hidden.
    # They sit above the taskbar near the right edge and are much taller than
    # normal message notifications.
    work_left, work_top, work_right, work_bottom = get_monitor_work_area(info.hwnd)
    gap_right = work_right - info.right
    gap_bottom = work_bottom - info.bottom
    inside_work_area = (
        info.left >= work_left - 32
        and info.top >= work_top - 32
        and info.right <= work_right + 32
        and info.bottom <= work_bottom + 48
    )
    near_corner = -32 <= gap_right <= 180 and -32 <= gap_bottom <= 180
    popup_size = 240 <= info.width <= 560 and 150 <= info.height <= 430

    return has_ad_text(info) or (inside_work_area and near_corner and popup_size)


def is_bottom_banner_ad(info, main):
    if not info.visible or info.hwnd == main.hwnd:
        return False
    if not is_kakao_window(info):
        return False
    if has_safe_text(info):
        return False

    horizontal_overlap = overlap_width(info, main)
    if horizontal_overlap < min(info.width, main.width) * 0.65:
        return False

    bottom_gap = main.bottom - info.bottom
    top_offset = info.top - main.top
    width_ratio = info.width / max(main.width, 1)
    height_ratio = info.height / max(main.height, 1)

    bottom_aligned = -24 <= bottom_gap <= 120
    lower_half = top_offset > main.height * 0.35
    banner_size = (
        info.width >= 180
        and 45 <= info.height <= 300
        and width_ratio >= 0.50
        and height_ratio <= 0.45
    )

    if has_ad_text(info):
        return bottom_aligned and banner_size

    # Fallback for ad containers that expose no window title at all.
    return bottom_aligned and lower_half and banner_size and info.height >= 75


def hide_window(info, reason, debug=False):
    user32.ShowWindow(info.hwnd, SW_HIDE)
    user32.SetWindowPos(
        info.hwnd,
        0,
        0,
        0,
        0,
        0,
        SWP_HIDEWINDOW | SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE,
    )
    if debug:
        print(
            f"hidden {reason}: hwnd={info.hwnd:#x} class={info.cls!r} "
            f"text={info.text!r} rect={info.rect} pid={info.pid}"
        )


def scan_once(debug=False):
    hidden = 0
    top_level_infos = [get_window_info(hwnd) for hwnd in enum_windows()]

    for info in top_level_infos:
        if is_bottom_right_popup_ad(info):
            hide_window(info, "popup", debug)
            hidden += 1

    main_windows = [info for info in top_level_infos if is_probable_main_window(info)]
    for main in main_windows:
        for child_hwnd in enum_child_windows(main.hwnd):
            child = get_window_info(child_hwnd)
            if is_bottom_banner_ad(child, main):
                hide_window(child, "banner", debug)
                hidden += 1

    if debug and hidden == 0:
        print("no ad windows found")

    return hidden


def create_single_instance_mutex():
    ctypes.set_last_error(0)
    handle = kernel32.CreateMutexW(None, True, MUTEX_NAME)
    if not handle:
        return None
    last_error = ctypes.get_last_error()
    if last_error == ERROR_ALREADY_EXISTS:
        kernel32.CloseHandle(handle)
        return None
    return handle


def parse_args():
    parser = argparse.ArgumentParser(description="Hide KakaoTalk PC ad windows.")
    parser.add_argument("--debug", action="store_true", help="Print detected windows.")
    parser.add_argument("--once", action="store_true", help="Scan once and exit.")
    parser.add_argument("--interval", type=float, default=0.5, help="Scan interval in seconds.")
    return parser.parse_args()


def main():
    args = parse_args()
    mutex = create_single_instance_mutex()
    if mutex is None:
        if args.debug:
            print("KakaoTalk Perfect AdBlocker is already running.")
        return 0

    if args.debug:
        print("KakaoTalk Perfect AdBlocker started...")

    try:
        while True:
            scan_once(debug=args.debug)
            if args.once:
                break
            time.sleep(max(args.interval, 0.1))
    finally:
        kernel32.CloseHandle(mutex)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
