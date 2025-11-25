
import subprocess
import time
import datetime
import os

class SimpleRTSPRecorder:
    def __init__(self, rtsp_url, folder, segment_duration=5):
        self.rtsp_url = rtsp_url
        self.segment_duration = segment_duration
        self.is_recording = False
        self.folder_path = os.path.join("records", folder, datetime.datetime.now().strftime("%Y-%m-%d"))
        os.makedirs(self.folder_path, exist_ok=True)

    def get_filename(self):
        current_time = datetime.datetime.now().strftime("%H-%M-%S")
        return f"{self.folder_path}/{current_time}.mp4"

    def start_segment(self):
        filename = self.get_filename()
        print(f"[INFO] Запись сегмента: {filename}")

        proc = subprocess.Popen([
            "ffmpeg",
            "-rtsp_transport", "tcp",
            "-i", self.rtsp_url,
            "-t", str(self.segment_duration),
            "-c", "copy",
            filename
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        return proc

    def record(self, duration=None):
        self.is_recording = True
        while self.is_recording:
            p = self.start_segment()

            # ждём завершения сегмента (или выхода)
            start_t = time.time()
            while time.time() - start_t < self.segment_duration:
                if self.is_recording == False:
                    p.kill()
                time.sleep(0.1)

            # сегмент завершён
            p.wait()

    def stop(self):
        self.is_recording = False

if __name__ == "__main__":
    pass