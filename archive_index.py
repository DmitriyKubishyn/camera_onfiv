import os
import datetime
import bisect


class ArchiveIndex:
    """
    Индекс архива одной камеры.
    Хранит список сегментов и позволяет быстро искать сегмент по времени.
    """

    def __init__(self, camera_name, base_dir="records"):
        self.camera_name = camera_name
        self.archive_path = os.path.join(base_dir, camera_name)
        self.segments = []            # список путей
        self.timestamps = []          # список datetime начала каждого сегмента

        self._scan()

    # ---------------------------------------------------------------

    def _parse_timestamp(self, filename):
        """
        Имя сегмента имеет вид:
        front_20250101_120000_003.mp4
              ^^^^^^^ date    ^time
        """
        try:
            base = os.path.basename(filename)
            parts = base.split("_")
            date = parts[2]               # 20250101
            time = parts[3]               # 120000
            dt = datetime.datetime.strptime(date + time, "%Y%m%d%H%M%S")
            print(dt)
            return dt
        except Exception:
            return None

    # ---------------------------------------------------------------

    def _scan(self):
        """Сканирование сегментов камеры, создание индексных списков."""
        if not os.path.exists(self.archive_path):
            return

        files = [
            os.path.join(self.archive_path, f)
            for f in os.listdir(self.archive_path)
            if f.endswith(".mp4")
        ]
        print(files)
        timestamps = []
        good_files = []

        for f in files:
            ts = self._parse_timestamp(f)
            if ts:
                timestamps.append(ts)
                good_files.append(f)

        # сортируем по времени
        data = sorted(zip(timestamps, good_files), key=lambda x: x[0])
        print(data)
        self.timestamps = [x[0] for x in data]
        self.segments = [x[1] for x in data]

    # ---------------------------------------------------------------

    def rescan(self):
        """Если запись идёт — можно обновить индекс."""
        self._scan()

    # ---------------------------------------------------------------

    def find_segment(self, dt: datetime.datetime):
        """
        Быстрый бинарный поиск сегмента по времени.
        Возвращает индекс сегмента или None.
        """
        if not self.timestamps:
            return None

        pos = bisect.bisect_right(self.timestamps, dt) - 1
        if pos == -1:
            pos = 0
        print(pos, self.timestamps, dt)
        if pos < 0 or pos >= len(self.timestamps):
            return None

        return pos

    # ---------------------------------------------------------------

    def get_range(self, start_dt, end_dt):
        """
        Вернуть список сегментов, покрывающих диапазон времени.
        """
        print(start_dt, end_dt)
        start_idx = self.find_segment(start_dt)
        if start_idx is None:
            return []

        end_idx = self.find_segment(end_dt)
        if end_idx is None:
            end_idx = len(self.segments) - 1

        return self.segments[start_idx:end_idx + 1]
