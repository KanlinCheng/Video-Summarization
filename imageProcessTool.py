import numpy as np
import cv2
import os
from PIL import Image
from skimage.metrics import structural_similarity as strcsim
import json
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *


"""
readrgbfile function:
input: .rgb file
output: 3D array to store all the rgb info with corresponding position
"""
def readrgbfile(filename, width = 320, height = 180):
	file = open(filename, "rb")
	image_bytes = file.read()
	
	res = np.fromstring(image_bytes, dtype = np.uint8)
	img_rgb = res.reshape((3, height, width)).transpose().transpose(1, 0, 2)
	#img_rgb.shape = (height, width, 3)

	return img_rgb


def get_all_rgbfile(path):
	res = []
	for root, dirs, files in os.walk(path, topdown = False):

		for file_name in files:
			if ".rgb" in file_name:
				res.append(file_name[5:].zfill(9))
		
	res.sort()
	for i in range(0, len(res)):
		res[i] = path + "frame" + res[i].strip('0')
		if i == 0:
			res[i] = path + "frame0.rgb"
	
	return res



def combine_all_rgbfile(image_list):
	synopsis = None
	for img in image_list:
		if synopsis:
			synopsis = concat_imgs(synopsis, Image.fromarray(img))
		else:
			synopsis = Image.fromarray(img)
	return np.array(synopsis)

def concat_imgs(img1, img2):
	res = Image.new("RGB", (img1.width+img2.width, img1.height))
	res.paste(img1, (0, 0))
	res.paste(img2, (img1.width, 0))
	return res


def cal_img_diff(img1, img2):

	# Compute the mean structural similarity index between two images
	# multichannel=True ssim done independently for each channel then averaged
	mssim = strcsim(img1, img2, multichannel=True, gaussian_weightsbool=True) 
	# print(mssim)

	#cv2.calcHist(images, channels, mask, histSize, ranges[, hist[, accumulate]])
	hist1 = cv2.calcHist([img1], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
	hist2 = cv2.calcHist([img2], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])

	#cv2.HISTCMP_CORREL: Computes the correlation between the two histograms.
	hist_diff = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
	# print(hist_diff)

	res_diff = 0.7*mssim + 0.3*hist_diff

	return res_diff
	

def create_jsoninfo(video_path, start, end, audio_path):
	infodict = {}
	infodict["type"] = 1
	infodict["video"] = video_path
	infodict["start"] = start
	infodict["end"] = end
	infodict["audio"] = audio_path
	return infodict


def write_jsonfile(video_path, selected_scene, audio_path, jfile_name):
	info = []
	for scene in selected_scene:
		info.append(create_jsoninfo(video_path, scene[0], scene[1], audio_path))

	with open(jfile_name, 'w') as jfile:
		json.dump(info, jfile)


def readrgbtoQImage(fileName, width = 320, height = 180):
    rgbinfo = readrgbfile(fileName, width =  width)
    bytesPerLine = 3*width
    img = QImage(rgbinfo.tobytes(), width, height, bytesPerLine, QImage.Format_RGB888)
    return img




