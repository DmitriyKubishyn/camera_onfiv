import bd_engine
from onvif_cams import CameraOperator
import rtsp_recorder
import async_rtsp_multi_recorder
import video_player
import asyncio
import datetime
import os

def main():
    # Настройки камеры (замените на свои)
    CAMERA_HOST = '10.10.10.10'
    CAMERA_PORT = 80
    USERNAME = 'onvif'
    PASSWORD = 'test_test'

    # Создание и настройка клиента
    viewer = CameraOperator(CAMERA_HOST, CAMERA_PORT, USERNAME, PASSWORD)

    # Подключение к камере
    if viewer.connect():
        # Получение информации о камере
        viewer.get_camera_info()
        # viewer.update_user(viewer.users[0].Username,"test_test")
        # viewer.update_resolution(1)
        # bd_engine.cam_saver(viewer)

    else:
        print("Не удалось подключиться к камере")




    async def routine():
        mgr = async_rtsp_multi_recorder.MultiCameraRecorder()

        # Добавляем камеры
        mgr.add_camera("front_door", "rtsp://onvif:test_test@10.10.10.10:554/Streaming/Channels/101?transportmode=unicast&profile=Profile_1")
        mgr.add_camera("back_yard",  "rtsp://rtspstream:iX357Xf2tGw-US0c7toZA@zephyr.rtsp.stream/movie")


        # Запустить все камеры
        await mgr.start_all()

        player = async_video_player.MultiRTSPPlayer()
        player.add_stream("front", "rtsp://onvif:test_test@10.10.10.10:554/Streaming/Channels/101?transportmode=unicast&profile=Profile_1")
        player.add_stream("yard", "rtsp://rtspstream:iX357Xf2tGw-US0c7toZA@zephyr.rtsp.stream/movie")

        print("Запись всех камер запущена. Ждём 2 минуты...")


        await player.start_all()


        try:
            await asyncio.sleep(120)
        finally:
            await mgr.stop_all()
            await player.stop_all()

    asyncio.run(routine())


    # async def routine():
    #     url = "rtsp://onvif:test_test@10.10.10.10:554/Streaming/Channels/101?transportmode=unicast&profile=Profile_1"
    #
    #     recorder = rtsp_recorder.AsyncRTSPRecorder(url, segment_seconds=30)
    #     await recorder.start()
    #
    #     print("Запись идёт... отмените Ctrl+C или подождите 100 секунд")
    #     try:
    #         await asyncio.sleep(100)
    #     finally:
    #         await recorder.stop()
    #
    # asyncio.run(routine())


if __name__ == "__main__":
    main()