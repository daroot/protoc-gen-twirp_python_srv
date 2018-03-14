# Twirp Python Server Generator

Generate a Python WSGI application that can answer
[Twirp](https://github.com/twitchtv/twirp) requests.

The general design of this generator was taken from [Chris Gaffney's ruby
client generator](https://github.com/gaffneyc/protoc-gen-twirp_ruby).

## Install

```bash
go get -u github.com/daroot/protoc-gen-twirp_python_srv
```

## Requirements

Code from the generator requires the following libraries:

- [protobuf](https://github.com/google/protobuf) - For protobuf (de)serialization.
- [Werkzeug](http://werkzeug.pocoo.org/) - used for WSGI request parsing.
- [Blinker](https://github.com/jek/blinker) - For request and response hooks.
- [enum34](https://pypi.python.org/pypi/enum34) - for python3.3 or earlier, including python 2.x

Additionally in order to use the resulting applicaiton,  you'll need a WSGI
capable server (such as gunicorn or uwsgi) or a library capable of acting as a
standalone server (like bjoern, gevent, or werkzeug's internal debugging
server).

## Usage

```bash
protoc --proto_path=$GOPATH/src:. --twirp_python_srv_out=. --python_out=. path/to/service.proto
```

Create service, using [bjoern](https://github.com/jonashaag/bjoern) as a WSGI
server:

```python
import random

import bjoern
import haberdasher_pb2 as pb
from haberdasher_twirp_srv import (Errors, HaberdasherImpl, HaberdasherServer,
                                   TwirpException)

class MadHaberdasher(HaberdasherImpl):
    def MakeHat(self, size):
        if size.Inches <= 0:
            raise TwirpException(Errors.InvalidArgument,
                                 "I can't make a hat that small")
        return pb.Hat(Size=size.Inches,
                      Color=random.choice("white", "black", "brown", "red"),
                      Name=random.choice("bowler", "top hat", "derby"))

if __name__ == "__main__":
    app = HaberdasherServer(MadHaberdasher())
    bjoern.run(app, "0.0.0.0", 8080)
```


## Signals

The generated server code uses the Blinker library to emit signals at various
points in the request processing to match the capabilities of Twirp Go's
`context.Context` and `twirp.ServerHooks`.  Applications can `connect` to one
or more of the following signals in order to do authentication, metrics,
logging, tracing, or other similar per-request tasks:

- *request-received*: Upon receiving a request via the WSGI server, before determining which endpoint it will be delivered to.  ctx['request'] contains the `werkzeug.wrappers.Request` object.
- *request-routed*: Once the endpoint is determined.  ctx['endpoint'] now contains the service rpc endpoint name.
- *response-prepared*: After the endpoint method is invoked and the protobuf response generated.  ctx['response'] contains the `werkzeug.wrappers.Response` object including the serialized return value and headers.
- *response-sent*:  Called just before the response is returned to the WSGI server to be sent to the client, once all processing is done and status code is determined.
- *error-occurred*: If any part of the WSGI or request handling fails.

Each signal handler receives a 'context' dictionary, which contains the current
state of processing.  The same context object is used throughout the entire
request/response processing, so it may be used to store temporary data such as
timing or latency information for use in later signal handlers.

Any number of handlers may be connected to each signal so that independent
packages can handle various tasks, but per Blinker's documentation, the order
of notification is not defined.

```python
import time
from haberdasher_twirp_srv import request_received, request_sent

@request_recieved.connect
def start_metrics(ctx):
    ctx['start_time'] = time.time()

@request_sent.connect
def finish_metrics(ctx):
    duration = time.time() - ctx['start_time']
    log.info("Request to %s endpoint took %0.4f seconds",
             ctx['endpoint'], duration)
```
