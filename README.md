This is a [Splunk](http://www.splunk.com) modular input add-on (Splunk 5.0+) for polling message queues or topics via the __Streaming Text Oriented Messaging Protocol (STOMP)__ implementing the [Splunk Modular Inputs Framework](http://docs.splunk.com/Documentation/Splunk/latest/AdvancedDev/ModInputsIntro).

STOMP is a simple text-based protocol, designed for working with Message Oriented Middleware. It provides an interoperable wire format that allows STOMP clients to talk with any Message Broker supporting the protocol.

STOMP is currently supported by many popular MOM products such as [Apache ActiveMQ](http://activemq.apache.org/) or [RabbitMQ](http://www.rabbitmq.com/).

Quickstart
==========

Simply copy [stomp](https://github.com/allenta/splunk-stomp/tree/master/stomp) folder to `$SPLUNK_HOME/etc/apps/` and restart Splunk.

As any other modular input, you can configure it via `Manager > DataInputs` in your Splunk installation.

Development Notes
=================

Some useful recipes while developing. See [Developer tools for modular inputs](http://docs.splunk.com/Documentation/Splunk/latest/AdvancedDev/ModInputsDevTools) for further information.

- Preview the output of the script:

  ```
    $ export SPLUNK_HOME=/opt/splunk
    $ sudo $SPLUNK_HOME/bin/splunk cmd splunkd print-modinput-config stomp stomp://localhost:61613/queue/whatever | sudo $SPLUNK_HOME/bin/splunk cmd python $SPLUNK_HOME/etc/apps/stomp/bin/stomp.py
  ```

- Check script status in `https://localhost:8089/services/admin/inputstatus`.

- Any log entries/errors will get written to `$SPLUNK_HOME/var/log/splunk/splunkd.log`

Pending Tasks
-------------

- Scripts are NOT killed on Splunk restart. Consider dirty workarounds like [this](http://splunk-base.splunk.com/answers/69630/modular-input-scripts-dont-die-during-splunk-restart).

- Improve error handling.
