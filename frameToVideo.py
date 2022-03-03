import imageProcessTool as imgtool
import cv2
import random
import numpy as np
import sys


class videoProcess:

    def __init__(self):
        super().__init__()

    def keyframe_extraction(self, imgs_path):
        video_scenes = self.separate_scene(imgs_path, 0, len(imgs_path), 15)
        print(video_scenes)
        print(len(video_scenes))

        return video_scenes

    # print("---------------------------------------------------------")
    # candidate_list = self.select_candidate(imgs_path, video_scenes, 20)

    # return candidate_list

    # for cand in candidate_list:

    def separate_scene(self, path, start, end, window_size):
        scene_list = []
        cur_scene_start = 0
        cur_scene_end = 0
        prev_img = imgtool.readrgbfile(path[start])
        prev_diff = -1  # no pre diff if pre image is the start scene

        for i in range(start + window_size, end, window_size):
            cur_img = imgtool.readrgbfile(path[i])
            cur_diff = imgtool.cal_img_diff(cur_img, prev_img)

            if prev_diff != -1 and cur_diff < 0.5 and abs(cur_diff - prev_diff) >= 0.2:
                cur_scene_end = self.find_boundary(path, i - window_size, i + 1)
                scene_list.append([cur_scene_start, cur_scene_end])

                cur_scene_start = cur_scene_end + 1
                i = cur_scene_start
                prev_img = imgtool.readrgbfile(path[cur_scene_start])
                prev_diff = -1
                continue

            prev_img = cur_img
            prev_diff = cur_diff
        # print(scene_list)

        if cur_scene_end < end - 1:
            scene_list.append([cur_scene_start, end - 1])

        return scene_list

    def find_boundary(self, path, start, end):
        prev_img = imgtool.readrgbfile(path[start])
        prev_diff = 1
        min_diff = 1
        min_index = end - 1
        for i in range(start + 1, end):
            cur_img = imgtool.readrgbfile(path[i])
            cur_diff = imgtool.cal_img_diff(prev_img, cur_img)

            if cur_diff < min_diff:
                min_diff = cur_diff
                min_index = i - 1

            prev_img = cur_img
            prev_diff = cur_diff

        return min_index

    def select_candidate(self, path, video_scenes, cand_num):
        cand_list = []
        for scene in video_scenes:
            cand = []
            start = scene[0]
            end = scene[1]

            if end - start > cand_num:
                interval = (end - start) // cand_num + 1
            else:
                interval = 1

            for i in range(start, end + 1, interval):
                cand_img = imgtool.readrgbfile(path[i])
                if random.random() < 0.5:
                    cand.append(cand_img)

            cand_list.append(cand)

        return cand_list


if __name__ == "__main__":

    video_process = videoProcess()

    # path = "../project_dataset/frames_rgb/soccer_rgb/"
    # path = "./project_dataset/frames_rgb/soccer/"
    # audio_path = "./project_dataset/audio/soccer.wav"
    # path = "../test_data/frames_rgb_test/test_video/"
    # audio_path = "../test_data/test_video.wav"
    # path = "../test_data_3/frames_rgb_test/test_video_3/"
    # audio_path = "../test_data_3/test_video_3.wav"
    path = sys.argv[1]
    audio_path = sys.argv[2]
    json_output_path = sys.argv[3]

    imgs_path = imgtool.get_all_rgbfile(path)

    res = video_process.keyframe_extraction(imgs_path)
    print(res)

    # selected_scene = res[0: 3]
    selected_scene = res
    print("selected................", selected_scene)

    # imgtool.write_jsonfile(path, selected_scene, audio_path, "test_3_origin.json")
    imgtool.write_jsonfile(path, selected_scene, audio_path, json_output_path)

    img = []
    for scene in selected_scene:
        index = scene[0]
        img.append(imgtool.readrgbfile(imgs_path[index]))

# img1 = imgtool.readrgbfile(path+"frame"+str(res[0][0])+".rgb")

# for i in range(int(res[0][0]+1), int(res[0][1])):
# 	img2 = imgtool.readrgbfile(path+"frame"+str(i)+".rgb")
# 	diff = imgtool.get_img_ssim(img1, img2)

# 	img1 = img2

# 	print(diff)













