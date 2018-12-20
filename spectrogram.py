# coding: utf-8
import numpy as np
from settings import FFT_SIZE
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QImage, QColor
from PyQt5.QtWidgets import QWidget
from utils import adobe_palette, freqToPx, pxToFreq, notes, note_name, mel


class Spectrogram(QWidget):

    mouseMoved = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self.data = np.zeros((300, FFT_SIZE // 2))
        self.pal = adobe_palette()
        self.setMouseTracking(True)
    
    def plot(self, data):
        self.data = np.vstack((self.data[1:,:], data))
        self.update()

    def paintEvent(self, event):
        palette_indexes = list(self.data.astype(np.uint8))
        image_data = self.pal[palette_indexes]

        # отрисовка спектрограммы
        im = QImage(image_data, self.data.shape[1], self.data.shape[0], QImage.Format_RGB32)
        im = im.scaled(self.width(), self.height(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        p = QPainter(self)
        p.drawImage(0, 0, im)

        # отрисовка нот
        pen_color = QColor(Qt.white)
        pen_color.setAlpha(128)
        p.setPen(pen_color)

        for octave in range(3, 11):
            for i, note in enumerate(notes(octave)):
                # x = freqToPx(mel(note), self.width())
                x = freqToPx(note, self.width())
                p.drawLine(x, 30, x, self.height())
                p.drawText(x-10, 0, 20, 20, Qt.AlignHCenter, note_name(i))

    def mouseMoveEvent(self, event):
        frequency = pxToFreq(event.x(), self.width())
        self.mouseMoved.emit(frequency)
