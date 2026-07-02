from pathlib import Path
from PIL import Image


class ImageProcessor:
    TEMPLATE_DIR = Path("templates")

    @staticmethod
    def load_image(image_path: str):
        """Open the uploaded image."""
        return Image.open(image_path).convert("RGBA")

    @classmethod
    def load_footer(cls, template="default"):
        """Load the selected footer."""

        footer_path = cls.TEMPLATE_DIR / template / "footer.png"

        if not footer_path.exists():
            raise FileNotFoundError(
                f"Footer not found: {footer_path}"
            )

        return Image.open(footer_path).convert("RGBA")

    @staticmethod
    def trim_footer(footer):
        """
        Remove transparent space around the footer.
        """

        bbox = footer.getbbox()

        if bbox:
            return footer.crop(bbox)

        return footer

    @staticmethod
    def resize_footer(photo, footer):
        """
        Resize footer to match the width of the photo.
        Aspect ratio is preserved.
        """

        scale = photo.width / footer.width

        new_width = photo.width
        new_height = int(footer.height * scale)

        return footer.resize(
            (new_width, new_height),
            Image.Resampling.LANCZOS
        )

    @staticmethod
    def apply_footer(photo, footer):
        """
        Overlay the footer on the bottom of the photo.
        Transparency and gradients are preserved.
        """

        result = photo.copy()

        y = photo.height - footer.height

        result.alpha_composite(
            footer,
            (0, y)
        )

        return result

    @staticmethod
    def save_image(image, output_path):
        """
        Save the final image.
        """

        image.convert("RGB").save(
            output_path,
            quality=100
        )

    @classmethod
    def process(cls, image_path, output_path, template="default"):
        """
        Complete processing pipeline.
        """

        # Load photo
        photo = cls.load_image(image_path)

        # Load footer
        footer = cls.load_footer(template)

        # Remove transparent space
        footer = cls.trim_footer(footer)

        # Resize footer
        footer = cls.resize_footer(photo, footer)

        # Overlay footer
        result = cls.apply_footer(photo, footer)

        # Save image
        cls.save_image(result, output_path)