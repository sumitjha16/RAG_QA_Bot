import base64
import logging
import requests
import streamlit as st
from fpdf import FPDF
import tempfile
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(page_title="💬 PDF QA", layout="wide")

# Custom CSS for improved layout
st.markdown("""
    <style>
    /* Set the overall layout width to reduce margins */
    .stApp {
        max-width: 94% !important;  /* Set the total width of the app to 94%, so 3% margin on both sides */
        margin-left: 3% !important;  /* Set left margin */
        margin-right: 3% !important; /* Set right margin */
    }

    /* Adjust sidebar width and appearance */
    .css-1lcbmhc {
        margin-left: 0px !important;  /* Remove left margin from the sidebar */
        width: 300px !important;  /* Sidebar width */
        background-color: grey !important; /* Set sidebar color to grey */
    }

    /* Adjust the sidebar's toggler arrow size */
    .css-1cpxqw2 {
        font-size: 30px !important;  /* Increase arrow size */
        padding: 10px !important;    /* Add some padding for better click area */
    }

    /* Sidebar buttons styling */
    .stButton>button {
        width: 100%;  /* Make sidebar buttons full width */
        background-color: #4e107d;  /* Button background color */
        color: white;  /* Button text color */
        border-radius: 8px;  /* Rounded corners */
        font-size: 16px;
        padding: 10px;
        border: none;
    }

    /* Button hover effect */
    .stButton>button:hover {
        background-color: #1b052b;
    }

    /* Download button styling */
    .stDownloadButton>button {
        width: 100%;  /* Full width for download buttons */
        background-color: #28a745;  /* Green background for download buttons */
        color: white;  /* White text */
        border-radius: 8px;
        padding: 10px;
        font-size: 16px;
        border: none;
    }

    /* Hover effect for download buttons */
    .stDownloadButton>button:hover {
        background-color: #218838;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'summary' not in st.session_state:
    st.session_state.summary = None
if 'reset_app' not in st.session_state:
    st.session_state.reset_app = False
if 'current_pdf' not in st.session_state:
    st.session_state.current_pdf = None

def reset_backend():
    try:
        # response = requests.post("http://127.0.0.1:8000/reset")
        # response.raise_for_status()
        logger.info("Backend reset successfully")
    except requests.RequestException as e:
        logger.error(f"Failed to reset backend: {str(e)}")
def generate_summary(pdf_file):
    with st.spinner("Generating summary..."):
        try:
            pdf_file.seek(0)  # Reset file pointer
            encoded_pdf = base64.b64encode(pdf_file.read()).decode("ascii")
            json_payload = {"pdf": encoded_pdf}
            response = requests.post("http://127.0.0.1:8000/summarize", json=json_payload, timeout=120)
            response.raise_for_status()
            summary = response.json().get("summary", "No summary returned.")
            st.session_state.summary = summary
            st.success("Summary generated successfully!")
        except requests.RequestException as e:
            st.error(f"Failed to get summary: {str(e)}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")


def export_conversation_as_pdf(conversation):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for chat in conversation:
            pdf.multi_cell(0, 10, txt=f"{chat['role'].capitalize()}: {chat['message']}")

        # Save PDF to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            pdf.output(temp_pdf.name)

        # Read the temporary file and return its contents
        with open(temp_pdf.name, "rb") as file:
            pdf_bytes = file.read()

        # Clean up the temporary file
        os.unlink(temp_pdf.name)

        return pdf_bytes
    except Exception as e:
        st.error(f"Failed to generate PDF: {str(e)}")
        return None


def reset_app():
    st.session_state.conversation = []
    st.session_state.summary = None
    st.session_state.reset_app = True
    st.session_state.current_pdf = None
    reset_backend()
    st.rerun()


# Check if we need to reset the app
if st.session_state.reset_app:
    st.session_state.reset_app = False
    st.success("New session started! Your conversation history has been cleared.")

# Sidebar
with st.sidebar:
    st.title("📁 Document Upload")
    uploaded_file = st.file_uploader(
        label="Upload a PDF file",
        type="pdf",
        accept_multiple_files=False,
        help="Choose a PDF file to analyze"
    )


    if uploaded_file:
        if uploaded_file != st.session_state.current_pdf:
            st.session_state.current_pdf = uploaded_file
            reset_backend()
            st.session_state.summary = None
            st.session_state.conversation = []

    if st.button("📊 Generate Summary"):
        if uploaded_file:
            generate_summary(uploaded_file)
        else:
            st.warning("Please upload a PDF file first.")

    if st.session_state.summary:
        summary_bytes = st.session_state.summary.encode()
        st.download_button(
            label="📥 Download Summary",
            data=summary_bytes,
            file_name="document_summary.txt",
            mime="text/plain"
        )

    if st.button("📤 Export Conversation"):
        if st.session_state.conversation:
            try:
                # Export as text file
                with open("conversation.txt", "w") as file:
                    for chat in st.session_state.conversation:
                        file.write(f"{chat['role'].capitalize()}: {chat['message']}\n\n")

                # Export as PDF
                pdf_bytes = export_conversation_as_pdf(st.session_state.conversation)
                if pdf_bytes:
                    st.download_button(
                        label="Download PDF",
                        data=pdf_bytes,
                        file_name="conversation.pdf",
                        mime="application/pdf"
                    )
                st.success("Conversation exported successfully!")
            except Exception as e:
                st.error(f"Failed to export conversation: {str(e)}")
        else:
            st.warning("No conversation to export.")

    if st.button("🔄 New Session"):
        reset_app()

# Main content
st.title("💬 PDF QA Assistant")

if uploaded_file:
    if st.session_state.summary:
        with st.expander("Document Summary", expanded=True):
            st.write(st.session_state.summary)
    else:
        st.info("📊 Click 'Generate Summary' in the sidebar to summarize the document.")

# Display conversation history
for chat in st.session_state.conversation:
    with st.chat_message(chat["role"]):
        st.write(chat["message"])

# Chat input
prompt = st.chat_input("Ask a question about your document")
if prompt:
    if uploaded_file is None:
        st.warning("Please upload a PDF file before asking questions.")
    else:
        st.session_state.conversation.append({"role": "user", "message": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    uploaded_file.seek(0)  # Reset file pointer
                    encoded_pdf = base64.b64encode(uploaded_file.read()).decode("ascii")
                    json_payload = {"question": prompt, "pdf": encoded_pdf}
                    response = requests.post("http://127.0.0.1:8000/ask", json=json_payload, timeout=120)
                    response.raise_for_status()
                    answer = response.json().get("answer", "No answer returned.")
                    st.session_state.conversation.append({"role": "assistant", "message": answer})
                    st.write(answer)
                except requests.RequestException as e:
                    st.error(f"Failed to get answer from the backend: {str(e)}")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {str(e)}")

# Display a message if no file is uploaded
if uploaded_file is None:
    st.info("👆 Upload a PDF file to get started!")