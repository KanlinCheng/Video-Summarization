README

Note: Please install K-lite codecs (available at http://www.codecguide.com/configuration_tips.htm?version=1612) in Windows to run the player successfully.

(1) To implement the shot detection, evaluation and generate the summary video in mp4 format, please run videoProcess.py in command line.
    It's better to run the program in PyCharm terminal for faster speed.
	
	User needs input 5 arguments, which are (1)RGB frame path (2)Audio file path (3)Output json file path (4)JPEG frame path (5)Output video summary path in order.

	Sample commands for these 2 test dataset:
	python videoProcess.py ../test_data/frames_rgb_test/test_video/ ../test_data/test_video.wav ./test_1_demo.json ../test_data/frames_test/test_video/ ./test_1_summary.mp4

	python videoProcess.py ../test_data_3/frames_rgb_test/test_video_3/ ../test_data_3/test_video_3.wav ./test_3_demo.json ../test_data_3/frames_test/test_video_3/ ./test_3_summary.mp4

	The "test_1_summary.mp4" and "test_3_summary.mp4" are the output summary videos.
	During running, it will print the start and end index of each detected shot, the score of each shot and final selected candidate shot for the summary video, as well as the total running time of the program.
	
	Then run newPlayer2.py (either in IDE or in command line)
	Command: python newPlayer2.py
	Click the "Open Video" button, choose the generated mp4 file, then click the play button. The video will play.



(2) To play the original full video
	Please first run frameToVideo.py in command line.
	User needs input 3 arguments, which are (1)RGB frame path (2)Audio file path (3)Output json file path
	
	Sample commands for these 2 test dataset:
	python frameToVideo.py ../test_data/frames_rgb_test/test_video/ ../test_data/test_video.wav ./test_1_ori.json
	python frameToVideo.py ../test_data_3/frames_rgb_test/test_video_3/ ../test_data_3/test_video_3.wav ./test_3_ori.json
	
	The "test_1_ori.json" and "test_3_ori.json" are the output json files.
	
	Then, there are 2 different methods to play the video:
	[1] The first one is to run videoPlayer.py in command line.
	User needs to input the file path of the json file generated in the previous step.
	
	Sample commands for these 2 test dataset:
	python videoPlayer.py ./test_1_ori.json
	python videoPlayer.py ./test_3_ori.json
	
	Now there will be a player window, user needs to click the left part of the black rectangle at the bottom of the player.
	Then the video will play until the end. User can pause the video and start it during the middle of the video.
	
	
	[2] The second method is to run videoSave.py to generate a mp4 file, then run newPlayer2.py to play it.
	To run videoSave.py, user needs to input 5 arguments, which are (1)JPEG frame path (2)Output avi file (not used) (3)JSON file geneated in the first step (4)Original audio file path (5)Output mp4 video path
	
	Sample commands:
	python videoSave.py ../test_data/frames_test/test_video/ test_1.avi ./test_1_ori.json ../test_data/test_video.wav ./test_1_ori.mp4
	python videoSave.py ../test_data_3/frames_test/test_video_3/ test_3.avi ./test_3_ori.json ../test_data_3/test_video_3.wav ./test_3_ori.mp4
	
	Then run newPlayer2.py (either in IDE or in command line)
	Command: python newPlayer2.py
	Click the "Open Video" button, choose the generated mp4 file, then click the play button. The video will play.
	


Generally, the running time will be within 5-8 minutes.
If there are any issues when running the program, please contact us. Thank you!
Email: kanlinch@usc.edu

