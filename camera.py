import cv2
from naoqi import ALProxy
import vision_definitions
from PIL import Image
import numpy

class VideoCamera(object):
    def __init__(self):
        IP = "127.0.0.1"  # Replace here with your NAOqi's IP address.
        PORT = 9559
        self.camProxy = ALProxy("ALVideoDevice", IP, PORT)

        # Register a Generic Video Module
        resolution = vision_definitions.kQVGA  # 320 * 240
        colorSpace = vision_definitions.kRGBColorSpace
        fps = 30

        self.nameId = self.camProxy.subscribe("python_GVM", resolution, colorSpace, fps)

    def __del__(self):
        self.camProxy.unsubscribe(self.nameId)

    def get_frame(self):
        naoImage = self.camProxy.getImageRemote(self.nameId)

         # Get the image size and pixel array.
        imageWidth = naoImage[0]
        imageHeight = naoImage[1]
        array = naoImage[6]

        # Create a PIL Image from our pixel array.
        try:
            im = Image.fromstring("RGB", (imageWidth, imageHeight), array)
        except:
            im = Image.frombytes("RGB", (imageWidth, imageHeight), array)

        #im = im.rotate(180)

        cv_im = numpy.array(im)
        # Convert RGB to BGR
        cv_im = cv_im[:, :, ::-1].copy()

        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.
        ret, jpeg = cv2.imencode('.jpg', cv_im)
        return jpeg.tobytes()
