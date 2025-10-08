import subprocess
import tempfile
import customtkinter as ctk
from tkinter import messagebox
import os
import shutil

# === CẤU HÌNH GIAO DIỆN ===
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# 🔍 TÌM FILE AutoHotkey (ưu tiên các tên thường gặp)
def find_autohotkey():
    possible_paths = [
        r"C:\Program Files\AutoHotkey\AutoHotkeyU64.exe",
        r"C:\Program Files\AutoHotkey\AutoHotkey.exe",
    ]

    for name in ["AutoHotkeyU64.exe", "AutoHotkey64.exe", "AutoHotkey.exe"]:
        ahk_path = shutil.which(name)
        if ahk_path:
            return ahk_path

    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None


# 🧩 HÀM CHẠY CODE AHK
def run_ahk_script():
    num = selected_num.get()
    width = entry_width.get().strip()
    height = entry_height.get().strip()
    mode = layout_mode.get()

    if not (width.isdigit() and height.isdigit()):
        messagebox.showerror("Lỗi", "Vui lòng nhập độ phân giải màn hình hợp lệ (số nguyên)!")
        return

    MonitorWidth = int(width)
    MonitorHeight = int(height)
    desired_num = int(num)

    # Nếu nhập trên 4 → không cho dàn Dọc 100%
    if desired_num > 4 and mode == "Dọc 100%":
        messagebox.showinfo("Chế độ bị vô hiệu hóa",
                            "❌ 'Dọc 100%' chỉ hỗ trợ tối đa 4 Chrome.\nHãy chọn '70% layout' thay thế.")
        return

    # --- CODE AHK ---
    ahk_code = fr"""
#NoEnv
#SingleInstance Force
SetTitleMatchMode, 2

; === Chrome Layout Tool (AutoHotkey v1) ===
WinGet, chromeList, List, ahk_exe chrome.exe

numChrome := chromeList
numDesired := {desired_num}
if (numChrome < 1)
{{
    MsgBox, Không phát hiện cửa sổ Chrome nào!
    return
}}

if (numDesired < 1)
{{
    numToArrange := numChrome
}}
else if (numDesired > numChrome)
{{
    MsgBox, Có %numChrome% cửa sổ Chrome đang mở. Sẽ dàn %numChrome% cửa sổ (không đủ số bạn yêu cầu).
    numToArrange := numChrome
}}
else
{{
    numToArrange := numDesired
}}

MonitorWidth := {MonitorWidth}
MonitorHeight := {MonitorHeight}
layoutMode := "{mode}"

if (layoutMode = "70% layout")
{{
    resizeFactor := 0.7
    if (numToArrange <= 8)
    {{
        rows := 2
        cols := (numToArrange < 4) ? numToArrange : 4
    }}
    else if (numToArrange <= 10)
    {{
        rows := 2
        cols := 5
    }}
    else
    {{
        rows := Ceil(numToArrange / 4)
        cols := 4
    }}

    WindowWidth := Round((MonitorWidth / cols) * resizeFactor)
    WindowHeight := Round((MonitorHeight / rows) * resizeFactor)

    index := 1
    Loop %rows%
    {{
        row := A_Index - 1
        Loop %cols%
        {{
            col := A_Index - 1
            if (index > numToArrange)
                break
            hwnd := chromeList%index%
            WinRestore, ahk_id %hwnd%
            x := col * WindowWidth
            y := row * WindowHeight
            WinMove, ahk_id %hwnd%, , x, y, WindowWidth, WindowHeight
            index++
        }}
    }}
}}
else if (layoutMode = "Dọc 100%")
{{
    ; Dàn dọc toàn màn hình — tự điều chỉnh overlap
    if (numToArrange < 4)
        overlap := 0
    else if (numToArrange = 4)
        overlap := 10
    else if (numToArrange = 5)
        overlap := 14

    totalWidth := MonitorWidth
    WindowWidth := Floor(totalWidth / numToArrange)
    WindowHeight := MonitorHeight

    Loop %numToArrange%
    {{
        hwnd := chromeList%A_Index%
        WinRestore, ahk_id %hwnd%

        ; Tính vị trí X
        x := (A_Index - 1) * (WindowWidth - overlap)
        y := 0

        ; Cửa sổ cuối cùng luôn khít phải màn hình
        if (A_Index = numToArrange)
            w := MonitorWidth - x
        else
            w := WindowWidth

        WinMove, ahk_id %hwnd%, , x, y, w, WindowHeight
    }}
}}

MsgBox, ✅ Đã dàn thành công %numToArrange% cửa sổ Chrome theo chế độ %layoutMode% trên màn hình {MonitorWidth}x{MonitorHeight}!
return
"""

    # --- Ghi ra file .ahk tạm ---
    with tempfile.NamedTemporaryFile(suffix=".ahk", delete=False, mode="w", encoding="utf-8") as f:
        f.write(ahk_code)
        temp_ahk = f.name

    ahk_path = find_autohotkey()
    if not ahk_path:
        messagebox.showerror(
            "Không tìm thấy AutoHotkey",
            "Không tìm thấy AutoHotkey (v1).\nTải tại: https://www.autohotkey.com/download/1.1/"
        )
        return

    try:
        subprocess.run([ahk_path, temp_ahk])
    except Exception as e:
        messagebox.showerror("Lỗi khi chạy AHK", str(e))


# === GIAO DIỆN CHÍNH ===
app = ctk.CTk()
app.title("Chrome Layout Tool v1")
app.geometry("480x420")
app.resizable(False, False)

title = ctk.CTkLabel(app, text="🧩 Chrome Layout Tool v1", font=ctk.CTkFont(size=20, weight="bold"))
title.pack(pady=15)

frame = ctk.CTkFrame(app, corner_radius=15)
frame.pack(pady=10, padx=20, fill="both", expand=True)

# 🔢 Chọn số lượng Chrome (3–12)
label_chrome = ctk.CTkLabel(frame, text="Chọn số lượng Chrome cần dàn:", font=ctk.CTkFont(size=14))
label_chrome.pack(pady=8)
selected_num = ctk.StringVar(value="4")
num_options = [str(i) for i in range(3, 13)]
num_menu = ctk.CTkOptionMenu(frame, variable=selected_num, values=num_options)
num_menu.pack(pady=5)


# Độ phân giải
label_res = ctk.CTkLabel(frame, text="Độ phân giải màn hình:", font=ctk.CTkFont(size=14))
label_res.pack(pady=(10, 5))

res_frame = ctk.CTkFrame(frame)
res_frame.pack(pady=5)

entry_width = ctk.CTkEntry(res_frame, width=80, height=35, placeholder_text="Rộng")
entry_width.grid(row=0, column=0, padx=5)
entry_height = ctk.CTkEntry(res_frame, width=80, height=35, placeholder_text="Cao")
entry_height.grid(row=0, column=1, padx=5)

def set_resolution(res):
    w, h = res.split("x")
    entry_width.delete(0, "end")
    entry_height.delete(0, "end")
    entry_width.insert(0, w)
    entry_height.insert(0, h)

preset_res = ["1920x1080", "2560x1440", "3840x2160"]
res_option = ctk.CTkOptionMenu(frame, values=preset_res, command=set_resolution)
res_option.set("2560x1440")
res_option.pack(pady=8)


# Chế độ dàn trang
label_mode = ctk.CTkLabel(frame, text="Chọn chế độ dàn cửa sổ:", font=ctk.CTkFont(size=14))
label_mode.pack(pady=(10, 5))
layout_mode = ctk.StringVar(value="70% layout")
mode_option = ctk.CTkOptionMenu(frame, variable=layout_mode, values=["70% layout", "Dọc 100%"])
mode_option.pack(pady=5)

# 🔄 Tự động bật/tắt chế độ “Dọc 100%” khi chọn số Chrome
def update_mode_availability(choice):
    num = int(choice)
    if num > 4:
        if layout_mode.get() == "Dọc 100%":
            layout_mode.set("70% layout")
        mode_option.configure(values=["70% layout"])
    else:
        mode_option.configure(values=["70% layout", "Dọc 100%"])

num_menu.configure(command=update_mode_availability)


# Nút dàn trang
btn = ctk.CTkButton(frame, text="🚀 DÀN TRANG", width=180, height=40, command=run_ahk_script)
btn.pack(pady=15)

credit = ctk.CTkLabel(app, text="Developed by Minh Quân • AutoHotkey v1 Integration", font=ctk.CTkFont(size=10))
credit.pack(side="bottom", pady=10)

app.mainloop()
