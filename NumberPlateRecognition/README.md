# Number Plate Recognition System

> **Academic Project** · Python · OpenCV · Tesseract OCR · Streamlit · SQLite

A complete, end-to-end **Number Plate Recognition (NPR)** system built with open-source Python libraries. Upload a vehicle image, let the pipeline detect and crop the plate region, extract text via OCR, and look up the registration in a local SQLite database — all through a professional Streamlit web interface.

---

## 📸 Features

| Feature | Description |
|---------|-------------|
| 🖼️ Image Upload | JPG, JPEG, PNG support with validation |
| 🔧 Image Preprocessing | Resize → Grayscale → Bilateral Filter → Adaptive Threshold → Canny Edges |
| 🔲 Plate Detection | Contour analysis + aspect-ratio filtering to locate plate region |
| 🔤 OCR Extraction | Tesseract OCR with PSM 7 (single text line), character whitelist |
| 🗃️ Database Lookup | SQLite vehicle records — registered/unregistered result |
| 📋 Scan History | Timestamped log of all recognition attempts |
| ✏️ Manual Override | Type plate text manually if OCR fails |
| 🎨 Professional UI | Dark navy / blue theme built with Streamlit |

---

## 🧰 Software Prerequisites

| Software | Version | Notes |
|----------|---------|-------|
| Python | 3.9 – 3.12 | [python.org](https://www.python.org/downloads/) |
| pip | Latest | Bundled with Python |
| **Tesseract OCR** | 5.x | **Must be installed separately** (see below) |

---

## 🪟 Tesseract OCR Installation (Windows)

Tesseract is **not** a Python package — it is a separate program that pytesseract calls.

### Step-by-Step

1. Go to: **https://github.com/UB-Mannheim/tesseract/wiki**
2. Download the latest Windows installer, e.g.:
   `tesseract-ocr-w64-setup-5.4.0.20240606.exe`
3. Run the installer. **Note the installation path** (usually `C:\Program Files\Tesseract-OCR`).
4. During installation, check **"Add to PATH"** if the option is available.
5. Verify the installation — open a new terminal and run:
   ```
   tesseract --version
   ```
   You should see something like `tesseract 5.4.0`.

### If Tesseract Is Not on PATH

Open `recognition.py` and add this near the top (after the imports), replacing the path if yours differs:

```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

---

## 🚀 Installation

```bash
# 1. Navigate to the project folder
cd NumberPlateRecognition

# 2. (Optional but recommended) Create a virtual environment
python -m venv venv
venv\Scripts\activate      # Windows

# 3. Install Python dependencies
pip install -r requirements.txt
```

---

## ▶️ Running the Application

```bash
streamlit run app.py
```

The app will open automatically in your browser at **http://localhost:8501**.

---

## 🗺️ How to Use

### Recognition Workflow
1. Open the app and navigate to **🔍 Number Plate Recognition**.
2. Click **Browse files** and upload a vehicle photo (JPG/PNG).
3. Click **🔍 Recognize Number Plate**.
4. View the preprocessing stages (grayscale, threshold, edges).
5. See the detected plate region highlighted in green.
6. The extracted registration number is displayed in yellow.
7. The system automatically checks the vehicle database and shows owner details or "Not Found".
8. Each scan is saved to **📋 Scan History**.

### Tips for Best OCR Results
- Use a front-facing vehicle photo with the plate clearly visible.
- Ensure good lighting — avoid glare and shadows on the plate.
- Plate should be horizontal, not at a steep angle.
- Higher resolution images generally produce better results.
- If OCR fails, use the **Manual Plate Text** input to enter the number manually.

### Pages
| Page | Description |
|------|-------------|
| 🏠 Dashboard | Summary cards, pipeline overview |
| 🔍 Recognition | Upload image, run full pipeline |
| 🗄️ Vehicle Database | Browse fictional demo vehicle records |
| 📋 Scan History | View and clear recognition log |
| ℹ️ About | Problem statement, objectives, workflow, tech, limitations |

---

## 📁 Project Structure

```
NumberPlateRecognition/
├── app.py              # Main Streamlit application (UI + page routing)
├── recognition.py      # Image processing & OCR pipeline
├── database.py         # SQLite database operations
├── requirements.txt    # Python package dependencies
├── README.md           # This file
├── assets/             # Static assets (logos, sample images)
└── data/
    └── vehicle_records.db   # Auto-created SQLite database
```

---

## ⚠️ Limitations

- OCR accuracy is highly dependent on **image quality, lighting, and plate condition**.
- The contour-based plate detector works best with **standard rectangular plates**.
- Only **static image** input is supported (no real-time video).
- The database contains **8 fictional demo records** for demonstration only.
- No perspective/angle correction — tilted plates may not be read correctly.

---

## 🔮 Future Scope

- Deep learning plate detector (YOLOv8)
- Real-time webcam/video stream support
- Perspective correction for angled plates
- Multi-country plate format support
- REST API for system integration
- Admin UI for managing vehicle records

---

## 📄 Disclaimer

> All vehicle records in this application are **entirely fictional** and created solely for academic
> demonstration. They do not represent real people, vehicles, or registration numbers.

---

*Number Plate Recognition System · Academic Project · Python 3 + OpenCV + Tesseract + Streamlit*
