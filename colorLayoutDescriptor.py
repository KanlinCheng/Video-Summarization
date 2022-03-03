import numpy as np
import cv2
import os
from PIL import Image
from skimage.metrics import structural_similarity as strcsim
import json
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from cv2 import dct

import cv2, sys, os
from scipy.spatial.distance import cdist
# from DescriptorComputer import DescriptorComputer


def readrgbfile(filename, width=320, height=180):
    file = open(filename, "rb")
    image_bytes = file.read()

    res = np.fromstring(image_bytes, dtype=np.uint8)
    img_rgb = res.reshape((3, height, width)).transpose().transpose(1, 0, 2)
    # img_rgb.shape = (height, width, 3)

    return img_rgb


def computeCLD(img, rows, cols):
    averages = np.zeros((rows, cols, 3))
    imgH, imgW, _ = img.shape
    # print(imgH, imgW, _)
    for row in range(rows):
        for col in range(cols):
            slice = img[imgH // rows * row: imgH // rows * (row + 1),
                    imgW // cols * col: imgW // cols * (col + 1)]
            average_color_per_row = np.mean(slice, axis=0)
            average_color = np.mean(average_color_per_row, axis=0)
            average_color = np.uint8(average_color)
            averages[row][col][0] = average_color[0]
            averages[row][col][1] = average_color[1]
            averages[row][col][2] = average_color[2]

    icon = cv2.cvtColor(np.array(averages, dtype=np.uint8), cv2.COLOR_RGB2YCR_CB)
    y, cr, cb = cv2.split(icon)
    dct_y = cv2.dct(np.float32(y))
    dct_cb = cv2.dct(np.float32(cb))
    dct_cr = cv2.dct(np.float32(cr))
    dct_y_zigzag = []
    dct_cb_zigzag = []
    dct_cr_zigzag = []
    flip = True
    flipped_dct_y = np.fliplr(dct_y)
    flipped_dct_cb = np.fliplr(dct_cb)
    flipped_dct_cr = np.fliplr(dct_cr)
    for i in range(rows + cols - 1):
        k_diag = rows - 1 - i
        diag_y = np.diag(flipped_dct_y, k=k_diag)
        diag_cb = np.diag(flipped_dct_cb, k=k_diag)
        diag_cr = np.diag(flipped_dct_cr, k=k_diag)

        if flip:
            diag_y = diag_y[::-1]
            diag_cb = diag_cb[::-1]
            diag_cr = diag_cr[::-1]
        dct_y_zigzag.append(diag_y)
        dct_cb_zigzag.append(diag_cb)
        dct_cr_zigzag.append(diag_cr)
        flip = not flip
    return np.concatenate(
        [np.concatenate(dct_y_zigzag), np.concatenate(dct_cb_zigzag), np.concatenate(dct_cr_zigzag)])


# def cal_cld_diff(a, b):
#     total_diff = 0
#
#     square_diff = []
#     for i in range(len(a)):
#         square_diff.append(np.square(a[i]-b[i]))
#     print(square_diff)
#
#     for j in range(0, len(a), len(a)//3):
#         total_diff += np.sqrt(np.sum(square_diff[j:j+len(a)//3]))
#
#     return total_diff


def cal_cld_diff(img0, img1):
    frame0 = readrgbfile(img0)
    frame1 = readrgbfile(img1)
    a = computeCLD(frame0, 8, 8)
    b = computeCLD(frame1, 8, 8)

    total_diff = 0

    square_diff = []
    for i in range(len(a)):
        square_diff.append(np.square(a[i]-b[i]))
    # print(square_diff)

    for j in range(0, len(a), len(a)//3):
        total_diff += np.sqrt(np.sum(square_diff[j:j+len(a)//3]))

    return total_diff


if __name__ == "__main__":
    img_path = "./project_dataset/frames_rgb/soccer/frame0.rgb"
    img_path2 = "./project_dataset/frames_rgb/soccer/frame1200.rgb"
    rgb = readrgbfile(img_path)
    rgb2 = readrgbfile(img_path2)

    cld = computeCLD(rgb, 8, 8)

    diff = cal_cld_diff(rgb, rgb2)
    print(diff)
