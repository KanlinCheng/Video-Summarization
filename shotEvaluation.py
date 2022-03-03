import cv2
from scipy.io import wavfile
import numpy as np
import math
import imageProcessTool as imgtool
from colorLayoutDescriptor import *

def cal_motion_diff(imgs_path, start, end):

	frame0 = imgtool.readrgbfile(imgs_path[start])
	frame0 = cv2.cvtColor(frame0, cv2.COLOR_RGB2BGR)
	gray_frame0 =cv2.cvtColor(frame0,cv2.COLOR_BGR2GRAY)
	gray_frame0 =cv2.GaussianBlur(gray_frame0,(25,25),0)

	motion_diff = 0

	for i in range(start+1, end+1):

		frame = imgtool.readrgbfile(imgs_path[i])
		frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
		gray_frame=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
		gray_frame=cv2.GaussianBlur(gray_frame,(25,25),0)


		delta = cv2.absdiff(gray_frame0, gray_frame)
		delta = np.reshape(delta, (1, 320*180))

		motion_diff += sum(delta[0])

		# threshold=cv2.threshold(delta,5,255, cv2.THRESH_BINARY)[1]

		# (contours,_)=cv2.findContours(threshold,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		
		# for contour in contours:
		# 	# if cv2.contourArea(contour) < 100:
		# 		# continue
		# 	(x, y, w, h)=cv2.boundingRect(contour)
		# 	cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 1)
		# cv2.imshow("motion", frame)
		# cv2.waitKey(20)

		gray_frame0 = gray_frame

	return motion_diff / (end-start+1)
	# print(motion_diff)

	

def cal_audio_level(audio, start, end):
	audio_start = (start + 1) / 30
	audio_end = (end + 1) / 30
	# print("start and end:", audio_start, audio_end)

	samplerate, data = wavfile.read(audio)
	# data.shape[0] num of samples
	# data.shape[1] num of channels

	start_index = audio_start * samplerate
	end_index = audio_end * samplerate

	print("start and end index:", int(start_index), int(end_index))	
	
	return max(abs(data[int(start_index) : int(end_index+1), 0]))




def cal_cld_normalized_diff(imgs_path, start, end):
	# previous_cld = 0
	# current_cld = 0
	# diff_list = []
	shot_diff = 0


	for i in range(start, end - 1):
		tmp_diff = cal_cld_diff(imgs_path[i], imgs_path[i + 1])
		shot_diff += tmp_diff

	return shot_diff

