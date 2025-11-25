import tkinter as tk
from tkinter import ttk, messagebox
import os
import cv2
from pathlib import Path


class VideoArchivePlayer:
    def __init__(self, root, folder_id="10.10.10.10"):
        self.root = root
        self.folder_id = folder_id
        self.root.title(f"Архив - {folder_id}")
        self.base_path = f"records/{folder_id}"

        self.current_file = None
        self.cap = None

        self.setup_ui()
        self.load_dates()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(main_frame, text="Выберите дату:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.date_vr = tk.StringVar()
        self.date_combo = ttk.Combobox(main_frame, textvariable=self.date_vr, state="readonly")
        self.date_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        self.date_combo.bind('<<ComboboxSelected>>', self.on_date_selected)


        ttk.Label(main_frame, text="Файлы:").grid(row=1, column=0, sticky=(tk.W, tk.N), pady=5)
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=(5, 0))

        self.file_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        self.file_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.file_listbox.bind('<Double-Button-1>', self.on_file_double_click)

    def load_dates(self):
        dates = []
        for item in os.listdir(self.base_path):
            dates.append(item)
        dates.sort(reverse=True)
        self.date_combo['values'] = dates
        if dates:
            self.date_combo.set(dates[0])
            print(self.date_combo.get())
            print(self.date_vr.get())
            self.on_date_selected()

    def on_date_selected(self, event=None):
        selected_date = self.date_vr.get()
        print(self.date_combo.get())
        print(self.date_vr.get())
        if not selected_date:
            return
        self.load_files_for_date(selected_date)

    def load_files_for_date(self, date):
        self.file_listbox.delete(0, tk.END)
        date_path = os.path.join(self.base_path, date)
        files = []
        for file in os.listdir(date_path):
            files.append(file)
        files.sort()  # Сортируем по времени
        for file in files:
            self.file_listbox.insert(tk.END, file)

    def on_file_double_click(self, event):
        self.play_video()

    def play_video(self):
        video_seected = self.file_listbox.curselection()
        if not video_seected:
            messagebox.showwarning("Предупреждение", "Выберите файл для воспроизведения")
            return

        self.current_file = os.path.join(self.base_path, self.date_vr.get(), self.file_listbox.get(video_seected[0]))
        self.play()

    def play(self):
        try:
            self.cap = cv2.VideoCapture(self.current_file)
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            delay = int(1000 / fps)

            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break
                cv2.imshow(f"{self.folder_id}", frame)
                cv2.waitKey(delay)

                if cv2.getWindowProperty(f"{self.folder_id}", cv2.WND_PROP_VISIBLE) < 1:
                    break

        except Exception as e:
            pass

