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
from PIL.ExifTags import GPSTAGS, IFD


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

        # BUG (fixed): exif.items() at the top level only yields a raw
        # integer byte-offset for the GPSInfo tag (0x8825/34853), not
        # the actual GPS sub-IFD dict — Pillow stores GPS data in a
        # separate IFD that has to be fetched explicitly via
        # get_ifd(). The old code iterated exif.items() looking for a
        # dict value under "GPSInfo" and never found one, so every
        # real photo with GPS data silently returned None.
        try:
            raw_gps_ifd = exif.get_ifd(IFD.GPSInfo)
        except (KeyError, AttributeError):
            raw_gps_ifd = {}

        if not raw_gps_ifd:
            return None

        gps_info = {
            GPSTAGS.get(tag_id, tag_id): value
            for tag_id, value in raw_gps_ifd.items()
        }

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
