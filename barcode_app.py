import streamlit as st
import barcode
from barcode.writer import ImageWriter
import qrcode
from PIL import Image, ImageColor
import io

# Page Configuration
st.set_page_config(
    page_title="Universal Barcode Generator",
    page_icon="🏷️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to improve UI
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        margin-top: 10px;
    }
    .stAlert {
        padding-top: 10px;
        padding-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏷️ Universal Barcode & QR Generator")
st.markdown("Generate high-quality barcodes and QR codes for text, URLs, and product IDs.")

# --- Helper Functions ---

def generate_linear_barcode(data, barcode_type, options):
    """Generates a linear barcode (1D)"""
    try:
        # Get the barcode class
        barcode_class = barcode.get_barcode_class(barcode_type)
        
        # Create barcode object
        writer = ImageWriter()
        
        # Configure writer options (colors need to be hex or valid names)
        # python-barcode ImageWriter expects colors specifically
        
        my_barcode = barcode_class(data, writer=writer)
        
        # Render
        buffer = io.BytesIO()
        my_barcode.write(buffer, options=options)
        buffer.seek(0)
        return buffer, None
    except Exception as e:
        return None, str(e)

def generate_qr_code(data, options):
    """Generates a QR code (2D)"""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=options['error_correction'],
            box_size=options['box_size'],
            border=options['border'],
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color=options['fill_color'], back_color=options['back_color'])
        
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer, None
    except Exception as e:
        return None, str(e)

# --- Sidebar Controls ---
st.sidebar.header("🛠️ Configuration")

# Mode Selection
mode = st.sidebar.radio("Generator Mode", ["Linear Barcode (1D)", "QR Code (2D)"])

# --- Main Logic ---

if mode == "Linear Barcode (1D)":
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Settings")
        
        # Input Data
        raw_data = st.text_area("Enter Content", "123456789", height=100, 
                               help="Enter text, numbers, or link.")
        
        # Barcode Type Selection
        # Common useful types. Code128 is best for text/mixed. EAN/UPC for products.
        barcode_types = [
            "code128", "code39", "ean13", "ean8", "upca", "isbn13", "itf"
        ]
        b_type = st.selectbox("Barcode Type", barcode_types, index=0)
        
        # Customization Expanders
        with st.expander("🎨 Appearance", expanded=False):
            bar_color = st.color_picker("Bar Color", "#000000")
            bg_color = st.color_picker("Background Color", "#FFFFFF")
            write_text = st.checkbox("Show Text Below Code", value=True)
            
        with st.expander("📏 Dimensions", expanded=False):
            module_width = st.slider("Bar Width (mm)", 0.1, 1.0, 0.2, 0.1)
            module_height = st.slider("Bar Height (mm)", 5.0, 30.0, 15.0, 1.0)
            font_size = st.slider("Font Size", 5, 20, 10)
            quiet_zone = st.slider("Quiet Zone", 1.0, 10.0, 6.5)

    with col2:
        st.subheader("Preview")
        
        if raw_data:
            # Prepare options for python-barcode
            options = {
                'module_width': module_width,
                'module_height': module_height,
                'font_size': font_size,
                'text_distance': 5.0,
                'quiet_zone': quiet_zone,
                'write_text': write_text,
                'foreground': bar_color,
                'background': bg_color,
            }

            image_buffer, error = generate_linear_barcode(raw_data, b_type, options)

            if error:
                st.error(f"Error generating barcode: {error}")
                st.info("Tip: EAN-13 requires exactly 12 or 13 digits. UPC-A requires 11 or 12 digits. For text/mixed data, use 'code128'.")
            else:
                st.image(image_buffer, caption=f"Type: {b_type} | Data: {raw_data}", use_column_width=False)
                
                # Download Button
                st.download_button(
                    label="💾 Download Barcode",
                    data=image_buffer,
                    file_name=f"barcode_{b_type}_{raw_data[:10]}.png",
                    mime="image/png"
                )
        else:
            st.warning("Please enter some data to generate a barcode.")

elif mode == "QR Code (2D)":
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Settings")
        
        # Input Data
        raw_data = st.text_area("Enter Content (URL, Text, etc.)", "https://www.streamlit.io", height=100)
        
        with st.expander("🎨 Appearance", expanded=False):
            fill_color = st.color_picker("Fill Color", "#000000")
            back_color = st.color_picker("Background Color", "#FFFFFF")
        
        with st.expander("🔧 Technical", expanded=False):
            box_size = st.slider("Box Size (Resolution)", 1, 20, 10)
            border = st.slider("Border Size", 0, 10, 4)
            
            # Error Correction Mapping
            ec_options = {
                "Low (7%)": qrcode.constants.ERROR_CORRECT_L,
                "Medium (15%)": qrcode.constants.ERROR_CORRECT_M,
                "Quartile (25%)": qrcode.constants.ERROR_CORRECT_Q,
                "High (30%)": qrcode.constants.ERROR_CORRECT_H,
            }
            ec_label = st.selectbox("Error Correction", list(ec_options.keys()), index=1)
            error_correction = ec_options[ec_label]

    with col2:
        st.subheader("Preview")
        
        if raw_data:
            options = {
                'fill_color': fill_color,
                'back_color': back_color,
                'box_size': box_size,
                'border': border,
                'error_correction': error_correction
            }
            
            image_buffer, error = generate_qr_code(raw_data, options)
            
            if error:
                st.error(f"Error generating QR Code: {error}")
            else:
                st.image(image_buffer, caption="Generated QR Code", use_column_width=False)
                
                # Download Button
                st.download_button(
                    label="💾 Download QR Code",
                    data=image_buffer,
                    file_name="qrcode.png",
                    mime="image/png"
                )
        else:
            st.warning("Please enter text or a URL to generate a QR code.")

# --- Footer ---
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit, Python-Barcode, and Qrcode.")