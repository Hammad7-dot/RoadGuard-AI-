import unittest

from utils.geotag import extract_gps, _to_degrees


class FakeExif(dict):
    """
    Minimal stand-in for PIL's Image.Exif: falsy-check must be True
    (a real Exif block with tags in it), and get_ifd(IFD.GPSInfo)
    returns the raw GPS sub-IFD dict, mirroring how extract_gps
    actually reads GPS data (see D9 in docs/DECISIONS.md - the
    historical bug this module fixed).
    """

    def __init__(self, gps_ifd):
        super().__init__()
        self._gps_ifd = gps_ifd

    def __bool__(self):
        return True

    def get_ifd(self, tag):
        return self._gps_ifd


class FakeImage:
    def __init__(self, gps_ifd):
        self._exif = FakeExif(gps_ifd)

    def getexif(self):
        return self._exif


class GeotagTest(unittest.TestCase):
    def test_to_degrees_converts_dms_to_decimal(self):
        self.assertAlmostEqual(_to_degrees((40, 26, 46.0)), 40.446111, places=5)

    def test_extract_gps_returns_none_without_gps_ifd(self):
        image = FakeImage(gps_ifd={})
        self.assertIsNone(extract_gps(image))

    def test_extract_gps_parses_north_east_coordinates(self):
        gps_ifd = {
            1: "N",                    # GPSLatitudeRef
            2: (40.0, 26.0, 46.0),      # GPSLatitude
            3: "E",                    # GPSLongitudeRef
            4: (79.0, 58.0, 56.0),      # GPSLongitude
        }

        lat, lon = extract_gps(FakeImage(gps_ifd))

        self.assertAlmostEqual(lat, 40.446111, places=5)
        self.assertAlmostEqual(lon, 79.982222, places=5)

    def test_extract_gps_applies_south_west_sign_flip(self):
        gps_ifd = {
            1: "S",
            2: (40.0, 26.0, 46.0),
            3: "W",
            4: (79.0, 58.0, 56.0),
        }

        lat, lon = extract_gps(FakeImage(gps_ifd))

        self.assertLess(lat, 0)
        self.assertLess(lon, 0)

    def test_extract_gps_handles_malformed_data_gracefully(self):
        # GPSLatitudeRef present but GPSLatitude itself missing -
        # extract_gps must swallow the resulting KeyError rather than
        # raising and breaking the upload flow.
        gps_ifd = {1: "N"}

        self.assertIsNone(extract_gps(FakeImage(gps_ifd)))


if __name__ == "__main__":
    unittest.main()
