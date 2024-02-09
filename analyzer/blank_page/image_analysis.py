from PIL import Image
import numpy as np
from io import BytesIO
import cv2
import pytesseract
import zipfile


class ExperimentScreenshotBlankDetector:
    
    def experiment_is_screenshot_blank(self, image_path, std_dev_threshold=6, edge_threshold=2000, text_threshold=10):
        image = Image.open(image_path)

        # Convert image to grey-scale
        gray_image = np.array(image.convert('L'))

        # Calculate the standard deviation of the grayscale image
        std_dev = np.std(gray_image)

        # Use Canny edge detection to find edges in the image
        # First threshold: 100 (Represents the lower boundary for pixel intensity gradient. If a pixel gradient is below this threshold, it is considered not to be an edge)
        # Second threshold: 200 (Represents the upper boundary for pixel intensity gradient. If a pixel gradient is above this threshold, it is considered to be a strong edge.)
        edges = cv2.Canny(gray_image, 100, 200)
        edge_count = np.sum(edges > 0)

        # Use OCR to detect text in the image
        text = pytesseract.image_to_string(image)
        text_count = len(text.strip())

        stats = {
            "std_dev": std_dev,
            "edge_count": int(edge_count),
            "text_count": int(text_count)
        }

        # Check against thresholds
        if std_dev < std_dev_threshold and edge_count < edge_threshold and text_count < text_threshold:
            return True, stats
        
        return False, stats


    # Only to be used to determine threshold values
    def experimentation_for_blank_page_threshold_values(self):
        print("\nNon-blank")
        self.experiment_is_screenshot_blank("test_image_analysis/screenshot_aft.png")

        print("\nGoogle")
        self.experiment_is_screenshot_blank("test_image_analysis/Google.JPG")

        print("\nFacebook")
        self.experiment_is_screenshot_blank("test_image_analysis/screenshot_fb.png")

        print("\nBlank (dataset)")
        self.experiment_is_screenshot_blank("test_image_analysis/screenshot_blank.png")

        print("\nBlank with few words")
        self.experiment_is_screenshot_blank("test_image_analysis/blank_with_few_words.JPG")

        print("\nBlank with simple words")
        self.experiment_is_screenshot_blank("test_image_analysis/blank_with_simple_words.JPG")

        print("\nBlank with grey line")
        self.experiment_is_screenshot_blank("test_image_analysis/blank_with_grey_line.JPG")

        print("\nBlank")
        self.experiment_is_screenshot_blank("test_image_analysis/complete_blank.JPG")

        print("\nBlank (Black)")
        self.experiment_is_screenshot_blank("test_image_analysis/complete_blank_black.JPG")

        print("\nBlank (White)")
        self.experiment_is_screenshot_blank("test_image_analysis/complete_blank_white.JPG")


class BlankScreenshotDetector:
    def __init__(self):
        self.std_dev_threshold = 6
        self.edge_threshold = 2000
        self.text_threshold = 10

    def get_standard_deviation_of_grayscaled_ss(self, gray_image):
        std_dev = np.std(gray_image) # Calculate the standard deviation of the grayscale image
        return std_dev


    # Use Canny edge detection to find edges in the image
    # First threshold: 100 (Represents the lower boundary for pixel intensity gradient. If a pixel gradient is below this threshold, it is considered not to be an edge)
    # Second threshold: 200 (Represents the upper boundary for pixel intensity gradient. If a pixel gradient is above this threshold, it is considered to be a strong edge.)
    def get_canny_edge_count_of_grayscaled_ss(self, gray_image):
        edges = cv2.Canny(gray_image, 100, 200)
        edge_count = np.sum(edges > 0)
        return edge_count
    

    # Use OCR to detect text in the image
    def get_length_of_text_in_ss(self, image):
        text = pytesseract.image_to_string(image)
        text_count = len(text.strip())
        return text_count
    

    def generate_screenshot_stats(self, sd, edge_count, text_count):
        stats = {
            "std_dev": sd,
            "edge_count": int(edge_count),
            "text_count": int(text_count)
        }
        return stats
    

    def is_potential_blank_ss(self, sd, edge_count, text_count):
        is_less_than_sd = sd < self.std_dev_threshold 
        is_less_than_ec = edge_count < self.edge_threshold 
        is_less_than_tc = text_count < self.text_threshold

        return is_less_than_sd and is_less_than_ec and is_less_than_tc


    def is_screenshot_blank(self, zip_path, image_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            with zip_ref.open(image_path) as image_file:
                image = Image.open(BytesIO(image_file.read()))
                gray_image = np.array(image.convert('L')) # Convert image to grey-scale
                
                std_dev = self.get_standard_deviation_of_grayscaled_ss(gray_image)
                edge_count = self.get_canny_edge_count_of_grayscaled_ss(gray_image)
                text_count = self.get_length_of_text_in_ss(image)
                
                stats = self.generate_screenshot_stats(std_dev, edge_count, text_count)

                # Check against thresholds
                return self.is_potential_blank_ss(std_dev, edge_count, text_count), stats

