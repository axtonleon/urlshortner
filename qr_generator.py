import qrcode
from io import BytesIO
from fastapi.responses import StreamingResponse
import logging

logger = logging.getLogger(__name__)

def generate_qr_code(url: str, box_size: int = 10, border: int = 4) -> BytesIO:
    """
    Generate a QR code for the given URL.
    
    Args:
        url (str): The URL to encode in the QR code
        box_size (int): Size of each box in the QR code (default: 10)
        border (int): Border size around the QR code (default: 4)
    
    Returns:
        BytesIO: A BytesIO object containing the QR code image
    """
    try:
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=box_size,
            border=border,
        )
        
        # Add data
        qr.add_data(url)
        qr.make(fit=True)
        
        # Create an image from the QR Code
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to BytesIO
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        return img_io
    except Exception as e:
        logger.error(f"Error generating QR code: {str(e)}")
        raise 