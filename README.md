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

- [Werkzeug](http://werkzeug.pocoo.org/) - used for WSGI request parsing.
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
