import unittest
from PIL import Image, ImageDraw
from tools.validate_pet_assets import COUNTS, SIZE, inspect_sheet, inspect_pet, ROOT


def valid_sheet():
    image = Image.new("RGBA", SIZE)
    draw = ImageDraw.Draw(image)
    for row, count in enumerate(COUNTS):
        for col in range(count):
            draw.rectangle((col * 192 + 30, row * 208 + 30, col * 192 + 150, row * 208 + 170), fill="white")
    return image


class SheetValidationTests(unittest.TestCase):
    def test_valid(self):
        self.assertTrue(inspect_sheet(valid_sheet())["ok"])

    def test_wrong_size(self):
        self.assertFalse(inspect_sheet(Image.new("RGBA", (1536, 1872)))["ok"])

    def test_missing_frame(self):
        image = valid_sheet()
        image.paste((0, 0, 0, 0), (0, 0, 192, 208))
        self.assertIn("Missing artwork in cell 0,0", inspect_sheet(image)["errors"])

    def test_unused_cell(self):
        image = valid_sheet()
        image.putpixel((7 * 192 + 30, 30), (255, 255, 255, 255))
        self.assertIn("Artwork in unused cell 0,7", inspect_sheet(image)["errors"])

    def test_boundary_contact(self):
        image = valid_sheet()
        image.putpixel((0, 50), (255, 255, 255, 255))
        self.assertIn("Artwork touches a cell boundary at 0,0", inspect_sheet(image)["errors"])

    def test_no_alpha(self):
        self.assertFalse(inspect_sheet(valid_sheet().convert("RGB"))["ok"])

    def test_new_mobile_suits(self):
        for name in ("green-zaku", "red-zaku", "gouf", "gm"):
            with self.subTest(pet=name):
                self.assertTrue(inspect_pet(ROOT / "pets" / name)["ok"])

    def test_legacy_extra_idle_cells_remain_visible(self):
        # Preserve the originals and disclose their existing incompatibility.
        # This does not waive the layout error or report the old assets as valid.
        for name in ("sd-gundam-codex-pet", "chibi-asuka", "chibi-miku"):
            with self.subTest(pet=name):
                report = inspect_pet(ROOT / "pets" / name)
                self.assertFalse(report["ok"])
                self.assertIn("Artwork in unused cell 0,6", report["layout"]["errors"])


if __name__ == "__main__":
    unittest.main()
