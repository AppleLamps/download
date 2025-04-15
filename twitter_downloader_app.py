import streamlit as st
import subprocess
import os
from pathlib import Path
import shutil
import base64  # For encoding file data in download buttons

# Create a folder for downloads
DOWNLOAD_FOLDER = Path("downloads")
DOWNLOAD_FOLDER.mkdir(exist_ok=True)

st.set_page_config(page_title="Twitter Video Downloader", layout="centered")
st.title("Twitter Video Downloader")

# Inform the user about limitations, file handling, and potential deployment issues
st.markdown("This downloader works for public Twitter videos only. Files are saved temporarily on the server, and you can download them to your device using the buttons below.")
st.markdown("Note: In deployed environments, additional dependencies like ffmpeg may be required for yt-dlp to work properly.")
st.markdown("Paste one or more Twitter video URLs (one per line):")
tweet_input = st.text_area("Tweet URLs", height=200, placeholder="https://twitter.com/username/status/123...\nhttps://twitter.com/...")

# Use session state to store downloaded file paths
if "downloaded_files" not in st.session_state:
    st.session_state.downloaded_files = []

if st.button("Download"):
    tweet_urls = [url.strip() for url in tweet_input.splitlines() if url.strip()]
    
    if not tweet_urls:
        st.warning("Please enter at least one valid Twitter video URL.")
    else:
        # Check if yt-dlp is installed
        if shutil.which("yt-dlp") is None:
            st.error("yt-dlp is not found. Please ensure it is installed (e.g., via pip install yt-dlp).")
            st.stop()
        
        # Check if ffmpeg is installed, as yt-dlp often requires it
        if shutil.which("ffmpeg") is None:
            st.error("ffmpeg is not found. yt-dlp may fail without it. Install ffmpeg on your system or ensure it's available in the deployment environment.")
            st.stop()  # Halt if ffmpeg is missing, as downloads will likely fail
        
        st.success(f"Starting download for {len(tweet_urls)} video(s)...")
        successful_downloads = []  # Temp list for this run
        for i, url in enumerate(tweet_urls, 1):
            output_file = DOWNLOAD_FOLDER / f"twitter_video_{i}.mp4"
            with st.spinner(f"Downloading video {i}..."):
                try:
                    result = subprocess.run(
                        ["yt-dlp", "-f", "best", "-o", str(output_file), url],
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    
                    if result.returncode == 0:
                        st.info(f"Successfully downloaded: {output_file.name}")
                        successful_downloads.append(str(output_file))  # Store path for download buttons
                    else:
                        error_msg = result.stderr.strip()
                        st.error(f"Failed to download from {url}: {error_msg}")
                
                except Exception as e:
                    st.error(f"An error occurred while downloading from {url}: {str(e)}")
        
        # Add successful downloads to session state to persist across reruns
        st.session_state.downloaded_files.extend(successful_downloads)

# Display download buttons for all downloaded files in session state
if st.session_state.downloaded_files:
    st.header("Downloaded Files")
    for file_path in st.session_state.downloaded_files:
        file_name = Path(file_path).name
        with open(file_path, "rb") as file:
            btn = st.download_button(
                label=f"Download {file_name}",
                data=file,
                file_name=file_name,
                mime="video/mp4"
            )
else:
    if "download_triggered" in st.session_state and not st.session_state.downloaded_files:
        st.info("No files were successfully downloaded.")
    st.session_state["download_triggered"] = True  # Track if download was attempted

# Note: Files are stored in the 'downloads' folder on the server or local machine.
# In Streamlit Cloud, these files are temporary and may be cleaned up periodically.
