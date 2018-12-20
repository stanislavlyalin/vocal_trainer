# coding: utf-8
import numpy as np
from settings import SAMPLE_RATE, LINES_PER_SECOND, FFT_SIZE, CHUNK_SIZE
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QSlider
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from spectrogram import Spectrogram
from recorder import Recorder
from utils import mel, hz


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('icon.png'))

        self.spectrogram = Spectrogram()
        self.spectrogram.mouseMoved.connect(lambda f: self.setWindowTitle('Vocal Trainer - ' + '%.2f' % f + ' Hz'))

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(10)
        self.slider.setMaximum(50)
        self.slider.setValue(10)
        self.slider.valueChanged.connect(self.updateCoef)

        self.startButton = QPushButton('Start')
        self.startButton.clicked.connect(self.clicked)        

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.addWidget(self.spectrogram)
        self.layout.addWidget(self.slider)
        self.layout.addWidget(self.startButton)
        self.setLayout(self.layout)
        
        center = QApplication.desktop().availableGeometry().center()
        width, height = 1500, 1000
        self.setGeometry(center.x() - width // 2, center.y() - height // 2, width, height)

        self.buffer = np.zeros(FFT_SIZE)
        self.coef = 1
        
        self.recorder = Recorder(SAMPLE_RATE, CHUNK_SIZE, self.recorderData)

    def updateCoef(self, val):
        self.coef = val * 0.1

    def recorderData(self, data):
        if not np.any(np.isnan(data)):
            self.buffer = np.hstack((self.buffer[len(data):], data))

            sp = 10 * np.log10(np.abs(np.fft.rfft(self.buffer * np.hamming(len(self.buffer)))))[:FFT_SIZE // 2]
            
            # преобразование в шкалу MEL
            # h = hz(np.arange(len(sp)) * mel(SAMPLE_RATE / 2) / (FFT_SIZE / 2))
            # sp_i = np.clip(np.round(h * (FFT_SIZE / 2) / (SAMPLE_RATE / 2)), 0, (FFT_SIZE // 2) - 1).astype(int)
            # sp = sp[sp_i]

            # нормализация
            sp *= self.coef
            sp -= sp.min()
            sp = np.clip(sp, 0, 255).astype(np.uint8)

            self.spectrogram.plot(sp)


    def clicked(self):
        if self.recorder.recording:
            self.recorder.stop()
        else:
            self.recorder.start()

        self.startButton.setText('Stop' if self.recorder.recording else 'Start')
