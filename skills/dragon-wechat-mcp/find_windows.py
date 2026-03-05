import win32gui

def find_wechat_windows(hwnd, windows):
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd)
        if title:
            rect = win32gui.GetWindowRect(hwnd)
            w = rect[2] - rect[0]
            h = rect[3] - rect[1]
            if w > 100:  # 只显示比较大的窗口
                windows.append((hwnd, title, rect, w, h))

windows = []
win32gui.EnumWindows(lambda h, ctx: find_wechat_windows(h, windows), None)

for hwnd, title, rect, w, h in windows:
    print(f'{hwnd}: "{title}" - {w}x{h} @ {rect}')
