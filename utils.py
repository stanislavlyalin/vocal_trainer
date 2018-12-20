# coding: utf-8
import numpy as np
import struct
from settings import SAMPLE_RATE


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


def adobe_palette():
    return palette(np.array([[0, 0, 0, 0], [64, 2, 0, 101], [154, 255, 1, 0], [205, 255, 255, 0], [255, 255, 255, 255]]))
                      

def notes(octave):
    notes_list = [
        [16.35, 18.35, 20.60, 21.83, 24.50, 27.50, 30.87],
        [32.70, 36.95, 41.21, 43.65, 49, 55, 61.74],
        [65.41, 73.91, 73.91, 87.31, 98, 110, 123.48],
        [130.82, 147.83, 164.81, 174.62, 196, 220, 246.96],
        [261.63, 293.33, 329.63, 349.23, 392, 440, 493.88],
        [523.25, 587.32, 659.26, 698.46, 784, 880, 987.75],
        [1046.5, 1174.6, 1318.5, 1396.9, 1568, 1760, 1975.5],
        [2093, 2349.2, 2637, 2793.8, 3136, 3520, 3951],
        [4186, 4698.4, 5274, 5587.6, 6272, 7040, 7902],
        [8372, 9396.8, 10548, 11175.2, 12544, 14080, 15804],
        [16744, 18793.6, 21096, 22350.4, 25088, 28160, 31608]
    ]
    return notes_list[octave]

def note_name(index):
    return ['C', 'D', 'E', 'F', 'G', 'A', 'B'][index]


def freqToPx(frequency, width):
    return frequency * width / (SAMPLE_RATE / 2)

def pxToFreq(px, width):
    return px * (SAMPLE_RATE / 2) / width

def mel(hz):
    return 1127.01048 * np.log(1 + hz / 700)

def hz(mel):
    return 700 * (np.exp(mel / 1127.01048) - 1)

