import bjoern
import echo_pb2 as pb
from echo_twirp_srv import EchoImpl, EchoServer


class Echoer(EchoImpl):
    def Repeat(self, request):
        return pb.EchoResponse(output=request.input)

    def RepeatMultiple(self, request):
        output = request.input
        if request.count > 0:
            output = output * request.count
        return pb.EchoResponse(output=output)


if __name__ == "__main__":
    app = EchoServer(Echoer())
    bjoern.run(app, "0.0.0.0", 8080)
