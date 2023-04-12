#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import re


RequestBandwidthCommand = "RequestBandwidth"

def parse(line):
    data = {}
    if line.startswith('(video_stream_encoder.cc') and 'RunPostEncode' in line:
        m = re.match(re.compile('.*RunPostEncode, (\\d+), codec: (\\d+), size: (\\d+), width: (\\d+), height: (\\d+), .*'), line) 
        data['type'] = 'image_encoded'
        data['ts'] = int(m[1])
        data['codec'] = int(m[2])
        data['encoded_size'] = int(m[3])
        data['encoded_image_width'] = int(m[4])
        data['encoded_image_height'] = int(m[5])
    elif line.startswith('(rtp_transport_controller_send') and 'OnSentPacket' in line:
        m = re.match(re.compile('.*OnSentPacket, (\\d+), id: (-?\\d+), type: (\\d+), size: (\\d+).*'), line) 
        data['type'] = 'packet_sent'
        data['ts'] = int(m[1])
        data['rtp_id'] = int(m[2])
        data['rtp_type'] = int(m[3])
        data['size'] = int(m[3])
    elif line.startswith('(rtp_transport_controller_send.cc') and 'OnTransportFeedback' in line:
        m = re.match(re.compile('.*OnTransportFeedback, (\\d+), id: (-?\\d+), received: (\\d+).*'), line) 
        data['type'] = 'packet_acked'
        data['ts'] = int(m[1])
        data['rtp_id'] = int(m[2])
        data['received'] = int(m[3])
    elif line.startswith('(video_stream_encoder.cc:') and 'OnFrame' in line:
        m = re.match(re.compile('.*OnFrame, (\\d+), id: (-?\\d+), captured at: (\\d+).*'), line) 
        data['type'] = 'frame_available'
        data['ts'] = int(m[1])
        data['id'] = int(m[2])
        data['capture_ts'] = int(m[3])
    return data

def fetch_stats(line: str)->dict:
    line = line.strip()
    try:
        stats = parse(line)
        return stats
    except json.decoder.JSONDecodeError:
        return None


def request_estimated_bandwidth(line: str)->bool:
    line = line.strip()
    if RequestBandwidthCommand == line:
        return True
    return False


def find_estimator_class():
    import BandwidthEstimator
    return BandwidthEstimator.Estimator


def main(ifd = sys.stdin, ofd = sys.stdout):
    estimator_class = find_estimator_class()
    estimator = estimator_class()
    while True:
        try:
            line = ifd.readline()
            if not line:
                break
            if isinstance(line, bytes):
                line = line.decode("utf-8")
            stats = fetch_stats(line)
            if stats:
                estimator.report_states(stats)
                continue
            request = request_estimated_bandwidth(line)
            if request:
                bandwidth = estimator.get_estimated_bandwidth()
                ofd.write("{}\n".format(int(bandwidth)).encode("utf-8"))
                ofd.flush()
                continue
            sys.stdout.write(line)
            sys.stdout.flush()
        except Exception as e:
            print(e)


def test():
    test_data = [
        '(video_stream_encoder.cc:1441): RunPostEncode, 4226786158, codec: 1, size: 29726, width: 1920, height: 1080, captured at: 0', 
        '(rtp_transport_controller_send.cc:400): OnSentPacket, 4226786160, id: 5322, type: 1, size: 1139',
        '(rtp_transport_controller_send.cc:546): OnTransportFeedback, 4226786170, id: 5337, received: 1, RTT: 4 ms',
        '(video_stream_encoder.cc:824): OnFrame, 4226786119, id: 0, captured at: 4226786117',
    ]
    for l in test_data:
        print(parse(l))


if __name__ == '__main__':
    # main()
    test()
