import asyncio
import datetime
import os


class AsyncRTSPRecorder:
    def __init__(self, name, rtsp_url, output_dir="records", segment_seconds=30):
        self.name = name
        self.rtsp_url = rtsp_url
        self.output_dir = os.path.join(output_dir, name)
        self.segment_seconds = segment_seconds
        os.makedirs(self.output_dir, exist_ok=True)

        self.process = None
        self.running = False

    async def start(self):
        if self.running:
            print(f"[{self.name}] Уже записывается")
            return

        self.running = True

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_pattern = os.path.join(self.output_dir, f"{self.name}_{timestamp}_%03d.mp4")

        cmd = [
            "ffmpeg",
            "-rtsp_transport", "tcp",
            "-i", self.rtsp_url,
            "-c", "copy",
            "-f", "segment",
            "-segment_time", str(self.segment_seconds),
            "-reset_timestamps", "1",
            output_pattern,
        ]

        print(f"[{self.name}] Старт записи → {self.output_dir}")

        self.process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        asyncio.create_task(self._log_ffmpeg())

    async def _log_ffmpeg(self):
        while self.process:
            line = await self.process.stderr.readline()
            if not line:
                break
            print(f"[{self.name}][ffmpeg] {line.decode(errors='ignore').strip()}")

    async def stop(self):
        if not self.running:
            return

        print(f"[{self.name}] Остановка...")
        self.running = False

        if self.process:
            self.process.terminate()
            await self.process.wait()
            self.process = None

        print(f"[{self.name}] Остановлена")


# -------------------- Менеджер нескольких камер --------------------

class MultiCameraRecorder:
    def __init__(self):
        self.recorders = {}

    def add_camera(self, name, rtsp_url, segment_seconds=30):
        recorder = AsyncRTSPRecorder(name, rtsp_url, segment_seconds=segment_seconds)
        self.recorders[name] = recorder

    async def start_all(self):
        await asyncio.gather(*(r.start() for r in self.recorders.values()))

    async def stop_all(self):
        await asyncio.gather(*(r.stop() for r in self.recorders.values()))


# ----------------------- Пример использования -----------------------

# if __name__ == "__main__":
#     async def main():
#         mgr = MultiCameraRecorder()
#
#         # Добавляем камеры
#         mgr.add_camera("front_door", "rtsp://admin:1@192.168.1.10/stream1")
#         mgr.add_camera("back_yard",  "rtsp://admin:1@192.168.1.11/stream1")
#         mgr.add_camera("garage",     "rtsp://admin:1@192.168.1.12/stream1")
#
#         # Запустить все камеры
#         await mgr.start_all()
#
#         print("Запись всех камер запущена. Ждём 2 минуты...")
#         try:
#             await asyncio.sleep(120)
#         finally:
#             await mgr.stop_all()
#
#     asyncio.run(main())
