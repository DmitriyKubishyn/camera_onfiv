import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import bd_engine
from onvif_cams import CameraOperator
import video_player
import rtsp_recorder
import threading
import archive_player

class ResEditor(tk.Toplevel):
    def __init__(self, master, camera=None):
        super().__init__(master)
        self.title("Разрешение")
        self.camera = camera
        resolutions = []
        options = []
        print(self.camera[1].options)
        if hasattr(self.camera[1].options.H264, 'ResolutionsAvailable'):
            for res in self.camera[1].options.H264.ResolutionsAvailable:
                resolutions.append([res.Width, res.Height])

        for res in resolutions:
            options.append (f"{res[0]}*{res[1]}")

        self.selected_option = tk.IntVar(self)
        self.selected_option.set(0)

        for i, option_text in enumerate(options):
            radio_btn = ttk.Radiobutton(
                self,
                text=option_text,
                variable=self.selected_option,
                value=i,
                command=self.on_radio_select
            )
            radio_btn.pack(anchor="w", padx=10, pady=2)

        app.text_logger(f"Выбрано разрешение: ID={self.selected_option.get()}")

        btn = tk.Button(self, text="Сохранить", command=self.save)
        btn.pack(side="bottom", fill="y")

    def on_radio_select(self):
        app.text_logger(f"Выбрано разрешение: ID={self.selected_option.get()}")

    def save(self):
        self.camera[1].update_resolution(self.selected_option.get())
        app.text_logger(f"Установлено разрешение: ID={self.selected_option.get()}\n")

        self.master.init_camera_list()
        self.destroy()


class CameraEditor(tk.Toplevel):
    def __init__(self, master, camera=None):
        super().__init__(master)
        self.title("Камера")
        self.camera = camera


        tk.Label(self, text="IP:").grid(row=0, column=0)
        tk.Label(self, text="Порт:").grid(row=1, column=0)
        tk.Label(self, text="Имя пользователя:").grid(row=2, column=0)
        tk.Label(self, text="Пароль:").grid(row=3, column=0)
        tk.Label(self, text="Имя камеры:").grid(row=4, column=0)


        self.host = tk.Entry(self)
        self.port = tk.Entry(self)
        self.user = tk.Entry(self)
        self.pwd = tk.Entry(self)
        self.name = tk.Entry(self)


        self.host.grid(row=0, column=1)
        self.port.grid(row=1, column=1)
        self.user.grid(row=2, column=1)
        self.pwd.grid(row=3, column=1)
        self.name.grid(row=4, column=1)

        btn = tk.Button(self, text="Сохранить", command=self.save)
        btn.grid(row=6, column=0, columnspan=2)

        if self.camera:
            if self.camera[-1]:
                self.host.insert(0, camera[0].camera_host)
                self.port.insert(0, camera[0].camera_port)
                self.name.insert(0, camera[0].model)
                self.user.insert(0, camera[0].username)


    def save(self):
        name = self.name.get()
        host = self.host.get()
        port = self.port.get()
        user = self.user.get()
        pwd = self.pwd.get()

        if self.camera:
            if self.camera[-1]: # обновление камеры
                if self.camera[1].update_user(user, pwd, self.camera[1].users[0].UserLevel):
                    self.camera[1].host = host
                    self.camera[1].port = port
                    self.camera[1].username = user
                    self.camera[1].password = pwd
                    self.camera[1].model = name
                    print(self.camera[1].model)
                    bd_engine.update_camera(self.camera[1], self.camera[0].id)
                    app.text_logger(f"Обновление камеры - {self.camera[0].id}\n")
        else: # добавление новой камеры
            viewer = CameraOperator(host, port, user, pwd)
            if viewer.connect():
                app.text_logger(f"Добавление камеры - {bd_engine.cam_saver(viewer)}\n")

        self.master.init_camera_list()
        self.destroy()


class CameraApp(tk.Tk):
    def __init__(self):
        self.cam_dict = {}
        self.cameras = list()
        super().__init__()
        self.title("Камера")

        # Список камер
        self.cam_list = tk.Listbox(self, width=40)
        self.cam_list.pack(side="left", fill="y")
        self.cam_list.bind("<<ListboxSelect>>", self.on_select)

        # Панель кнопок
        btns = tk.Frame(self)
        btns.pack(side="right", fill="both", expand=True)

        tk.Button(btns, text="Добавить", command=self.add_camera).pack(fill="x")
        tk.Button(btns, text="Изменить", command=self.edit_camera).pack(fill="x")
        tk.Button(btns, text="Удалить", command=self.delete_camera_btn).pack(fill="x")
        tk.Button(btns, text="Воспроизвести", command=self.play_stream).pack(fill="x")
        tk.Button(btns, text="Запись", command=self.start_recording).pack(fill="x")
        tk.Button(btns, text="Архив", command=self.open_archive).pack(fill="x")
        tk.Button(btns, text="Разрешение", command=self.change_resolution).pack(fill="x")

        self.textbox = tk.Text(self)
        self.textbox.pack(side="right", fill="both", expand=True)

        self.init_camera_list()

    def text_logger(self, text):
        self.textbox.insert("end", f"{text}\n")
        self.textbox.see("end")

    def init_camera_list(self):
        self.cam_list.delete(0, tk.END)
        cameras = bd_engine.get_all_cameras()
        for cam in cameras:
            viewer = CameraOperator(cam.camera_host, cam.camera_port, cam.username, cam.password)
            self.text_logger(f"Камера: {cam.camera_host}")
            if viewer.connect():
                self.cameras.append([cam, viewer, True])
                self.text_logger(f"{bd_engine.cam_saver(viewer)}\n")
                bg = "white"
            else:
                self.cameras.append([cam, False])
                self.text_logger("Соединение с камерой не установлено\n")
                bg = "red"
            self.cam_list.insert(tk.END, f"{cam.id}: {cam.camera_host}: {cam.model}")
            self.cam_list.itemconfig(tk.END, {'bg' : bg})

    def refresh_camera_list(self):
        self.cam_list.delete(0, tk.END)
        self.cameras = bd_engine.get_all_cameras()
        print(self.cameras)
        for c in self.cameras:
            self.cam_list.insert(tk.END, f"{c.id}: {c.camera_host}: {c.model}")

    def get_selected_camera(self):
        idx = self.cam_list.curselection()
        if not idx:
            messagebox.showwarning("Выбор", "Камера не выбрана")
            return None
        return self.cameras[idx[0]]

    def add_camera(self):
        CameraEditor(self)

    def edit_camera(self):
        cam = self.get_selected_camera()
        if cam[-1]:
            CameraEditor(self, cam)
        else:
            messagebox.showwarning("Изменение", f"Камера ID={cam[0].id} - недоступна!")

    def delete_camera_btn(self):
        cam = self.get_selected_camera()
        if not cam:
            return

        if messagebox.askyesno("Удалить", "Удалить выбранную камеру?"):
            bd_engine.delete_camera(cam[0].id)
            self.init_camera_list()

    def change_resolution(self):
        cam = self.get_selected_camera()
        if cam[-1]:
            ResEditor(self, cam)
        else:
            messagebox.showwarning("Изменение", f"Камера ID={cam[0].id} - недоступна!")

    def play_stream(self):
        cam = self.get_selected_camera()
        if not cam: return
        rtsp_url = cam[0].rtsp_url
        video_player.play_rtsp(rtsp_url)

    def start_recording(self):
        cam = self.get_selected_camera()
        if not cam: return

        rec = rtsp_recorder.SimpleRTSPRecorder(cam[0].rtsp_url, cam[0].camera_host)
        thread = threading.Thread(target=rec.record)
        thread.start()
        a = messagebox.showinfo("Запись", f"Идёт запись для камеры - {cam[0].camera_host}")
        if a: rec.stop()
        thread.join()
        self.text_logger("Запись завершена\n")


    def open_archive(self):
        cam = self.get_selected_camera()
        if not cam: return
        a = archive_player.VideoArchivePlayer(tk.Toplevel(), cam[0].camera_host)

    def on_select(self, ev):
        pass

if __name__ == "__main__":
    app = CameraApp()
    app.mainloop()
