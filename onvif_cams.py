from onvif import ONVIFCamera
import bd_engine

class CameraOperator:
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.camera = None
        self.media_service = None
        self.profiles = None
        self.users = None
        self.model = None
        self.profile_token = None
        self.options = None
        self.rtsp_url = None

    def connect(self):
        try:
            self.camera = ONVIFCamera(
                self.host,
                self.port,
                self.username,
                self.password
            )

            self.media_service = self.camera.create_media_service()
            self.profiles = self.media_service.GetProfiles()
            self.profile_token = self.profiles[0]["VideoEncoderConfiguration"].token
            self.options = self.media_service.GetVideoEncoderConfigurationOptions({
                'ConfigurationToken': self.profile_token
            })
            self.users = self.camera.devicemgmt.GetUsers()
            self.model = self.camera.devicemgmt.GetDeviceInformation().Model
            self.rtsp_url = self.get_rtsp_stream_url()

            bd_engine.simple_logger(f"Успешно подключено к камере {self.host}")
            bd_engine.simple_logger(f"Доступно профилей: {len(self.profiles)}")

            return True

        except Exception as e:
            bd_engine.simple_logger(f"Ошибка подключения: {e}")
            return False

    def get_rtsp_stream_url(self, profile_index=0):
        try:
            stream_setup = {
                'Stream': 'RTP-Unicast',
                'Transport': {
                    'Protocol': 'RTSP'
                }
            }
            profile_token = self.profiles[profile_index].token
            stream_uri = self.media_service.GetStreamUri(
                {
                    'StreamSetup': stream_setup,
                    'ProfileToken': profile_token
                }
            )
            rtsp_url = stream_uri.Uri
            if self.username and self.password:
                url_parts = rtsp_url.split('://')
                self.rtsp_url = f"{url_parts[0]}://{self.username}:{self.password}@{url_parts[1]}"

            return self.rtsp_url

        except Exception as e:
            print(f"Ошибка получения RTSP URL: {e}")
            return None

    def get_camera_info(self):
        try:
            print("=== Информация об устройстве ===")
            print(f"Модель: {self.model}")

            print("\n=== Пользователи ===")
            for i, user in enumerate(self.users):
                print(f"Номер пользователя: {i}")
                print(f"  Имя пользователя: {user.Username}")
                print(f"  Уровень доступа: {user.UserLevel}")

            print("\n=== Профили ===")
            for i, profile in enumerate(self.profiles):
                print(f"Профиль {i}: {profile.Name}")
                print(f"  Разрешение: {profile.VideoEncoderConfiguration.Resolution}")
                print(f"  Качество: {profile.VideoEncoderConfiguration.Quality}")

            print("\n=== Доступные разрешения ===")
            for i, option in enumerate(self.options.H264.ResolutionsAvailable):
                print(f"Доступные разрешения для профиля {i}:")
                print(f"  Width: {option.Width}")
                print(f"  Height: {option.Height}")

        except Exception as e:
            print(f"Ошибка получения информации: {e}")

    def update_user(self, username, new_pass, userlevel):
        try:
            user_data = {
                'Username': username,
                'Password': new_pass,
                'UserLevel': userlevel,
                }
            self.camera.devicemgmt.SetUser(user_data)
            return True
        except Exception as e:
            bd_engine.simple_logger("Ошибка записи данных пользователя")
            return False


    def update_resolution(self, profile_id):
        profile_dump = self.profiles[0].VideoEncoderConfiguration
        setattr(profile_dump.Resolution, "Width", self.options.H264.ResolutionsAvailable[profile_id].Width)
        setattr(profile_dump.Resolution, "Height",self.options.H264.ResolutionsAvailable[profile_id].Height)
        self.media_service.SetVideoEncoderConfiguration({
            'Configuration': profile_dump,
            'ForcePersistence': True  # Сохранить настройки после перезагрузки
        })
        self.profiles = self.media_service.GetProfiles()