import time
import stomp
import logging


logging.basicConfig(level=10)


class MyListener(stomp.ConnectionListener):
    def on_error(self, headers, message):
        print('received an error "%s"' % message)

    def on_message(self, headers, message):
        print('received a message "%s"' % message)
        for x in range(50):
            print(x)
            time.sleep(1)
        print('finish')


conn = stomp.Connection()#heartbeats=(4000, 4000))
conn.set_listener('', MyListener())
conn.start()
conn.connect('guest', 'guest', wait=True)
conn.subscribe(destination='/queue/rocket1', id=1, ack='auto')
#while conn.is_connected():
time.sleep(60)
conn.disconnect()
