import cv2
import numpy as np
import os
from os.path import isfile, join
import math
from moviepy.editor import *
import json
import sys

def convert_frames_to_video(pathIn,pathOut,fps):
    frame_array = []
    files = [f for f in os.listdir(pathIn) if isfile(join(pathIn, f))]
    files.sort(key = lambda x: int(x[5:-4]))
    
    for i in range(len(files)):
        filename=pathIn + files[i]
        #reading each files
        img = cv2.imread(filename)
        height, width, layers = img.shape
        size = (width,height)
        
        # print(filename)
        #inserting the frames into an image array
        frame_array.append(img)

    out = cv2.VideoWriter(pathOut,cv2.VideoWriter_fourcc(*'DIVX'), fps, size)


    for i in range(len(frame_array)):
        # writing to a image array
        out.write(frame_array[i])

    out.release()

def main():
    # pathIn= '../project_dataset/frames/soccer/'
    # pathOut = 'video.avi'
    pathIn = sys.argv[1]
    pathOut = sys.argv[2]
    file_meta_path = sys.argv[3]
    audio_clip_path = sys.argv[4]
    result_path = sys.argv[5]
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
        start = round(start/30)
        end = round(end/30)
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


if __name__=="__main__":
    main()
