import os
import io
import logging
import tempfile
import pytesseract
from PIL import Image

def extract_text_from_image(image_file):
    """
    Extract text from an uploaded image using pytesseract OCR.
    
    Args:
        image_file: The uploaded image file object
        
    Returns:
        str: The extracted text from the image
    """
    logging.debug("Starting OCR processing")
    
    # Check if tesseract is installed
    try:
        pytesseract.get_tesseract_version()
    except Exception as e:
        logging.error(f"Tesseract not properly installed: {str(e)}")
        raise RuntimeError("Tesseract OCR is not properly installed. Please install Tesseract OCR to use this feature.")
    
    try:
        # Create a temporary file to store the image
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            image_file.save(temp_file.name)
            temp_filename = temp_file.name
        
        # Open the image with PIL
        with Image.open(temp_filename) as img:
            # Preprocessing for better OCR results
            # Convert to grayscale
            if img.mode != 'L':
                img = img.convert('L')
                
            # Use pytesseract to extract text
            text = pytesseract.image_to_string(img)
            
            logging.info(f"OCR extracted {len(text)} characters")
            
            # Clean up the temporary file
            os.unlink(temp_filename)
            
            if not text or len(text.strip()) < 10:
                raise ValueError("Could not extract sufficient text from the image. Please try a clearer image.")
            
            return text
    
    except Exception as e:
        if 'temp_filename' in locals():
            try:
                os.unlink(temp_filename)
            except:
                pass
        
        logging.error(f"OCR processing error: {str(e)}")
        raise
