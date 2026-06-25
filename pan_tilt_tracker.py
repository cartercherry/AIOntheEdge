from adafruit_servokit import ServoKit

class PanTiltTracker:
    def __init__(self, channels = 16, pan_pin = 0, tilt_pin=1):
        self.kit = ServoKit(channels=channels)
        self.pan_servo = self.kit.servo[pan_pin]
        self.tilt_servo = self.kit.servo[tilt_pin]
        self.pan_servo.actuation_range = 180
        self.tilt_servo.actuation_range = 180

    def set_pan(self, angle):
        """ Accepts -90 (Right) to 90 (Left).  0 is Center"""
        # Clamp the angle value
        safe_angle = max(-90, min(angle,90))
        # Translate to the Library's 0-180 scale
        self.pan_servo.angle = safe_angle + 90

    def set_tilt(self, angle):
        """ Accepts -90 (Down) to 90 (Up).  0 is Center"""
        safe_angle = max(-90, min(angle, 90))
        self.tilt_servo.angle = 90 -safe_angle

# Useage:  cam_mount = PanTiltTracker()
#          cam_mount.set_pan(0)    Looks straight ahead
#          cam_mount.set_pan(-45)  Pans 45 degrees clockwise
#          cam_mount.set_tilt(45)  Looks UP 45 degrees  
