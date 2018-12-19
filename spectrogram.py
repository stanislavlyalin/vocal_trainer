# coding: utf-8
import numpy as np
import struct
from settings import SAMPLE_RATE, FFT_SIZE
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QImage
from PyQt5.QtWidgets import QWidget


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
        self.notes = [['C', 261.63], ['D', 293.66], ['E', 329.63], ['F', 349.23], ['G', 392.00], ['A', 440.00], ['B', 493.88]]
        
    def freqToPx(self, frequency):
        return frequency * self.width() / (SAMPLE_RATE / 2)

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

        # отрисовка нот
        p.setPen(Qt.white)
        for n in self.notes:
            x = self.freqToPx(n[1])
            p.drawLine(x, 30, x, self.height())
            p.drawText(x-10, 0, 20, 20, Qt.AlignHCenter, n[0])