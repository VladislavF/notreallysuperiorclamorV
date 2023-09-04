#!/bin/bash
#ffmpeg -i http://localhost:8000/radio -ac 2 -ar 44100 -f f32le -filter:a "volume=1.0" -acodec pcm_f32le tcp://zeus.local:2000
#ffmpeg -f alsa -c:a pcm_f32le -channels 2 -sample_rate 44100 -i hw:0,1 -ac 2 -ar 44100 -f f32le -filter:a "volume=1.0" -acodec pcm_f32le tcp://zeus.local:2000
#regular stream
ffmpeg -i http://vladfm.fomitchev.net/radio -ac 2 -ar 44100 -f f32le -filter:a "volume=0.99" -acodec pcm_f32le zmq:tcp://0.0.0.0:2000
