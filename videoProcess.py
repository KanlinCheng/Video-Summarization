import imageProcessTool as imgtool
import cv2
import random
import numpy as np
import shotEvaluation as shoteva
import videoSave
from sklearn import preprocessing
import time
import sys
from os.path import isfile, join
from moviepy.editor import *
import json


class videoProcess:

	def __init__(self):
		super().__init__()

	def keyframe_extraction(self, imgs_path):
		video_scenes = self.separate_scene(imgs_path, 0, len(imgs_path), 15)
		print(video_scenes)
		print(len(video_scenes))

		video_scenes = self.adjust_shot_length(video_scenes)
		print(video_scenes)
		print(len(video_scenes))

		return video_scenes


	def adjust_shot_length(self, video_scenes):
		scene_list = []
		for scene in video_scenes:
			scene_len = scene[1]-scene[0]+1

			# adjust long shot 
			if scene_len > 600:
				while scene_len > 600:
					scene_len /= 2
				divid_len = int(scene_len)
				for i in range(scene[0], scene[1], divid_len+1):
					if i+divid_len > scene[1] and scene[1]-scene_list[len(scene_list)-1][0] <= 600:
						scene_list[len(scene_list)-1][1] = scene[1]
					elif i+divid_len > scene[1]:
						scene_list.append([i, scene[1]])
					else:
						scene_list.append([i, i+divid_len])

			#adjust short shot
			elif scene_len <= 150 and len(scene_list) > 0 and scene[1]-scene_list[len(scene_list)-1][0] <= 600:

				scene_list[len(scene_list)-1][1] = scene[1]


			else:
				scene_list.append([scene[0], scene[1]])

		return scene_list
	


	def separate_scene(self, path, start, end, window_size):
		scene_list = []
		cur_scene_start = 0
		cur_scene_end = 0
		prev_img = imgtool.readrgbfile(path[start])
		prev_diff = -1 #no pre diff if pre image is the start scene


		for i in range(start+window_size, end, window_size):
			cur_img = imgtool.readrgbfile(path[i])
			cur_diff = imgtool.cal_img_diff(cur_img, prev_img)

			if prev_diff != -1 and cur_diff < 0.5 :
				cur_scene_end = self.find_boundary(path, i - window_size, i+1)
				scene_list.append([cur_scene_start, cur_scene_end])

				cur_scene_start = cur_scene_end + 1
				i = cur_scene_start
				prev_img = imgtool.readrgbfile(path[cur_scene_start])
				prev_diff = -1
				continue

			prev_img = cur_img
			prev_diff = cur_diff
			# print(scene_list)

		if cur_scene_end < end-1:
			scene_list.append([cur_scene_start, end-1])

		return scene_list


	def find_boundary(self, path, start, end):
		prev_img = imgtool.readrgbfile(path[start])
		prev_diff = 1
		min_diff = 1
		min_index = end-1
		for i in range(start+1, end):
			cur_img = imgtool.readrgbfile(path[i])
			cur_diff = imgtool.cal_img_diff(prev_img, cur_img)

			if cur_diff < min_diff:
				min_diff = cur_diff
				min_index = i-1

			prev_img = cur_img
			prev_diff = cur_diff

		return min_index


	def select_candidate(self, path, video_scenes, audio_path):
		
		sort_score = self.cal_shot_score(path, video_scenes, audio_path)
		print("the sort score:", sort_score)
		final_candidate = []
		final_length = 0
		for score in sort_score:
			index = int(score[0][4:])
			print("this is index:", index)
			cur_shot_length = video_scenes[index][1] - video_scenes[index][0] + 1
			
			final_length += cur_shot_length

			if final_length - cur_shot_length <= 2400:
				final_candidate.append(video_scenes[index])
			if final_length > 2850:
				break

		final_candidate.sort()
		print("----------------------------this is final candiate---------------------")
		print(final_candidate)
		print(final_length)
		return final_candidate


	def cal_shot_score(self, path, video_scenes, audio_path):
		motion_score_list = []
		audio_score_list = []
		cld_diff_list = []
		normalized_cld_diff_list = []
		for scene in video_scenes:
			cand = []
			start = scene[0]
			end = scene[1]

			motion_score = shoteva.cal_motion_diff(path, start, end)
			motion_score_list.append(motion_score)

			audio_score = shoteva.cal_audio_level(audio_path, start, end)
			audio_score_list.append(audio_score)

			cld_diff = shoteva.cal_cld_normalized_diff(path, start, end)
			cld_diff_list.append(cld_diff)

		normalized_motion_list = preprocessing.normalize(np.array(motion_score_list).reshape(1, -1))
		normalized_audio_list = preprocessing.normalize(np.array(audio_score_list).reshape(1, -1))
		normalized_cld_list = preprocessing.normalize(np.array(cld_diff_list).reshape(1, -1))
		# print("Normalized_cld_list: ", normalized_cld_list)

		diff_sum = np.sum(cld_diff_list)
		for d in cld_diff_list:
			normalized_cld_diff_list.append(d / diff_sum)

		score_dict = {}
		for i in range(0, len(video_scenes)):
			score = 0.4*normalized_motion_list[0][i] + 0.3*normalized_audio_list[0][i] + 0.3*normalized_cld_list[0][i]
			# score = 0.6*normalized_motion_list[0][i] + 0.4*normalized_audio_list[0][i]
			key = "shot"+str(i)
			score_dict[key] = score

		sort_score = sorted(score_dict.items(), key=lambda x: x[1], reverse=True)

		return sort_score

		# return normalized_motion_list, normalized_audio_list, normalized_cld_diff_list


def convert_frames_to_video(pathIn, pathOut, fps):
	frame_array = []
	files = [f for f in os.listdir(pathIn) if isfile(join(pathIn, f))]
	files.sort(key=lambda x: int(x[5:-4]))

	for i in range(len(files)):
		filename = pathIn + files[i]
		# reading each files
		img = cv2.imread(filename)
		height, width, layers = img.shape
		size = (width, height)

		# print(filename)
		# inserting the frames into an image array
		frame_array.append(img)

	out = cv2.VideoWriter(pathOut, cv2.VideoWriter_fourcc(*'DIVX'), fps, size)

	for i in range(len(frame_array)):
		# writing to a image array
		out.write(frame_array[i])

	out.release()


def main(path_in, path_out, meta_path, clip_audio_path, final_result_path):
	pathIn = path_in
	pathOut = path_out
	file_meta_path = meta_path
	audio_clip_path = clip_audio_path
	result_path = final_result_path
	fps = 30.0
	convert_frames_to_video(pathIn, pathOut, fps)

	# getting only first 15 seconds
	# file_meta = open('final.json',"r")
	file_meta = open(file_meta_path, "r")
	metadata = json.load(file_meta)
	num_shot = len(metadata)

	clips_list = []
	for i in range(0, num_shot):
		start = metadata[i]["start"]
		end = metadata[i]["end"]
		start = round(start / 30)
		end = round(end / 30)
		clip = VideoFileClip(pathOut).subclip(start, end)

		# loading audio file
		# audioclip = AudioFileClip("../project_dataset/audio/soccer.wav").subclip(start, end)
		audioclip = AudioFileClip(audio_clip_path).subclip(start, end)
		# adding audio to the video clip
		videoclip = clip.set_audio(audioclip)

		clips_list.append(videoclip)

	# concatinating both the clips
	finalclip = concatenate_videoclips(clips_list)
	# finalclip.write_videofile("summary.mp4")
	finalclip.write_videofile(result_path)


if __name__ == "__main__":

	s_time = time.time()
	video_process = videoProcess()

	# Please enter (1)RGB frame path (2)Audio file path (3)Output json file path (4)JPEG frame path (5)Output video summary path   in order.
	# path = "../project_dataset/frames_rgb/soccer_rgb/"
	# audio_path = "../project_dataset/audio/soccer.wav"
	path = sys.argv[1]
	audio_path = sys.argv[2]
	output_json_path = sys.argv[3]

	path_in = sys.argv[4]
	avi_path_out = "./tmp_avi.avi"
	result_path = sys.argv[5]

	imgs_path = imgtool.get_all_rgbfile(path)

	video_scenes = video_process.keyframe_extraction(imgs_path)

	final_candidate = video_process.select_candidate(imgs_path, video_scenes, audio_path)
	# imgtool.write_jsonfile(path, final_candidate, audio_path, "./final.json")
	imgtool.write_jsonfile(path, final_candidate, audio_path, output_json_path)

	time.sleep(1)
	main(path_in, avi_path_out, output_json_path, audio_path, result_path)
	e_time = time.time()
	print("time cosume:", e_time - s_time)
	
	









