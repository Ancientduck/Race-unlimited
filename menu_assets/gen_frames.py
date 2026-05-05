import cv2 

vid = cv2.VideoCapture('map_lock.mp4')
count = 0

while True:
    success,frame = vid.read()
    if not success:
        break
    cv2.imwrite(f'lock_frames/lock_frame_{count}.png',frame)
    count += 1
   

vid.release()
print('done')