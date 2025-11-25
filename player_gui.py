import os
import subprocess
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

RECORD_DIR = "../records"


def find_file(timestamp_str):
    # формат: 2025-01-31 15:22:10
    try:
        t = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None

    # файлы называются: YYYY-MM-DD_HH-MM-SS.mp4
    target_prefix = t.strftime("%Y-%m-%d_%H-%M-%S")

    for f in os.listdir(RECORD_DIR):
        if f.startswith(target_prefix):
            return os.path.join(RECORD_DIR, f)
    return None


def play_video(path):
    subprocess.Popen(["ffplay", "-autoexit", path])


def on_search():
    ts = entry.get().strip()
    if not ts:
        messagebox.showerror("Ошибка", "Введите дату и время!")
        return

    file_path = find_file(ts)
    if not file_path:
        messagebox.showinfo("Ничего не найдено",
                            "Фрагмент видео не найден.\n"
                            "Проверьте правильность даты и времени.")
        return

    play_video(file_path)


# ---------------- GUI -------------------

root = tk.Tk()
root.title("Поиск и воспроизведение видео")

label = tk.Label(root, text="Введите время (YYYY-MM-DD HH:MM:SS):")
label.pack(pady=5)

entry = tk.Entry(root, width=30)
entry.pack(pady=5)

btn = tk.Button(root, text="Найти и воспроизвести", command=on_search)
btn.pack(pady=10)

root.mainloop()
