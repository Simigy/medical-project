"""
CAPTCHA Solver Service

This module provides functions to solve CAPTCHAs using various services.
It supports both image-based CAPTCHAs and reCAPTCHA.

You can use this with either:
1. 2Captcha API (paid service)
2. Local OCR for simple CAPTCHAs
"""

import requests
import time
import base64
import os
import json
from typing import Optional, Dict, Any, Union
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("captcha_solver")

# Configuration
CAPTCHA_API_KEY = os.environ.get("CAPTCHA_API_KEY", "")  # Main API key from environment variable
TWOCAPTCHA_API_KEY = os.environ.get("TWOCAPTCHA_API_KEY", CAPTCHA_API_KEY)  # Use main key as fallback
ANTICAPTCHA_API_KEY = os.environ.get("ANTICAPTCHA_API_KEY", CAPTCHA_API_KEY)  # Use main key as fallback
CAPSOLVER_API_KEY = os.environ.get("CAPSOLVER_API_KEY", CAPTCHA_API_KEY)  # Use main key as fallback

class CaptchaSolver:
    """
    Class to solve various types of CAPTCHAs using different services
    """

    def __init__(self, api_key: str = "", service: str = "2captcha"):
        """
        Initialize the CAPTCHA solver

        Args:
            api_key (str): API key for the CAPTCHA solving service
            service (str): Service to use ('2captcha', 'anticaptcha', 'capsolver', 'local')
        """
        self.service = service.lower()

        # Select the appropriate API key based on the service
        if self.service == "2captcha":
            self.api_key = api_key or TWOCAPTCHA_API_KEY
        elif self.service == "anticaptcha":
            self.api_key = api_key or ANTICAPTCHA_API_KEY
        elif self.service == "capsolver":
            self.api_key = api_key or CAPSOLVER_API_KEY
        else:
            self.api_key = api_key or CAPTCHA_API_KEY

        # Check if we have a valid API key for paid services
        if self.service in ["2captcha", "anticaptcha", "capsolver"] and not self.api_key:
            logger.warning(f"No API key provided for {service}. CAPTCHA solving may fail.")

        # Log the service being used
        logger.info(f"Using CAPTCHA solver service: {self.service}")
        if self.api_key:
            logger.info(f"API key is set for {self.service}")
        else:
            logger.warning(f"No API key set for {self.service}")

        # Try to import optional dependencies
        self.has_pytesseract = False
        self.has_cv2 = False

        if self.service == "local":
            try:
                import pytesseract
                import cv2
                self.pytesseract = pytesseract
                self.cv2 = cv2
                self.has_pytesseract = True
                self.has_cv2 = True
            except ImportError:
                logger.warning("Local OCR requires pytesseract and opencv-python. Install with: pip install pytesseract opencv-python")

    def solve_image_captcha(self, image_path: str = "", image_url: str = "", image_base64: str = "",
                           timeout: int = 60) -> Optional[str]:
        """
        Solve an image-based CAPTCHA

        Args:
            image_path (str): Path to the CAPTCHA image file
            image_url (str): URL of the CAPTCHA image
            image_base64 (str): Base64-encoded CAPTCHA image
            timeout (int): Maximum time to wait for the solution in seconds

        Returns:
            str: The solved CAPTCHA text or None if failed
        """
        # Get the image data
        image_data = None

        if image_path:
            try:
                with open(image_path, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode("utf-8")
            except Exception as e:
                logger.error(f"Error reading image file: {e}")
                return None

        elif image_url:
            try:
                response = requests.get(image_url, timeout=10)
                response.raise_for_status()
                image_data = base64.b64encode(response.content).decode("utf-8")
            except Exception as e:
                logger.error(f"Error downloading image: {e}")
                return None

        elif image_base64:
            image_data = image_base64

        else:
            logger.error("No image provided")
            return None

        # Choose the appropriate service
        if self.service == "2captcha":
            return self._solve_with_2captcha(image_data, timeout)
        elif self.service == "anticaptcha":
            return self._solve_with_anticaptcha(image_data, timeout)
        elif self.service == "local":
            return self._solve_with_local_ocr(image_data)
        else:
            logger.error(f"Unknown service: {self.service}")
            return None

    def solve_recaptcha(self, site_key: str, page_url: str, timeout: int = 180) -> Optional[str]:
        """
        Solve a reCAPTCHA

        Args:
            site_key (str): The reCAPTCHA site key
            page_url (str): The URL of the page with the reCAPTCHA
            timeout (int): Maximum time to wait for the solution in seconds

        Returns:
            str: The reCAPTCHA solution token or None if failed
        """
        if self.service == "2captcha":
            return self._solve_recaptcha_with_2captcha(site_key, page_url, timeout)
        elif self.service == "anticaptcha":
            return self._solve_recaptcha_with_anticaptcha(site_key, page_url, timeout)
        else:
            logger.error(f"reCAPTCHA solving not supported with {self.service}")
            return None

    def _solve_with_2captcha(self, image_data: str, timeout: int) -> Optional[str]:
        """
        Solve a CAPTCHA using 2Captcha service

        Args:
            image_data (str): Base64-encoded image data
            timeout (int): Maximum time to wait for the solution

        Returns:
            str: The solved CAPTCHA text or None if failed
        """
        logger.info("Solving CAPTCHA with 2Captcha...")

        try:
            # Submit the CAPTCHA
            url = "https://2captcha.com/in.php"
            data = {
                "key": self.api_key,
                "method": "base64",
                "body": image_data,
                "json": 1
            }

            response = requests.post(url, data=data)
            response.raise_for_status()
            result = response.json()

            if result["status"] != 1:
                logger.error(f"Error submitting CAPTCHA: {result['request']}")
                return None

            captcha_id = result["request"]

            # Wait for the solution
            url = "https://2captcha.com/res.php"
            params = {
                "key": self.api_key,
                "action": "get",
                "id": captcha_id,
                "json": 1
            }

            start_time = time.time()
            while time.time() - start_time < timeout:
                time.sleep(5)  # Wait 5 seconds between checks

                response = requests.get(url, params=params)
                response.raise_for_status()
                result = response.json()

                if result["status"] == 1:
                    logger.info("CAPTCHA solved successfully")
                    return result["request"]

                if result["request"] != "CAPCHA_NOT_READY":
                    logger.error(f"Error solving CAPTCHA: {result['request']}")
                    return None

            logger.error("CAPTCHA solving timed out")
            return None

        except Exception as e:
            logger.error(f"Error solving CAPTCHA: {e}")
            return None

    def _solve_recaptcha_with_2captcha(self, site_key: str, page_url: str, timeout: int) -> Optional[str]:
        """
        Solve a reCAPTCHA using 2Captcha service

        Args:
            site_key (str): The reCAPTCHA site key
            page_url (str): The URL of the page with the reCAPTCHA
            timeout (int): Maximum time to wait for the solution

        Returns:
            str: The reCAPTCHA solution token or None if failed
        """
        logger.info("Solving reCAPTCHA with 2Captcha...")

        try:
            # Submit the reCAPTCHA
            url = "https://2captcha.com/in.php"
            data = {
                "key": self.api_key,
                "method": "userrecaptcha",
                "googlekey": site_key,
                "pageurl": page_url,
                "json": 1
            }

            response = requests.post(url, data=data)
            response.raise_for_status()
            result = response.json()

            if result["status"] != 1:
                logger.error(f"Error submitting reCAPTCHA: {result['request']}")
                return None

            captcha_id = result["request"]

            # Wait for the solution
            url = "https://2captcha.com/res.php"
            params = {
                "key": self.api_key,
                "action": "get",
                "id": captcha_id,
                "json": 1
            }

            start_time = time.time()
            while time.time() - start_time < timeout:
                time.sleep(5)  # Wait 5 seconds between checks

                response = requests.get(url, params=params)
                response.raise_for_status()
                result = response.json()

                if result["status"] == 1:
                    logger.info("reCAPTCHA solved successfully")
                    return result["request"]

                if result["request"] != "CAPCHA_NOT_READY":
                    logger.error(f"Error solving reCAPTCHA: {result['request']}")
                    return None

            logger.error("reCAPTCHA solving timed out")
            return None

        except Exception as e:
            logger.error(f"Error solving reCAPTCHA: {e}")
            return None

    def _solve_with_anticaptcha(self, image_data: str, timeout: int) -> Optional[str]:
        """
        Solve a CAPTCHA using Anti-Captcha service

        Args:
            image_data (str): Base64-encoded image data
            timeout (int): Maximum time to wait for the solution

        Returns:
            str: The solved CAPTCHA text or None if failed
        """
        logger.info("Solving CAPTCHA with Anti-Captcha...")

        try:
            # Submit the CAPTCHA
            url = "https://api.anti-captcha.com/createTask"
            data = {
                "clientKey": self.api_key,
                "task": {
                    "type": "ImageToTextTask",
                    "body": image_data,
                    "phrase": False,
                    "case": False,
                    "numeric": 0,
                    "math": False,
                    "minLength": 0,
                    "maxLength": 0
                }
            }

            response = requests.post(url, json=data)
            response.raise_for_status()
            result = response.json()

            if result["errorId"] != 0:
                logger.error(f"Error submitting CAPTCHA: {result['errorDescription']}")
                return None

            task_id = result["taskId"]

            # Wait for the solution
            url = "https://api.anti-captcha.com/getTaskResult"
            data = {
                "clientKey": self.api_key,
                "taskId": task_id
            }

            start_time = time.time()
            while time.time() - start_time < timeout:
                time.sleep(5)  # Wait 5 seconds between checks

                response = requests.post(url, json=data)
                response.raise_for_status()
                result = response.json()

                if result["errorId"] != 0:
                    logger.error(f"Error checking CAPTCHA status: {result['errorDescription']}")
                    return None

                if result["status"] == "ready":
                    logger.info("CAPTCHA solved successfully")
                    return result["solution"]["text"]

                if result["status"] != "processing":
                    logger.error(f"Unknown status: {result['status']}")
                    return None

            logger.error("CAPTCHA solving timed out")
            return None

        except Exception as e:
            logger.error(f"Error solving CAPTCHA: {e}")
            return None

    def _solve_recaptcha_with_anticaptcha(self, site_key: str, page_url: str, timeout: int) -> Optional[str]:
        """
        Solve a reCAPTCHA using Anti-Captcha service

        Args:
            site_key (str): The reCAPTCHA site key
            page_url (str): The URL of the page with the reCAPTCHA
            timeout (int): Maximum time to wait for the solution

        Returns:
            str: The reCAPTCHA solution token or None if failed
        """
        logger.info("Solving reCAPTCHA with Anti-Captcha...")

        try:
            # Submit the reCAPTCHA
            url = "https://api.anti-captcha.com/createTask"
            data = {
                "clientKey": self.api_key,
                "task": {
                    "type": "NoCaptchaTaskProxyless",
                    "websiteURL": page_url,
                    "websiteKey": site_key
                }
            }

            response = requests.post(url, json=data)
            response.raise_for_status()
            result = response.json()

            if result["errorId"] != 0:
                logger.error(f"Error submitting reCAPTCHA: {result['errorDescription']}")
                return None

            task_id = result["taskId"]

            # Wait for the solution
            url = "https://api.anti-captcha.com/getTaskResult"
            data = {
                "clientKey": self.api_key,
                "taskId": task_id
            }

            start_time = time.time()
            while time.time() - start_time < timeout:
                time.sleep(5)  # Wait 5 seconds between checks

                response = requests.post(url, json=data)
                response.raise_for_status()
                result = response.json()

                if result["errorId"] != 0:
                    logger.error(f"Error checking reCAPTCHA status: {result['errorDescription']}")
                    return None

                if result["status"] == "ready":
                    logger.info("reCAPTCHA solved successfully")
                    return result["solution"]["gRecaptchaResponse"]

                if result["status"] != "processing":
                    logger.error(f"Unknown status: {result['status']}")
                    return None

            logger.error("reCAPTCHA solving timed out")
            return None

        except Exception as e:
            logger.error(f"Error solving reCAPTCHA: {e}")
            return None

    def _solve_with_local_ocr(self, image_data: str) -> Optional[str]:
        """
        Solve a CAPTCHA using local OCR (Tesseract)

        Args:
            image_data (str): Base64-encoded image data

        Returns:
            str: The solved CAPTCHA text or None if failed
        """
        if not self.has_pytesseract or not self.has_cv2:
            logger.error("Local OCR requires pytesseract and opencv-python")
            return None

        logger.info("Solving CAPTCHA with local OCR...")

        try:
            # Decode the image
            import numpy as np
            image_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = self.cv2.imdecode(nparr, self.cv2.IMREAD_COLOR)

            # Preprocess the image
            gray = self.cv2.cvtColor(image, self.cv2.COLOR_BGR2GRAY)
            thresh = self.cv2.threshold(gray, 0, 255, self.cv2.THRESH_BINARY_INV + self.cv2.THRESH_OTSU)[1]

            # Apply noise removal
            kernel = self.cv2.getStructuringElement(self.cv2.MORPH_RECT, (2, 2))
            opening = self.cv2.morphologyEx(thresh, self.cv2.MORPH_OPEN, kernel, iterations=1)

            # OCR the image
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
            text = self.pytesseract.image_to_string(opening, config=custom_config)

            # Clean up the text
            text = text.strip()

            if text:
                logger.info(f"CAPTCHA solved with local OCR: {text}")
                return text
            else:
                logger.error("Local OCR failed to extract text")
                return None

        except Exception as e:
            logger.error(f"Error solving CAPTCHA with local OCR: {e}")
            return None

# Example usage
if __name__ == "__main__":
    # Example with 2Captcha
    solver = CaptchaSolver(api_key=TWOCAPTCHA_API_KEY, service="2captcha")

    # Test with a sample CAPTCHA image URL
    image_url = "https://example.com/captcha.jpg"
    solution = solver.solve_image_captcha(image_url=image_url)

    if solution:
        print(f"CAPTCHA solution: {solution}")
    else:
        print("Failed to solve CAPTCHA")

    # Test with a sample reCAPTCHA
    site_key = "6LcXXXXXXXXXXXXXXXXXXXXX"  # Replace with actual site key
    page_url = "https://example.com/recaptcha"
    solution = solver.solve_recaptcha(site_key, page_url)

    if solution:
        print(f"reCAPTCHA solution: {solution}")
    else:
        print("Failed to solve reCAPTCHA")
