#!/usr/bin/env python

# Test the fldigi-proxy TCP interface

import argparse

import trio

test_handshake_0 = b"\x00\x03U\xc7\xaa\xa3\x85\xe8%\x95M\x96\xcbQ\x80C\x04\x0f\xf0\x14\xcf\x10\x11{t\x93=\x9d}\xa8a\xf5r\x02w\xca;\x11\xa1T\xaa\x81\xbf\xf2\xcbr\xd5;\xa9\xb2"
test_handshake_1 = b"\x00\x02L\xdf\xd9\x81\x98\xcfr\xd8\xa7d\xd2\x167\x98\xff\x9b\t\x16\x1cR\x82^\x96\t8\xfb[\x9fv\x15d\n\xc0\xf7Wi\xf2\x1f\x9f\xd6ht\xba.\xf0>\\\x1c"
test_handshake_2 = b"\x00\xae);;\xcd\x02\xea\x12A\xfc@\xb6L\xd6\xd2.\x8by\xfc\xddIR\xd9\x9e\x86\x96j\xbf\x8cA\xec\x8aD\xb0\xf1\xcb\xd6\xedQzq\xc3,\xb3W_\xf25\x0b\x066j\xd7\x06\xd3\xa0\xf0i=\xcd\xd8J\xb0\xffv"
test_handshake_3 = b'\x00-\x00\x10\x00\x02"\x00\x00\x03\x02\xaa\xa2\x01 \x06"nF\x11\x1a\x0bY\xca\xaf\x12`C\xeb[\xbf(\xc3O:^3*\x1f\xc7\xb2\xb7<\xf1\x88\x91\x0f'
handshakes = [test_handshake_0] #, test_handshake_1, test_handshake_2, test_handshake_3]


async def send_raw(proxy_port, packets):
    print("Beginning to serve raw packets")
    for data in packets:
        print("sending data:", data)
        await proxy_port.send_all(data)
        # space out packets
        await trio.sleep(0.1)


async def tester_client(output_stream):
    print("fldigi output client started")
    received_data = []
    try:
        async for data in output_stream:
            print("receiving data:", data)
            received_data.append(data)
            if len(received_data) == len(handshakes):
                if received_data == handshakes:
                    print("Successful proxying!")
    except Exception as exc:
        print("tester client crashed: {!r}".format(exc))


async def tester_server(input_stream):
    print("fldigi input server started")
    delay = 2
    try:
        print("Sleeping for", delay, "seconds")
        await trio.sleep(delay)
        await send_raw(input_stream, handshakes)
        print("tester finished")
    except Exception as exc:
        print("tester server crashed: {!r}".format(exc))


async def server_wrapper(inport):
    print("wrapping server")
    await trio.serve_tcp(tester_server, inport)


async def client_wrapper(outport):
    print("wrapping client")
    await trio.serve_tcp(tester_client, outport)


async def main():
    parser = argparse.ArgumentParser(description="test fldigi-proxy")
    parser.add_argument("--inport", type=int, help="input port for fldigi-proxy")
    parser.add_argument("--outport", type=int, help="output port for fldigi-proxy")
    args = parser.parse_args()
    print("TCP tester started")

    async with trio.open_nursery() as nursery:
        nursery.start_soon(server_wrapper, args.inport)
        nursery.start_soon(client_wrapper, args.outport)


if __name__ == "__main__":
    trio.run(main)
