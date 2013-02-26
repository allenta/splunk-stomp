Splunk STOMP Modular Input
==========================

This is a Splunk modular input add-on for polling message queues via the __Streaming Text Oriented Messaging Protocol (STOMP)__ implementing the [Splunk Modular Inputs Framework](http://docs.splunk.com/Documentation/Splunk/latest/AdvancedDev/ModInputsIntro). Check out [app/appserver/static/README.md](https://raw.github.com/allenta/splunk-stomp/master/stomp/appserver/static/README.md) for further information.

Quickstart
==========

Simply copy [stomp](https://github.com/allenta/splunk-stomp/tree/master/stomp) folder under `$SPLUNK_HOME/etc/apps/` and restart Splunk.

Pending Tasks
=============

- Script is NOT killed on Splunk restart. Consider dirty workarounds like [this](http://splunk-base.splunk.com/answers/69630/modular-input-scripts-dont-die-during-splunk-restart).

- Improve error handling.

Development Notes
=================

Some useful recipes while developing. See [Developer tools for modular inputs](http://docs.splunk.com/Documentation/Splunk/latest/AdvancedDev/ModInputsDevTools) for further information.

- Preview the output of the script:

  ```
    $ export SPLUNK_HOME=/opt/splunk
    $ sudo $SPLUNK_HOME/bin/splunk cmd splunkd print-modinput-config stomp stomp://localhost:61613/queue/whatever | sudo $SPLUNK_HOME/bin/splunk cmd python $SPLUNK_HOME/etc/apps/stomp/bin/stomp.py
  ```

- Check script status in `https://localhost:8089/services/admin/inputstatus`.
