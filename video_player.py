import cv2
import time

def play_rtsp(url, window_name="RTSP Player"):
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    while True:
        print("Подключение к камере...")
        cap = cv2.VideoCapture(url)

        if not cap.isOpened():
            print("❌ Не удалось открыть поток. Повтор через 2 секунды...")
            time.sleep(2)
            continue

        print("✔ Поток открыт.")

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if width > 0 and height > 0:
            print(f"Разрешение потока: {width}x{height}")
            cv2.resizeWindow(window_name, width, height)

        while True:
            ret, frame = cap.read()

            if not ret:
                print("⚠ Поток прервался. Переподключение...")
                cap.release()
                break

            cv2.imshow(window_name, frame)
            cv2.waitKey(25)

            if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                print("⏹ Остановка воспроизведения")
                cap.release()
                cv2.destroyAllWindows()
                return


