# coding: utf-8
import numpy as np
from settings import FFT_SIZE
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QImage
from PyQt5.QtWidgets import QWidget
from utils import adobe_palette, freqToPx


class Spectrogram(QWidget):
    def __init__(self):
        super().__init__()
        self.data = np.zeros((300, FFT_SIZE // 2))
        self.pal = adobe_palette()
        self.notes = [['C', 261.63], ['D', 293.66], ['E', 329.63], ['F', 349.23], ['G', 392.00], ['A', 440.00], ['B', 493.88]]
    
    def plot(self, data):
        self.data = np.vstack((self.data[1:,:], data))
        self.update()

    def paintEvent(self, event):
        palette_indexes = list(self.data.astype(np.uint8))
        image_data = self.pal[palette_indexes]

        im = QImage(image_data, self.data.shape[1], self.data.shape[0], QImage.Format_RGB32)
        im = im.scaled(self.width(), self.height(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        p = QPainter(self)
        p.drawImage(0, 0, im)

        # отрисовка нот
        p.setPen(Qt.white)
        for n in self.notes:
            x = freqToPx(n[1], self.width())
            p.drawLine(x, 30, x, self.height())
            p.drawText(x-10, 0, 20, 20, Qt.AlignHCenter, n[0])
