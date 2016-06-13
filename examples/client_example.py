from rockettm import send_task
import logging

logging.basicConfig(level=20)
send_task("rocket1", "function3", "h", "o", "l", "a")
