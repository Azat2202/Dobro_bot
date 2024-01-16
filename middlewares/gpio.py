# It was made for my home Raspberry Pi to signal the amount of requests
from random import randint

from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from gpiozero import LEDBoard, LEDBarGraph

gpio_available = True

try:
    white_pins = [14, 15, 17, 18, 24, 10, 12, 26, 21]
    yellow_pins = [16, 19, 13]

    white_leds = LEDBoard(*white_pins)
    white_leds_count = len(white_pins)
    yellow_leds = LEDBarGraph(*yellow_pins, pwm=True)
    yellow_leds_count = len(yellow_pins)
except:
    gpio_available = False


class GPIOBlinker(BaseMiddleware):
    def __init__(self):
        super(GPIOBlinker, self).__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        if not gpio_available: return
        if message.is_command():
            yellow_leds[randint(0, yellow_leds_count - 1)].blink(4, n=1)
        else:
            white_leds[randint(0, white_leds_count - 1)].blink(1.5, n=1)
