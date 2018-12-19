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


def freqToPx(frequency, width):
    return frequency * width / (SAMPLE_RATE / 2)
