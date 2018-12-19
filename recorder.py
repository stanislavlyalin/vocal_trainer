# coding: utf-8
import numpy as np
import pyaudio
from array import array
from threading import Thread


class Recorder():
    def __init__(self, sample_rate, chunk_size, callback):
        self.recording = False
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.callback = callback

    def start(self):
        self.recording = True
        self.p = pyaudio.PyAudio()
        self.data = array('h')
        self.stream = self.p.open(format=pyaudio.paFloat32, channels=1, rate=self.sample_rate,
                    input=True, output=True,
                    frames_per_buffer=self.chunk_size)
        self.thread = Thread(target=self.microphoneReader)
        self.thread.start()

    def stop(self):
        self.recording = False
        self.thread.join()
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

    def microphoneReader(self):
        while self.recording:
            # self.data = np.frombuffer(array('h', self.stream.read(CHUNK_SIZE)), dtype=np.float32)
            self.callback(np.frombuffer(array('h', self.stream.read(self.chunk_size)), dtype=np.float32))

            