import cv2
import matplotlib.pyplot as plt
import numpy as np

def grey(image):
    return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

def gauss(image):
    return cv2.GaussianBlur(image, (5, 5), 0)

def canny(image):
    return cv2.Canny(image, 50, 150)

def region(image):
    height, width = image.shape[:2]
    triangle = np.array([[(100, height), (475, 325), (width, height)]], dtype=np.int32)
    mask = np.zeros_like(image)
    cv2.fillPoly(mask, triangle, 255)
    masked_image = cv2.bitwise_and(image, mask)
    return masked_image

def display_lines(image, lines):
    lines_image = np.zeros_like(image)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line.reshape(4)
            cv2.line(lines_image, (x1, y1), (x2, y2), (255, 0, 0), 10)
    return lines_image

def average(image, lines):
    left = []
    right = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line.reshape(4)
            parameters = np.polyfit((x1, x2), (y1, y2), 1)
            slope = parameters[0]
            y_int = parameters[1]
            if slope < 0:
                left.append((slope, y_int))
            else:
                right.append((slope, y_int))
        if left:
            left_avg = np.average(left, axis=0)
            left_line = make_points(image, left_avg)
        else:
            left_line = None
        if right:
            right_avg = np.average(right, axis=0)
            right_line = make_points(image, right_avg)
        else:
            right_line = None
        return np.array([left_line, right_line])

def make_points(image, average):
    slope, y_int = average
    y1 = image.shape[0]
    y2 = int(y1 * (3 / 5))
    x1 = int((y1 - y_int) / slope)
    x2 = int((y2 - y_int) / slope)
    return np.array([x1, y1, x2, y2])

image_path = "/content/lanelines_thirdPass.jpg"
image = cv2.imread(image_path)
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB

grey_image = grey(image)
blurred_image = gauss(grey_image)
edges = canny(blurred_image)
masked_edges = region(edges)

lines = cv2.HoughLinesP(masked_edges, 2, np.pi / 180, 100, np.array([]), minLineLength=40, maxLineGap=5)
averaged_lines = average(image, lines)

black_lines = display_lines(image, averaged_lines)

lanes = cv2.addWeighted(image, 0.8, black_lines, 1, 1)

plt.imshow(lanes)
plt.show()
