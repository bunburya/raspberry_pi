from time import sleep
from io import BytesIO

from picamera import PiCamera

class RaspiCam:

    def __init__(self):
        self.camera = PiCamera()
        self.camera.resolution = (1024, 768)
        self.camera.vflip = True
        self.img_fmt = 'jpeg'

    def take_photo(self, fname=None):
        if fname:
            args = [fname]
        else:
            img_stream = BytesIO()
            args = [img_stream, self.img_fmt]
        self.camera.start_preview()
        sleep(2)
        self.camera.capture(*args)
        self.camera.stop_preview()
        if not fname:
            img_stream.close()
            return img_stream

    


