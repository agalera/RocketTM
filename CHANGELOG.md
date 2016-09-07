# CHANGELOG
## 2.0.4 (2016-09-07)
 - implemented heartbeat
 - fix ack failed for loss connection

## 2.0.3 (2016-09-07)
 - prevent relaunch finish task

## 2.0.2 (2016-09-07)
 - Change prefetch to 1

## 2.0.1 (2016-09-06)
 - Reuse connection in send_tasks

## 2.0.0 (2016-09-06)
 - Migrate pika to kambu

## 1.0.16 (2016-09-06)
 - Fix ack

## 1.0.8 - 1.0.15 (2016-09-06)
 - clean code

## 1.0.8 - 1.0.13 (2016-09-05)
 - fix timeouts and other exceptions

## 1.0.7 (2016-09-05)
 - fix rabbitmq ack timeout

## 1.0.6 (2016-08-26)
 - retry sending the message to the queue 5 times before returning an exception
 - When you add in the queue fails, now returns an exception
 
## 1.0.5 (2016-08-26)
 - timekiller stop propagate
 - fix inmortal server

## 1.0.4 (2016-08-25)
 - run tasks in safe and asolated proccess

## 1.0.3 (2016-08-25)
 - Solved multiple errors with disconnection with RabbitMQ
 - Update python compatibility (py2.x no loger supported)

## 1.0.2 (2016-08-23)
 - Fix automatic declare queues

## 1.0.1 (2016-08-22)
 - send_task now sends the set ip 

## 1.0.0 (2016-07-19)
 - Added callback support
 - generate uuid for task
 - all tasks get _id in first attr
 - if multiple tasks with the same name, if continued with the following fails
 - prevent connection closed to send_task (automatic reconnect)

## 0.2.6 (2016-07-15)
 - py3 compatibility
 - fix hardcoding durable
 - ignore not exists logger config


## 0.2.5 (2016-07-15)
 - py3 compatibility

## 0.2.4 (2016-07-15)
 - Fix automatic declare queue

## 0.2.3 (2016-06-14)
 - Add new dependency (timekiller)

## 0.2.2 (2016-06-14)
 - hotfix bad raise

## 0.2.1 (2016-06-14)
  - Hotfix rabbitmq_server command

## 0.2.0 (2016-06-13)
  - add support timeout (tasks and queues)

## 0.1.1 (2016-04-27)
  - Fix dependencies

## 0.1.0 (2016-03-22)
  - Permit change log

## 0.0.4 (2016-03-21)
  - Fix CHANGELOG
  - Update README

## 0.0.3 (2016-03-21)
  - Permit connect different rabbitmq server
  - Prevent channel_closed
  - Support durable queues

## 0.0.2 (2016-03-14)
  - Add documentation

## 0.0.1 (2016-03-14)
  - initial version
