import asyncio
import cv2


class AsyncArchivePlayer:
    """
    Асинхронный плеер для последовательного воспроизведения
    нескольких сегментов как единого непрерывного видео.
    """

    def __init__(self, window_name="ArchivePlayer"):
        self.window_name = window_name
        self.running = False

    async def play_segments(self, files):
        """
        files – список путей к сегментам,
        полученный из ArchiveIndex.get_range()
        """
        if not files:
            print("Нет сегментов для воспроизведения")
            return

        self.running = True
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)

        print(f"▶ Старт воспроизведения {len(files)} сегментов")

        for file in files:
            if not self.running:
                break

            print(f"Открываем: {file}")
            cap = cv2.VideoCapture(file)
            if not cap.isOpened():
                print(f"Не удалось открыть {file}")
                continue

            fps = cap.get(cv2.CAP_PROP_FPS)
            delay = 1 / fps if fps > 0 else 0.033

            while self.running:
                ret, frame = cap.read()
                if not ret:
                    break

                cv2.imshow(self.window_name, frame)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    self.running = False
                    break

                await asyncio.sleep(delay)

            cap.release()

        cv2.destroyWindow(self.window_name)
        print("⏹ Воспроизведение завершено")

    async def stop(self):
        self.running = False
