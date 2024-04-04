import flight.vision.camera as camera
import time


if __name__ == "__main__":

    camera_ids = [0]
    manager = camera.CameraManager(camera_ids)
    manager.turn_on_cameras()

    for i in range(5):
        print(f"Capturing image {i}")
        manager.capture_images()
        frames = manager.get_available_frames()
        print(frames)
        manager.show(frames[0])
        time.sleep(1)

    manager.turn_off_cameras(camera_ids)
