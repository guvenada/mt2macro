# mt2macro (Open Source Automation)

![Status](https://img.shields.io/badge/Status-Stable-brightgreen)
![License](https://img.shields.io/badge/License-MIT-blue)
![Purpose](https://img.shields.io/badge/Purpose-Research%20Only-orange)

An open-source, thread-safe desktop automation tool powered by computer vision. This project demonstrates how to build robust automation software using Python, OpenCV, and WinAPI.

## ⚠️ Important Disclaimer

This software is for **EDUCATIONAL PURPOSES ONLY**. It is a generic tool designed to showcase:
- Multithreaded GUI applications with `customtkinter`.
- Real-time Screen Capture with `mss`.
- Template Matching algorithms with `opencv`.

**By using this software, you agree that:**
1. You will use it only for personal research or offline testing.
2. You will not use it to violate the Terms of Service of any third-party software.
3. The authors assume no liability for misuse.

See `EDUCATIONAL_CERTIFICATE.md` for full details.

## Features

- **Stealth Design**: Randomizes window titles to mimic system processes.
- **Modern GUI**: Professional dark-themed interface.
- **Performance**: Optimized for minimal CPU usage (~1-2% on idle).
- **Flexibility**: Works with any desktop application via image templates.
- **Safety**: Includes timeouts and stuck detection logic.

## Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/guvenada/mt2macro.git
    cd mt2macro
    ```

2.  **Install Requirements**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Launch the Tool**
    ```bash
    python external_gui.py
    ```

2.  **Setup Targets**
    - Click **Capture Main** to select your primary interaction target.
    - Click **Capture Sub** to select secondary targets (e.g., confirmation buttons, rare events).
    - *Note: Images are saved locally as `target.png` and `elite1.png` etc.*

3.  **Configure**
    - Go to the **Properties** tab.
    - Adjust **Threshold** (sensitivity, usually 0.55 - 0.75).
    - Set **Action Delay** (speed of interaction).

4.  **Start Service**
    - Click **START SERVICE**. The bot will run in the background.
    - **F12** to Pause/Resume.
    - **ESC** to Emergency Exit.

## Project Structure

- `external_gui.py`: Main application entry point (GUI).
- `external_bot.py`: CLI version (for headless operation).
- `requirements.txt`: Python package list.
- `LICENSE`: MIT License.
- `EDUCATIONAL_CERTIFICATE.md`: Certificate of Use.

## License

Distributed under the MIT License. See `LICENSE` for more information.
