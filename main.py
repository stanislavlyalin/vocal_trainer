# coding: utf-8
import numpy as np
import sys
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtGui import QPainter, QColor, QImage
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
import pyaudio
from array import array
from threading import Thread
import struct

SAMPLE_RATE = 4000
LINES_PER_SECOND = 24
FFT_SIZE = 2048

def palette(points):
    indexes = points[:, 0]
    gradient_points = points[:, 1:]
    channels = [[], [], []]

    for point_idx in range(len(gradient_points) - 1):
        fr_idx = point_idx
        to_idx = point_idx + 1
        steps = indexes[to_idx] - indexes[fr_idx]

        for channel in range(3):
            channels[channel] += list(
                np.linspace(
                    gradient_points[fr_idx, channel], gradient_points[to_idx, channel], steps, False, dtype=np.uint8))

    pal = np.vstack((np.array(channels).T, gradient_points[-1, :]))
    pal = np.array([int.from_bytes(struct.pack('BBB', *color), byteorder='big') for color in pal.astype(np.uint8)], dtype=np.int32)

    return pal


class Spectrogram(QWidget):
    def __init__(self):
        super().__init__()
        self.data = np.zeros((300, FFT_SIZE // 2))
        self.pal = palette(np.array([[0, 0, 0, 0], [64, 2, 0, 101], [154, 255, 1, 0], [205, 255, 255, 0], [255, 255, 255, 255]]))
        
    def plot(self, data):
        self.data = np.vstack((self.data[1:,:], data))
        self.update()

    def paintEvent(self, event):
        a = list(self.data.astype(np.uint8))
        a = self.pal[a]

        im = QImage(a, self.data.shape[1], self.data.shape[0], QImage.Format_RGB32)
        im = im.scaled(self.width(), self.height(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        p = QPainter(self)
        p.drawImage(0, 0, im)

CHUNK_SIZE = SAMPLE_RATE // LINES_PER_SECOND  # FFT_SIZE
FORMAT = pyaudio.paInt16

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.spectrogram = Spectrogram()
        self.startButton = QPushButton('Start')
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.spectrogram)
        self.layout.addWidget(self.startButton)
        self.setLayout(self.layout)
        self.recording = False
        self.buffer = np.zeros(FFT_SIZE)

        self.startButton.clicked.connect(self.clicked)

    def microphoneReader(self):
        while self.recording:
            self.data = np.frombuffer(array('h', self.stream.read(CHUNK_SIZE)), dtype=np.int16).astype(float)

            if not np.any(np.isnan(self.data)):

                self.buffer = np.hstack((self.buffer[len(self.data):], self.data))

                sp = 10 * np.log10(np.abs(np.fft.rfft(self.buffer * np.hamming(len(self.buffer)))))[:FFT_SIZE // 2]
                # sp = np.abs(np.fft.rfft(self.data))[:FFT_SIZE // 2]
                sp += sp.min()
                sp = np.clip(128 * sp / (sp.max() - sp.min()), 0, 255)
                self.spectrogram.plot(sp.astype(np.uint8))


    def clicked(self):
        self.recording = not self.recording
        self.startButton.setText('Stop' if self.recording else 'Start')

        if self.recording:
            self.p = pyaudio.PyAudio()
            self.data = array('h')
            self.stream = self.p.open(format=FORMAT, channels=1, rate=8000,
                        input=True, output=True,
                        frames_per_buffer=CHUNK_SIZE)
            self.thread = Thread(target=self.microphoneReader)
            self.thread.start()
            print('Start recording')
        else:
            self.thread.join()
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
            print('Stop recording')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    sys.exit(app.exec_())
