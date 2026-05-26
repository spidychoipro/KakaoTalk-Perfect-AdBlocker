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
SWP_NOOWNERZORDER = 0x0200
WM_CLOSE = 0x0010

EVENT_SYSTEM_FOREGROUND = 0x0003
EVENT_OBJECT_SHOW = 0x8002
OBJID_WINDOW = 0
WINEVENT_OUTOFCONTEXT = 0x0000
PM_REMOVE = 0x0001

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
MONITOR_DEFAULTTONEAREST = 2
ERROR_ALREADY_EXISTS = 183
MUTEX_NAME = "Local\\KakaoTalkPerfectAdBlocker"
DEFAULT_SCAN_INTERVAL = 0.1
MIN_EVENT_PUMP_INTERVAL = 0.02

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


class MSG(ctypes.Structure):
    _fields_ = (
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt", wintypes.POINT),
    )


EnumProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
WinEventProc = ctypes.WINFUNCTYPE(
    None,
    wintypes.HANDLE,
    wintypes.DWORD,
    wintypes.HWND,
    ctypes.c_long,
    ctypes.c_long,
    wintypes.DWORD,
    wintypes.DWORD,
)

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
user32.GetParent.argtypes = (wintypes.HWND,)
user32.GetParent.restype = wintypes.HWND
user32.ScreenToClient.argtypes = (wintypes.HWND, ctypes.POINTER(wintypes.POINT))
user32.ScreenToClient.restype = wintypes.BOOL
user32.ShowWindow.argtypes = (wintypes.HWND, ctypes.c_int)
user32.ShowWindow.restype = wintypes.BOOL
user32.PostMessageW.argtypes = (
    wintypes.HWND,
    wintypes.UINT,
    wintypes.WPARAM,
    wintypes.LPARAM,
)
user32.PostMessageW.restype = wintypes.BOOL
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
user32.SetWinEventHook.argtypes = (
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.HMODULE,
    WinEventProc,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.DWORD,
)
user32.SetWinEventHook.restype = wintypes.HANDLE
user32.UnhookWinEvent.argtypes = (wintypes.HANDLE,)
user32.UnhookWinEvent.restype = wintypes.BOOL
user32.PeekMessageW.argtypes = (
    ctypes.POINTER(MSG),
    wintypes.HWND,
    wintypes.UINT,
    wintypes.UINT,
    wintypes.UINT,
)
user32.PeekMessageW.restype = wintypes.BOOL
user32.TranslateMessage.argtypes = (ctypes.POINTER(MSG),)
user32.TranslateMessage.restype = wintypes.BOOL
user32.DispatchMessageW.argtypes = (ctypes.POINTER(MSG),)
user32.DispatchMessageW.restype = wintypes.LPARAM
user32.InvalidateRect.argtypes = (
    wintypes.HWND,
    ctypes.POINTER(RECT),
    wintypes.BOOL,
)
user32.InvalidateRect.restype = wintypes.BOOL
user32.UpdateWindow.argtypes = (wintypes.HWND,)
user32.UpdateWindow.restype = wintypes.BOOL
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


def has_ad_descendant_text(hwnd):
    for child_hwnd in enum_child_windows(hwnd):
        haystack = f"{get_window_class(child_hwnd)} {get_window_text(child_hwnd)}".lower()
        if any(keyword.lower() in haystack for keyword in AD_TEXT_KEYWORDS):
            return True
    return False


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


def screen_to_client(parent_hwnd, left, top):
    point = wintypes.POINT(left, top)
    if not user32.ScreenToClient(parent_hwnd, ctypes.byref(point)):
        return 0, 0
    return point.x, point.y


def set_child_window_rect(info, parent_hwnd, left, top, width, height):
    x, y = screen_to_client(parent_hwnd, left, top)
    return user32.SetWindowPos(
        info.hwnd,
        0,
        x,
        y,
        max(1, int(width)),
        max(1, int(height)),
        SWP_NOZORDER | SWP_NOOWNERZORDER | SWP_NOACTIVATE,
    )


def refresh_window(hwnd):
    user32.InvalidateRect(hwnd, None, True)
    user32.UpdateWindow(hwnd)


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
    marked_popup_size = 220 <= info.width <= 640 and 120 <= info.height <= 520
    marked_popup = (
        has_ad_descendant_text(info.hwnd)
        and inside_work_area
        and near_corner
        and marked_popup_size
    )

    return (
        has_ad_text(info)
        or marked_popup
        or (inside_work_area and near_corner and popup_size)
    )


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

    if has_ad_text(info) or has_ad_descendant_text(info.hwnd):
        return bottom_aligned and banner_size

    # Fallback for ad containers that expose no window title at all.
    return bottom_aligned and lower_half and banner_size and info.height >= 75


def is_bottom_ad_slot(info, main):
    if info.hwnd == main.hwnd:
        return False
    if not is_kakao_window(info):
        return False
    if has_safe_text(info):
        return False
    if info.width < 180 or info.height < 50:
        return False

    horizontal_overlap = overlap_width(info, main)
    if horizontal_overlap < min(info.width, main.width) * 0.70:
        return False

    bottom_gap = main.bottom - info.bottom
    top_offset = info.top - main.top
    width_ratio = info.width / max(main.width, 1)
    height_ratio = info.height / max(main.height, 1)

    return (
        -32 <= bottom_gap <= 140
        and top_offset > main.height * 0.45
        and width_ratio >= 0.62
        and height_ratio <= 0.35
    )


def should_extend_over_ad_slot(info, main, slot):
    if info.hwnd in (main.hwnd, slot.hwnd):
        return False
    if not is_kakao_window(info):
        return False
    if not info.visible:
        return False
    if info.width < 180 or info.height < main.height * 0.25:
        return False
    if info.top >= slot.top or info.bottom > slot.top + 36:
        return False
    if slot.top - info.bottom > 36:
        return False

    horizontal_overlap = overlap_width(info, slot)
    return horizontal_overlap >= min(info.width, slot.width) * 0.55


def collapse_bottom_ad_space(main, debug=False):
    collapsed = 0
    children = [get_window_info(hwnd) for hwnd in enum_child_windows(main.hwnd)]
    slots = [child for child in children if is_bottom_ad_slot(child, main)]

    for slot in slots:
        slot_parent = user32.GetParent(slot.hwnd) or main.hwnd
        set_child_window_rect(slot, slot_parent, slot.left, main.bottom - 1, slot.width, 1)
        hide_window(slot, "ad-space", debug)
        collapsed += 1

        for child in children:
            if should_extend_over_ad_slot(child, main, slot):
                child_parent = user32.GetParent(child.hwnd) or main.hwnd
                new_height = child.height + max(0, slot.bottom - child.bottom)
                set_child_window_rect(child, child_parent, child.left, child.top, child.width, new_height)
                collapsed += 1
                if debug:
                    print(
                        f"expanded content: hwnd={child.hwnd:#x} class={child.cls!r} "
                        f"old_rect={child.rect} new_height={new_height}"
                    )

    if collapsed:
        refresh_window(main.hwnd)

    return collapsed


def hide_window(info, reason, debug=False, close=False):
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
    if close:
        user32.PostMessageW(info.hwnd, WM_CLOSE, 0, 0)
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
            hide_window(info, "popup", debug, close=True)
            hidden += 1

    main_windows = [info for info in top_level_infos if is_probable_main_window(info)]
    for main in main_windows:
        for child_hwnd in enum_child_windows(main.hwnd):
            child = get_window_info(child_hwnd)
            if is_bottom_banner_ad(child, main):
                hide_window(child, "banner", debug)
                hidden += 1
        hidden += collapse_bottom_ad_space(main, debug)

    if debug and hidden == 0:
        print("no ad windows found")

    return hidden


def handle_window_event(hwnd, debug=False):
    if not hwnd:
        return False

    info = get_window_info(hwnd)
    if not is_kakao_window(info):
        return False

    if is_bottom_right_popup_ad(info):
        hide_window(info, "popup-event", debug, close=True)
        return True

    if is_probable_main_window(info):
        return collapse_bottom_ad_space(info, debug) > 0

    main_windows = [
        main
        for main in (get_window_info(parent) for parent in enum_windows())
        if is_probable_main_window(main)
    ]
    for main in main_windows:
        if info.hwnd != main.hwnd and is_bottom_banner_ad(info, main):
            hide_window(info, "banner-event", debug)
            collapse_bottom_ad_space(main, debug)
            return True

    return False


def install_event_hooks(debug=False):
    def callback(_hook, event, hwnd, object_id, child_id, _thread, _time):
        if object_id != OBJID_WINDOW or child_id != 0:
            return
        try:
            handle_window_event(hwnd, debug)
        except Exception as exc:
            if debug:
                print(f"event hook error: {exc!r}")

    event_proc = WinEventProc(callback)
    hooks = []

    for event in (EVENT_OBJECT_SHOW, EVENT_SYSTEM_FOREGROUND):
        hook = user32.SetWinEventHook(
            event,
            event,
            None,
            event_proc,
            0,
            0,
            WINEVENT_OUTOFCONTEXT,
        )
        if hook:
            hooks.append(hook)

    if debug:
        print(f"installed {len(hooks)} window event hook(s)")

    return hooks, event_proc


def uninstall_event_hooks(hooks):
    for hook in hooks:
        user32.UnhookWinEvent(hook)


def pump_window_events():
    msg = MSG()
    while user32.PeekMessageW(ctypes.byref(msg), 0, 0, 0, PM_REMOVE):
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))


def sleep_with_event_pump(duration):
    end_time = time.monotonic() + duration
    while True:
        pump_window_events()
        remaining = end_time - time.monotonic()
        if remaining <= 0:
            break
        time.sleep(min(MIN_EVENT_PUMP_INTERVAL, remaining))


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
    parser.add_argument(
        "--interval",
        type=float,
        default=DEFAULT_SCAN_INTERVAL,
        help="Scan interval in seconds.",
    )
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

    hooks = []
    event_proc = None
    try:
        if not args.once:
            hooks, event_proc = install_event_hooks(args.debug)

        while True:
            scan_once(debug=args.debug)
            if args.once:
                break
            sleep_with_event_pump(max(args.interval, 0.05))
    finally:
        uninstall_event_hooks(hooks)
        event_proc = None
        kernel32.CloseHandle(mutex)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
