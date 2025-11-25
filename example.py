import asyncio
import datetime

from archive_index import ArchiveIndex
from async_archive_player import AsyncArchivePlayer


async def main():
    # выбираем камеру
    index = ArchiveIndex("front_door")

    # диапазон для просмотра
    start_dt = datetime.datetime(2023, 11, 23, 0, 0, 0)
    end_dt   = datetime.datetime(2026, 11, 23, 23, 59, 59)

    # находим нужные сегменты
    files = index.get_range(start_dt, end_dt)
    print("Найдено сегментов:", len(files), files)

    # запускаем плеер
    player = AsyncArchivePlayer("FrontCamArchive")
    await player.play_segments(files)


if __name__ == "__main__":
    asyncio.run(main())
