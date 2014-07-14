from io import BytesIO
import time

from dataplicity.client.task import Task
import picamera
from pygame import mixer

import scanimage


class TakePhoto(Task):
    """Take a photo with the Raspberry Pi camera"""
    RESOLUTION = (1024, 768)

    def init(self):
        """Initialize the task"""
        self.timeline_name = self.conf.get('timeline', 'camera')
        self.frame_no = 1
        self.camera = None
        self.scan_image = scanimage.ScanImage()

    def on_startup(self):
        """Start the camera and return the camera instance"""
        self.camera = camera = picamera.PiCamera()
        self.log.debug('Raspberry Pi camera set resolution')
        camera.resolution = self.RESOLUTION
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
        self.camera.capture('tmp.png')

        # Get the timeline
        timeline = self.client.get_timeline(self.timeline_name)

        results = self.scan_image.process()
        if not results:
            self.log.debug('Nothing to analyse')
        else:
            description = 'Normalised drop percent: {}, level: {}'.format(
                    results['normalised_drop_percent'],
                    results['level'],
                    )

            # Create a new event photo
            event = timeline.new_photo(camera_file,
                    title="Frame {:06}".format(self.frame_no),
                    text=description,
                    ext="jpeg")
            # Write the event
            event.write()
            # Keep track of the frame number
            self.frame_no += 1

            # play a sount
            mixer.init()
            alert=mixer.Sound('beep1.wav')
            alert.play()

