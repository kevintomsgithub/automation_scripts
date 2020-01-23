from pytesseract import image_to_string
import argparse
import cv2
import os

if not os.path.exists('files_generated'):
    os.makedirs('files_generated')
    
ap = argparse.ArgumentParser()
ap.add_argument("-hw", "--hw", type=int, default=10,
    help="Number of images to be considered")
ap.add_argument("-e", "--export_image_folder", type=str, default="images_extracted_from_ppt",
    help="path to extract images from ppt")
ap.add_argument("-py", "--py_file", type=str, default="files_generated/extracted_python_file.py",
    help="name of python file generated")
args = vars(ap.parse_args())

# set to -1 for all images
hw_images = args["hw"]
export_folder_name = args["export_image_folder"]
python_file = args["py_file"]
a = []
for i in [k for i,j,k in os.walk(export_folder_name)][0]:
    if '.DS_Store' not in i:
        a.append(i)
file_names = [f"{export_folder_name}/{i}.png" for i in sorted([int(i.split('.')[0]) for i in a])]
text_from_image = {}
total_number_of_lines = 0

# Detect the contours in the image and extract the text
def convert_image_to_text(image_filename):
    """Function to convert image to text using OCR and opencv"""

    config = ("-l eng --oem 1 --psm 6")
    c_min = 500
    text_extracted = []

    def show_image(image):
        """Function to show image"""
        cv2.imshow("image", image)
        cv2.waitKey(0)

    def sort_contours_and_get_filtered_bb(contours, c_min, c_max):
        """Sort the given contours from top to bottom"""
        notebook_cells = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area>c_min and area<c_max:
                notebook_cells.append(cv2.boundingRect(contour))
                # cv2.drawContours(image, contour, -1, (0, 255, 0), 3)
        notebook_cells_sorted = sorted(notebook_cells, key=lambda bb: bb[1])
        return notebook_cells_sorted

    # Read image from disk 
    image = cv2.imread(image_filename)
    # Convert Image to grayscale
    imgray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Get the threshold image from the grayscale image
    thresh_image = cv2.adaptiveThreshold(imgray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
                cv2.THRESH_BINARY, 11, 2)

    # Find all the contours in the image
    contours, _ = cv2.findContours(thresh_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    # Find the largest contour in the image
    c_max = max(list(map(cv2.contourArea, contours)))

    sorted_bb = sort_contours_and_get_filtered_bb(contours, c_min, c_max)
    # show_image(thresh_image)

    for cell in sorted_bb:
        x, y, w, h = cell
        bounding_image = thresh_image[y:y+h, x:x+w]
        blur_image = cv2.GaussianBlur(bounding_image,(9,9),1)
        text = image_to_string(blur_image, config=config)
        text_extracted.append(text)
        # print(f"--------- Text from image --------- \n {text}")
        # show_image(bounding_image)

    cv2.destroyAllWindows()
    return text_extracted
                

# Refine the text extracted from the image       
def refine_text(text_from_image):
    text_list = []
    for item in text_from_image:
        for text in item.split('\n'):
            if text != '' and '#' not in text:
                text_list.append(text)
    return text_list
        

# Set the slice parameter for test case
file_names_slice = file_names if hw_images == -1 else file_names[:hw_images]
total_images = len(file_names_slice)


# Extract the text from the image and refine it
for index, item in enumerate(file_names_slice):
    print(f"[INFO] Extracting text from {index} of {total_images} images...")
    text = convert_image_to_text(item)
    text_from_image[index] = refine_text(text)
    total_number_of_lines += len(text_from_image[index])


print(f"[INFO] Total number of lines of code extracted = {total_number_of_lines}")
print("Done!")
print(f"[INFO] Writing extracted text to python file: {python_file}")
with open(python_file, 'w') as f:
    for text_list in text_from_image.values():
        for text in text_list:
            if text != '':
                f.write(text + '\n')
print("Done!")