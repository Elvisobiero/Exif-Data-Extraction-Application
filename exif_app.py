import streamlit as st
from PIL import Image, ExifTags
import pandas as pd

st.set_page_config(page_title="📸 Image EXIF & GPS Viewer", page_icon="📷", layout="wide")

st.title("📸 Image EXIF Metadata & GPS Viewer")

def get_decimal_from_dms(dms, ref):
    """Convert GPS coordinates stored in EXIF to decimal degrees."""
    degrees = dms[0][0] / dms[0][1]
    minutes = dms[1][0] / dms[1][1]
    seconds = dms[2][0] / dms[2][1]
    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
    if ref in ['S', 'W']:
        decimal = -decimal
    return decimal

def extract_gps_info(exif_data):
    """Extract latitude and longitude from EXIF data if available."""
    gps_info = exif_data.get('GPSInfo')
    if not gps_info:
        return None, None

    gps_tags = {}
    for key in gps_info.keys():
        decoded_tag = ExifTags.GPSTAGS.get(key, key)
        gps_tags[decoded_tag] = gps_info[key]

    try:
        lat = get_decimal_from_dms(gps_tags['GPSLatitude'], gps_tags['GPSLatitudeRef'])
        lon = get_decimal_from_dms(gps_tags['GPSLongitude'], gps_tags['GPSLongitudeRef'])
        return lat, lon
    except KeyError:
        return None, None

# Upload image
uploaded_file = st.file_uploader("Upload an image (JPEG, JPG, PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="🖼️ Uploaded Image", use_column_width=True)

    # Extract EXIF data
    exif_data_raw = image._getexif()

    if exif_data_raw:
        exif_data = {
            ExifTags.TAGS.get(tag, tag): value
            for tag, value in exif_data_raw.items()
            if tag in ExifTags.TAGS
        }

        # Display EXIF table
        df = pd.DataFrame(list(exif_data.items()), columns=["Tag", "Value"])
        st.subheader("📄 EXIF Metadata")
        st.dataframe(df, use_container_width=True)

        # GPS extraction
        lat, lon = extract_gps_info(exif_data)
        if lat and lon:
            st.success(f"📍 GPS Coordinates found: {lat:.6f}, {lon:.6f}")

            # Show map
            st.subheader("🗺️ Image Location on Map")
            st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))
        else:
            st.info("No GPS location data found in this image.")

        # Download option
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "⬇️ Download Metadata as CSV",
            csv,
            "exif_metadata.csv",
            "text/csv"
        )
    else:
        st.warning("⚠️ No EXIF metadata found in this image.")
else:
    st.info("Please upload an image file to extract EXIF and GPS metadata.")

