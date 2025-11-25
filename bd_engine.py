from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import datetime

class Base(DeclarativeBase): pass

def simple_logger(logData):
    with open ("simple_log.txt", "a") as f:
        f.write(f"{datetime.datetime.now()} - {logData}\n")

class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, autoincrement=True)
    camera_host = Column(String, nullable=False)
    camera_port = Column(Integer, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    model = Column(String, nullable=True)
    rtsp_url = Column(String, nullable=True)


engine = create_engine("sqlite:///cameras.db")
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def add_camera(cameraoperator):
    simple_logger(f"add_camera : camera_host - {cameraoperator.host}, camera_port - {cameraoperator.port}, username - {cameraoperator.username}, password - {cameraoperator.password},"
                  f"model - {cameraoperator.model}, rtsp_url - {cameraoperator.rtsp_url}")
    camera = session.query(Camera).filter_by(camera_host=cameraoperator.host).first()
    if camera:
        simple_logger(f"Камера была добавлена ранее: ID={camera.id}")
        return f"Камера была добавлена ранее: ID={camera.id}"

    else:
        camera = Camera(
            camera_host=cameraoperator.host,
            camera_port=cameraoperator.port,
            username=cameraoperator.username,
            password=cameraoperator.password,
            model=cameraoperator.model,
            rtsp_url=cameraoperator.rtsp_url,
        )
        session.add(camera)
        session.commit()
        simple_logger(f"Добавлена камера ID={camera.id}")
        return f"Добавлена камера ID={camera.id}"

def update_camera(cameraoperator, camera_id):
    simple_logger(f"update_camera : camera_id={camera_id}, kwargs={cameraoperator.host}")
    camera = session.query(Camera).filter_by(id=camera_id).first()
    if not camera:
        simple_logger("Камера не найдена")
        return "Камера не найдена"

    camera.camera_host = cameraoperator.host
    camera.camera_port = cameraoperator.port
    camera.username = cameraoperator.username
    camera.password = cameraoperator.password
    camera.model = cameraoperator.model
    camera.rtsp_url = cameraoperator.rtsp_url

    session.commit()
    simple_logger(f"Камера ID={camera_id} обновлена")
    return f"Камера ID={camera_id} обновлена"

def delete_camera(camera_id):
    simple_logger(f"delete_camera : camera_id={camera_id}")
    camera = session.query(Camera).filter_by(id=camera_id).first()
    if not camera:
        simple_logger("Камера не найдена")
        return

    session.delete(camera)
    session.commit()
    simple_logger(f"Камера ID={camera_id} удалена")

def get_all_cameras():
    camera = session.query(Camera).all()
    if not camera:
        simple_logger("Камеры не найдены")
        return False
    return camera

def cam_saver(cameraoperator):
    simple_logger(f"cam_saver : camera_host - {cameraoperator.host}, camera_port - {cameraoperator.port}, username - {cameraoperator.username}, password - {cameraoperator.password}")
    camera = session.query(Camera).filter_by(camera_host=cameraoperator.host).first()
    if camera:
        cameraoperator.model = session.query(Camera).filter_by(camera_host=cameraoperator.host).first().model
        return update_camera(cameraoperator, camera.id)
    else:
        return add_camera(cameraoperator)
