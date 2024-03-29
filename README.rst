Uploads Agent
=============

This is a Celery-based application that subscribes to an ``uploads`` AMQP
queue which is populated by one of TACC's minio servers in respose to
file uploads to a specific bucket. This application processes messages in
this queue, which take the form of SQS-compatible ``s3:ObjectCreated:Put``
documents. Filesystem upload events are processed as follows:

First, the event is stored in a MongoDB collection (``_fsevents``),
indexed on its unqiue Amazon Filesystem Event Identifier. A ``state`` and
``history`` field are also stored with the document to track progress and
history of processing the upload. Next, a request is dispatched to the
``uploads-manager.prod`` Reactor, requesting that it copy the data from the S3
resource to a TACC POSIX storage resource. The event identifier is propagated
along with this request to allow for future, downstream correlation analyses.
Once the request has been dispatched, it is monitored by a non-blocking
Celery task. This task, in addition to checking the state of the task
execution, updates the MongoDB record for the filesystem event with the
status of the execution. If a failure is detected in executing the task,
a background task is dispatched to send notifcations over email and/or Slack.

Concurrency
-----------

The application can safely manage multiple concurrent uploads, including
performing the appropriate state monitoring. To provide thread-saftety,
concurrent execution is managed by >1 workers, each of which has its own
dedicated Oauth2 client for interacting with the Tapis APIs.

Adding a new Worker
~~~~~~~~~~~~~~~~~~~

The system is currently configured with four workers. To add another worker:

    - Use ``tapis clients create`` to create a new Oauth client, taking care to record its api key and secret
    - Extend ``file://config.yml#tapis.clients`` with a new client stanza.
    - Add a new worker to ``docker-compose.yml``

Managing the System
-------------------

TBD

Notifications
-------------

The system is capable of sending notifications via email (using Mailgun) or
Slack. Configuration for which configuration channels to use is at
``config.yml#notifications``. Mailgun configured by ``config.yml#mailgun`` and
Slack by ``config.yml#slack``. As these are mediated by web service APIs
(and to prevent filling people's inboxes), these calls are rate-limited.
These rates are configurable by editing the task definitions.

Status.IO
~~~~~~~~~

The system is also capable of sending Status.IO notifications on its own behalf.
Configuration is via ``config.yml#statusio``.

Periodic Tasks
--------------

The system has three periodic tasks configured in ``proj/periodic_actions.py``.
Specific actions can be added to this module, and are expected to be added to
the ``daily``, ``weekly``, and ``monthly`` group tasks defined at the
top of the module.
