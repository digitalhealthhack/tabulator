import time
from io import BytesIO

import picamera

from dataplicity.client.task import Task


class TakePhoto(Task):
    """Take a photo with the Raspberry Pi camera"""

    def init(self):
        """Initialize the task"""
        self.timeline_name = self.conf.get('timeline', 'camera')
        self.frame_no = 1
        self.camera = None

    def on_startup(self):
        """Start the camera and return the camera instance"""
        self.camera = camera = picamera.PiCamera()
        #camera.resolution = (640, 480)
        self.log.debug('Raspberry Pi camera set resolution')
        camera.resolution = (1024, 768)
        self.log.debug('Raspberry Pi camera started')

    def on_shutdown(self):
        # Gracefully close the camera
        self.camera.close()

    def poll(self):
        # Write a frame to memory
        self.log.debug('Say CHEESE!')
        camera_file = BytesIO()
        self.log.debug('Camera warmup')

        self.camera.start_preview()
        time.sleep(2)
        self.log.debug('CHEEEEZ!')
        self.camera.capture(camera_file, 'jpeg')

        # Get the timeline
        timeline = self.client.get_timeline(self.timeline_name)

        # Create a new event photo
        event = timeline.new_photo(camera_file,
                                   title="Frame {:06}".format(self.frame_no),
                                   text="Captured by the Raspberry Pi Camera",
                                   ext="jpeg")
        # Write the event
        event.write()
        # Keep track of the frame number
        self.frame_no += 1
