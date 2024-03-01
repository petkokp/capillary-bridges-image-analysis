import cv2
import math

def construct_ellipse_from_contour(img, contour):
  ellipse = cv2.fitEllipse(contour)

  (xc,yc),(d1,d2),angle = ellipse

  # draw ellipse in green
  cv2.ellipse(img, ellipse, (0, 255, 0), 3)

  # draw circle at center
  xc, yc = ellipse[0]
  cv2.circle(img, (int(xc),int(yc)), 10, (255, 255, 255), -1)

  # draw major axis line in red
  rmajor = max(d1,d2)/2
  if angle > 90:
      angle = angle - 90
  else:
      angle = angle + 90

  x1 = xc + math.cos(math.radians(angle))*rmajor
  y1 = yc + math.sin(math.radians(angle))*rmajor
  x2 = xc + math.cos(math.radians(angle+180))*rmajor
  y2 = yc + math.sin(math.radians(angle+180))*rmajor
  cv2.line(img, (int(x1),int(y1)), (int(x2),int(y2)), (0, 0, 255), 3)

  # draw minor axis line in blue
  rminor = min(d1,d2)/2
  if angle > 90:
      angle = angle - 90
  else:
      angle = angle + 90

  x1 = xc + math.cos(math.radians(angle))*rminor
  y1 = yc + math.sin(math.radians(angle))*rminor
  x2 = xc + math.cos(math.radians(angle+180))*rminor
  y2 = yc + math.sin(math.radians(angle+180))*rminor
  
  cv2.line(img, (int(x1),int(y1)), (int(x2),int(y2)), (255, 0, 0), 3)