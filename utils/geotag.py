"""
RoadGuard AI
GPS/EXIF Helper
----------------

Most phone cameras embed GPS coordinates in a photo's EXIF metadata.
This module pulls that out (if present) so a road-damage photo can be
plotted on a map without the user having to type coordinates by hand.
Falls back to None if the image has no GPS tag (e.g. screenshots,
downloaded stock photos, or a camera with location services off) -
callers should let the user enter coordinates manually in that case.
"""

from typing import Optional, Tuple

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


def _to_degrees(value) -> float:
    """Convert an EXIF GPS coordinate (degrees, minutes, seconds) to decimal degrees."""
    d, m, s = (float(x) for x in value)
    return d + (m / 60.0) + (s / 3600.0)


def extract_gps(image: Image.Image) -> Optional[Tuple[float, float]]:
    """
    Return (latitude, longitude) as decimal degrees if the image has
    GPS EXIF data, otherwise None.
    """

    try:
        exif = image.getexif()
        if not exif:
            return None

        gps_info = {}
        for tag_id, value in exif.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == "GPSInfo":
                for gps_tag_id, gps_value in value.items():
                    gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                    gps_info[gps_tag] = gps_value

        if not gps_info:
            return None

        lat = _to_degrees(gps_info["GPSLatitude"])
        if gps_info.get("GPSLatitudeRef") in ("S", "s"):
            lat = -lat

        lon = _to_degrees(gps_info["GPSLongitude"])
        if gps_info.get("GPSLongitudeRef") in ("W", "w"):
            lon = -lon

        return round(lat, 6), round(lon, 6)

    except (KeyError, TypeError, ZeroDivisionError, AttributeError):
        # Malformed or partial GPS EXIF block - treat as "no location"
        # rather than crashing the upload flow.
        return None
