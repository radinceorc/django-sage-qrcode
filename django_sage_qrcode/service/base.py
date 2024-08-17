import os
import uuid
import segno
import logging
from typing import Optional
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    raise ImportError("Install `pillow` package. Run `pip install pillow`.")

from django_sage_qrcode.helpers.type import HexCode

logger = logging.getLogger(__name__)


class QRCodeBase:
    """A base class for generating and handling QR codes.

    Attributes:
        qr_image (Optional[Image.Image]): Stores the generated QR code image.

    """

    def __init__(self) -> None:
        """Initializes a new instance of QRCodeBase with no QR code image."""
        logging.info("Initializing QRCodeBase instance.")
        self.qr_image: Optional[Image.Image] = None

    def generate_qr_code(
        self,
        data: dict,
        scale: int = 10,
        error: str = "h",
        custom: Path = None,
        color: HexCode = "#000000",
        color2: HexCode = "#FFFFFF",
        color3: HexCode = "#000000",
    ) -> bool:
        """Generates a QR code image based on the provided data and parameters.

        Args:
            data (dict): The data to encode in the QR code.
            scale (int, optional): Scale factor for the QR code size. Default is 10.
            error (str, optional): Error correction level ('h', 'q', 'm', 'l'). Default is 'h'.
            custom (str): Path to a custom image to overlay on the QR code. Default is None.
            color (str, optional): Color of the QR code. Default is '#000000'.
            color2 (str, optional): Background color of the QR code. Default is '#FFFFFF'.
            color3 (str, optional): Finder pattern color of the QR code. Default is '#000000'.

        Returns:
            bool: True if a custom QR code is generated, False otherwise.

        """
        logging.debug(f"Generating QR code with data: {data}")
        qr = segno.make(data, error=error)

        if custom:
            logging.info("Applying custom image to QR code.")
            self.qr_image = self.customize_qr_code(qr, custom)
            return True

        try:
            self.qr_image = qr.to_pil(
                scale=scale, dark=color, light=color2, finder_dark=color3
            )
        except ValueError as e:
            logging.error(f"Error applying color: {e}")
            self.qr_image = qr.to_pil(scale=scale)

        if self.qr_image.mode != "RGBA":
            self.qr_image = self.qr_image.convert("RGBA")

        logging.info("QR code generated successfully.")
        return False

    def show_qr_code(self, save: bool = False) -> Image.Image:
        """Displays the generated QR code image.

        Args:
            save (bool, optional): Whether to save the QR code image to a file. Default is False.

        Returns:
            Image.Image: The generated QR code image.

        """
        logging.debug("Attempting to display QR code.")
        if self.qr_image is None:
            logging.error("No QR code image to display.")
            raise ValueError("QR code image is not generated.")

        if save:
            logging.info("Saving QR code image.")
            self.save_qr_code()

        # self.qr_image.show()
        logging.info("QR code displayed successfully.")
        return self.qr_image

    def save_qr_code(self) -> None:
        """Saves the generated QR code image to a file."""
        logging.debug("Attempting to save QR code image.")
        if self.qr_image is None:
            logging.error("No QR code image to save.")
            raise ValueError("QR code image is not generated.")

        unique_filename = str(uuid.uuid4()) + ".png"
        self.qr_image.save(unique_filename)
        logging.info(f"QR code image saved as {unique_filename}")

    def customize_qr_code(
        self, obj: segno.QRCode, path: str, scale: int = 10
    ) -> Image.Image:
        """Applies custom styling to the QR code by overlaying it with another
        image.

        Args:
            obj (segno.QRCode): The QR code object to customize.
            path (str): Path to the custom image file.
            scale (int, optional): Scale factor for the custom image. Default is 10.

        Returns:
            Image.Image: The customized QR code image.

        """
        logging.debug(f"Customizing QR code with image from path: {path}")
        target_extension = os.path.splitext(path)[1]
        unique_filename = str(uuid.uuid4()) + target_extension
        obj.to_artistic(background=path, target=unique_filename, scale=8)
        customized_qr = Image.open(unique_filename)
        logging.info("Customized QR code generated successfully.")
        return customized_qr
