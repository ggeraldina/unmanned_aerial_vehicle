import argparse
import numpy
import cv2

DEFAULT_IMAGE_NAME = "Frame_video.png"
DEFAULT_IMAGE_MASK_NAME = "Frame_video_mask.png"
DEFAULT_VIDEO_NAME = "Video.mp4"
DEFAULT_VIDEO_MASK_NAME = "Video_mask.mp4"

parser = argparse.ArgumentParser(description="This example demonstrates searching for moving objects.")
parser.add_argument("video", type=str, help="path to video file")
args = parser.parse_args()
cap = cv2.VideoCapture(args.video)

# Read the first frame
_, frame = cap.read()
height, width, _ = frame.shape
coordinate_x_place_text = numpy.int(width / 2) - 30
COORDINATE_Y_PLACE_TEXT = 50

# The result is saved in the video
# framerate = 10
# out_video = cv2.VideoWriter(DEFAULT_VIDEO_NAME, cv2.VideoWriter_fourcc(*"mp4v"), framerate, (width, height))
# out_video_mask = cv2.VideoWriter(DEFAULT_VIDEO_MASK_NAME, cv2.VideoWriter_fourcc(*"mp4v"), framerate, (width, height))

# Background subtractor
background_subtractor = cv2.bgsegm.createBackgroundSubtractorMOG()

while(True):
  # Computes a foreground mask
  foreground_mask = background_subtractor.apply(frame)
  kornel_size = (5, 5) 
  sigma = 1
  foreground_mask = cv2.GaussianBlur(foreground_mask, kornel_size, sigma)

  # Contours
  contours, hierarchy = cv2.findContours(foreground_mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
  # Drow contours
  # contour_index = -1 
  # contour_color = (0, 0, 255)
  # cv2.drawContours(frame, contours, contour_index, contour_color, 
  #                  thickness=1, lineType=cv2.LINE_AA, hierarchy=hierarchy, maxLevel=1)
  # OR drow framing rectangles
  amount_drawn_contours = 0
  rectangle_color = (0, 0, 255)
  min_size_contour_area = 1000
  for contour in contours:
    if cv2.contourArea(contour) > min_size_contour_area:
      (x, y, w, h) = cv2.boundingRect(contour)
      cv2.rectangle(frame, (x, y), (x + w, y + h), rectangle_color, thickness=2)
      amount_drawn_contours += 1
  
  # Show and save the foreground mask video
  # cv2.imshow("foreground mask", foreground_mask)
  # out_video_mask.write(cv2.cvtColor(foreground_mask, cv2.COLOR_GRAY2RGB))

  # Text on the frame
  font_scale = 1
  text_color = (0, 0, 255)
  cv2.putText(frame, str(amount_drawn_contours), 
              (coordinate_x_place_text, COORDINATE_Y_PLACE_TEXT), 
              cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, thickness=2)
  # Show and save the video
  cv2.imshow("frame", frame)
  # out_video.write(frame)
  
  key = cv2.waitKey(30) & 0xff
  # Exit
  if key == 27:
    break  
  # Save the frame and the foreground mask
  if key == ord("s"):
    cv2.imwrite(DEFAULT_IMAGE_NAME, frame)
    cv2.imwrite(DEFAULT_IMAGE_MASK_NAME, foreground_mask)

  # Read a next frame
  _, frame = cap.read()

cap.release()
cv2.destroyAllWindows()