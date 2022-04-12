import json
import time
import Adafruit_PCA9685
import paho.mqtt.client as mqtt

# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685()

# Alternatively specify a different address and/or bus:
# pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)

# Configure min and max servo pulse lengths
servo_min = 150  # Min pulse length out of 4096
servo_max = 600  # Max pulse length out of 4096

commands = []


class ServoController():
    def __init__(self, xDefault, yDefault):
        self.defaults = (xDefault, yDefault)
        self.xLooking = int(xDefault)
        self.yLooking = int(yDefault)

    def move_x(self, amount):
        if servo_min < (self.xLooking + int(amount)) < servo_max:
            print("servo moved")
            self.xLooking = (self.xLooking + int(amount))
            pwm.set_pwm(0, 0, self.xLooking)

    def move_y(self, amount):
        if servo_min < (self.yLooking + int(amount)) < servo_max:
            print("servo moved")
            self.yLooking = (self.yLooking + int(amount))
            pwm.set_pwm(1, 0, self.yLooking)

    def return_to_default(self):
        print("servo moved")
        pwm.set_pwm(0, 0, self.defaults[0])
        pwm.set_pwm(1, 0, self.defaults[1])


# Helper function to make setting a servo pulse width simpler.
def set_servo_pulse(channel, pulse):
    pulse_length = 1000000  # 1,000,000 us per second
    pulse_length //= 60  # 60 Hz
    print('{0}us per period'.format(pulse_length))
    pulse_length //= 4096  # 12 bits of resolution
    print('{0}us per bit'.format(pulse_length))
    pulse *= 1000
    pulse //= pulse_length
    #pwm.set_pwm(channel, 0, pulse)


# broker = "broker.hivemq.com"
# port = 1883


def on_message(client, userdata, msg):
    m_decode = str(msg.payload.decode("utf-8", "ignore"))
    m_in = json.loads(m_decode)
    print(m_in)
    commands.append(m_in)


# Set frequency to 60hz, good for servos.
pwm.set_pwm_freq(60)

print('Moving servo on channel 0, press Ctrl-C to quit...')


topic = "test/json_test333"
client = mqtt.Client("pythontest86858")
client.on_message = on_message
# print("Connecting to broker ", "broker.hivemq.com")
#client.connect("192.168.1.144")
client.connect("broker.hivemq.com")
client.loop_start()
client.subscribe(topic)
client.subscribe("test/json_test3")
client.subscribe("test/json_test1")


# time.sleep(1)

def Test_msg():
    brokers_out = {
        "servo1": "-10",
        "servo2": "20"
    }
    data_out = json.dumps(brokers_out)
    return data_out

pwm.set_pwm(0, 0, 150)
pwm.set_pwm(1, 0, 650)

servo_controller = ServoController(300, 300)
while True:
    # Move servo on channel O between extremes.
    # pwm.set_pwm(2, 0, 500)
    if len(commands) > 0:
        commands_dict = commands[0]
        if commands_dict.get('servo1'):
            servo_controller.move_x(commands_dict.get('servo1'))
        if commands_dict.get('servo2'):
            servo_controller.move_y(commands_dict.get('servo2'))
        commands.pop(0)
    time.sleep(0.1)
    client.publish(topic, Test_msg())

client.loop_stop()
