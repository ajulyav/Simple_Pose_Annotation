Input Data:

- a video clip clip_05.mp4
- a json file clip_05_pose.json with pose detection information using OpenPose (https://cmu-perceptual-computing-lab.github.io/openpose/web/html/doc/)
- an example CSV output on the first frame

Task to do:

- write a python program that will 
	(1) generate an output video with (suggested tool/library usage: ffmpeg, opencv): 
		a. bounding boxes around the head (facial organs not including neck) and upper body (neck to hip)
		b. lines that show the articulation of the limbs (arms from the shoulder to elbow, elbow to wrist, legs from hip to knee, knee to ankle)
	(2) output the information as tabular data in a CSV file. Each row should use comma delimiters to separate values for :
		a. Frame and person IDs: 'frame_ID','person_ID',
		b. Head bounding box center coordinates, width, and height: 'head_center_x', 'head_center_y', 'head_width', 'head_height',
		c. Upper body bounding box center coordinates, width, and height: 'body_center_x', 'body_center_y', 'body_width', 'body_height'
		d. Left and right shoulder coordinates with a unit vector (i.e. length of vector is 1) that points towards elbow and length parameter, and unit vector that points from elbow towards wrist with length parameter: 'left_shoulder_x', 'left_shoulder_y', 'left_shoulder_vec_x', 'left_shoulder_vec_y', 'left_upper_arm_length','left_elbow_vec_x', 'left_elbow_vec_y', 'left_lower_arm_length', 'right_shoulder_x', 'right_shoulder_y','right_shoulder_vec_x', 'right_shoulder_vec_y', 'right_upper_arm_length','right_elbow_vec_x', 'right_elbow_vec_y', 'right_lower_arm_length',
		e. Similarly to d. and e., for the left/right hip to knee, and the knee to ankle: 'left_hip_x', 'left_hip_y','left_hip_vec_x', 'left_hip_vec_y', 'left_upper_leg_length','left_knee_vec_x', 'left_knee_vec_y', 'left_lower_leg_length','right_hip_x', 'right_hip_y','right_hip_vec_x', 'right_hip_vec_y', 'right_upper_leg_length','right_knee_vec_x', 'right_knee_vec_y', 'right_lower_leg_length' 

	If a value is missing, it should be set to -1
- comment and document your code so that it is easily reusable
- your code should be as generic as possible to deal with all similarly named and formatted video-json file pairs
