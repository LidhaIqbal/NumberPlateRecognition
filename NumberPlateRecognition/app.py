"""
app.py - Main Streamlit application for Number Plate Recognition System
Run with: streamlit run app.py
"""

import streamlit as st
import os
from PIL import Image
import io
import sys

# ── Page config (must be the very first Streamlit call) ───────────────────────
st.set_page_config(
    page_title="Number Plate Recognition System",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Local module imports ───────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

import database as db
import recognition as rec

# ── Initialize DB ──────────────────────────────────────────────────────────────
db.initialize_database()

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global / Background ── */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0a1628 0%, #0d2040 50%, #0a1628 100%);
    min-height: 100vh;
}
[data-testid="stHeader"] { background: transparent; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1f3c 0%, #112244 100%);
    border-right: 1px solid #1e3a5f;
}
[data-testid="stSidebar"] .stRadio label {
    color: #a8c4e0 !important;
    font-size: 0.95rem;
}
[data-testid="stSidebarContent"] h1,
[data-testid="stSidebarContent"] h2,
[data-testid="stSidebarContent"] h3 { color: #60a5fa !important; }

/* ── Cards ── */
.metric-card {
    background: linear-gradient(135deg, #112244, #1a3260);
    border: 1px solid #2563eb44;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    margin: 6px 0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    transition: transform 0.2s;
}
.metric-card:hover { transform: translateY(-2px); }
.metric-card .value  { font-size: 2.4rem; font-weight: 700; color: #60a5fa; }
.metric-card .label  { font-size: 0.85rem; color: #94a3b8; margin-top: 4px; letter-spacing: 0.05em; text-transform: uppercase; }

/* ── Section headings ── */
h1, h2, h3 { color: #e2e8f0 !important; }
h1 { font-size: 2rem !important; }
p, li { color: #cbd5e1; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 24px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    width: 100% !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
    box-shadow: 0 4px 15px rgba(37,99,235,0.4) !important;
    transform: translateY(-1px) !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: #112244 !important;
    border: 2px dashed #2563eb55 !important;
    border-radius: 12px !important;
    padding: 10px !important;
}

/* ── Result boxes ── */
.result-box {
    border-radius: 10px;
    padding: 18px 22px;
    margin: 12px 0;
    font-size: 1rem;
}
.result-match   { background: #052e16; border-left: 4px solid #22c55e; }
.result-nomatch { background: #1c0a00; border-left: 4px solid #f97316; }
.result-error   { background: #1a0000; border-left: 4px solid #ef4444; }
.result-info    { background: #0c1a30; border-left: 4px solid #3b82f6; }
.result-warn    { background: #1a1000; border-left: 4px solid #eab308; }

/* ── Plate display ── */
.plate-text {
    font-family: 'Courier New', monospace;
    font-size: 2rem;
    font-weight: 800;
    color: #facc15;
    background: #1e1b00;
    border: 3px solid #ca8a04;
    border-radius: 8px;
    padding: 12px 28px;
    display: inline-block;
    letter-spacing: 0.18em;
}

/* ── Tables ── */
.stDataFrame { background: #0d1f3c !important; }
[data-testid="stTable"] th { background: #1e3a5f !important; color: #93c5fd !important; }

/* ── Divider ── */
hr { border-color: #1e3a5f !important; }

/* ── Status badge ── */
.badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.05em;
}
.badge-active    { background: #052e16; color: #4ade80; border: 1px solid #166534; }
.badge-expired   { background: #1c0a00; color: #f97316; border: 1px solid #9a3412; }
.badge-suspended { background: #1a0000; color: #f87171; border: 1px solid #991b1b; }

/* ── Expander ── */
details summary { color: #93c5fd !important; }

/* ── Progress / spinner ── */
.stSpinner > div { border-top-color: #3b82f6 !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR NAVIGATION
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 10px 0 20px;'>
        <div style='font-size:2.5rem;'>🚗</div>
        <div style='color:#60a5fa; font-size:1rem; font-weight:700; line-height:1.3;'>
            Number Plate<br>Recognition System
        </div>
        <div style='color:#475569; font-size:0.75rem; margin-top:4px;'>
            Academic Project v1.0
        </div>
    </div>
    <hr style='margin:0 0 16px;'>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["🏠  Dashboard",
         "🔍  Number Plate Recognition",
         "🗄️  Vehicle Database",
         "📋  Scan History",
         "ℹ️  About the Project"],
        label_visibility="collapsed",
    )

    st.markdown("<hr>", unsafe_allow_html=True)

    # Tesseract status indicator
    if rec.TESSERACT_AVAILABLE:
        st.markdown("""
        <div style='font-size:0.8rem; color:#4ade80; padding:8px 12px;
                    background:#052e16; border-radius:8px; text-align:center;'>
            ✅ Tesseract OCR Ready
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='font-size:0.8rem; color:#f97316; padding:8px 12px;
                    background:#1c0a00; border-radius:8px; text-align:center;'>
            ⚠️ Tesseract Not Found
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style='margin-top:20px; font-size:0.72rem; color:#475569; text-align:center;'>
        ⚠️ All vehicle data is<br>fictional demo data only.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

if page == "🏠  Dashboard":
    # Hero header
    st.markdown("""
    <div style='text-align:center; padding: 30px 0 10px;'>
        <h1 style='font-size:2.4rem; color:#e2e8f0; margin:0;'>
            🚗 Number Plate Recognition System
        </h1>
        <p style='color:#94a3b8; font-size:1.05rem; margin-top:10px;'>
            Automated vehicle identification using Image Processing &amp; Optical Character Recognition (OCR)
        </p>
        <p style='color:#475569; font-size:0.85rem;'>
            Academic Project · Python · OpenCV · Pytesseract · Streamlit · SQLite
        </p>
    </div>
    <hr>
    """, unsafe_allow_html=True)

    # Summary statistics
    stats = db.get_summary_stats()
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='value'>{stats['total_scans']}</div>
            <div class='label'>📸 Total Scans</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='value'>{stats['registered']}</div>
            <div class='label'>✅ Registered Matches</div>
        </div>""", unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='value'>{stats['unregistered']}</div>
            <div class='label'>❌ Unregistered</div>
        </div>""", unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='value'>{stats['total_vehicles']}</div>
            <div class='label'>🗄️ Demo Vehicles in DB</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Feature overview
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        <div style='background:#0d1f3c; border:1px solid #1e3a5f; border-radius:12px; padding:20px;'>
            <h3 style='color:#60a5fa; margin-top:0;'>⚙️ System Capabilities</h3>
            <ul style='color:#94a3b8; line-height:2;'>
                <li>📷 Upload JPG / JPEG / PNG vehicle images</li>
                <li>🖼️ Multi-stage image preprocessing pipeline</li>
                <li>🔲 Automatic number plate region detection</li>
                <li>🔤 OCR-based text extraction via Tesseract</li>
                <li>🗃️ SQLite vehicle database lookup</li>
                <li>📊 Scan history with timestamps</li>
            </ul>
        </div>""", unsafe_allow_html=True)

    with col_b:
        st.markdown("""
        <div style='background:#0d1f3c; border:1px solid #1e3a5f; border-radius:12px; padding:20px;'>
            <h3 style='color:#60a5fa; margin-top:0;'>🛤️ Recognition Pipeline</h3>
            <div style='color:#94a3b8; line-height:2.2; font-size:0.9rem;'>
                📤 Image Upload<br>
                &nbsp;&nbsp;↓<br>
                🔧 Preprocessing (Grayscale → Blur → Threshold)<br>
                &nbsp;&nbsp;↓<br>
                🔲 Plate Region Detection (Contours)<br>
                &nbsp;&nbsp;↓<br>
                ✂️ Plate Crop + OCR Enhancement<br>
                &nbsp;&nbsp;↓<br>
                🔤 Tesseract OCR Extraction<br>
                &nbsp;&nbsp;↓<br>
                🔍 Database Lookup &amp; Result Display
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class='result-warn'>
        <b>⚠️ Accuracy Notice:</b> OCR accuracy depends on image quality, lighting, angle, plate condition,
        and font style. Results should always be verified by a human operator.
        All vehicle records in this demo are entirely fictional.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: NUMBER PLATE RECOGNITION
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "🔍  Number Plate Recognition":
    st.markdown("## 🔍 Number Plate Recognition")
    st.markdown("<p style='color:#94a3b8;'>Upload a vehicle image to extract and identify the registration number.</p>",
                unsafe_allow_html=True)

    # Tesseract check
    if not rec.TESSERACT_AVAILABLE:
        st.markdown(f"""
        <div class='result-error'>
            <b>⚠️ Tesseract OCR Not Available</b><br><br>
            {rec.TESSERACT_ERROR_MSG.replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        st.info("💡 You can still explore the **Vehicle Database** and **Scan History** pages while Tesseract is being installed.")

    st.markdown("---")

    # ── Upload section ─────────────────────────────────────────────────────
    col_upload, col_tip = st.columns([2, 1])
    with col_upload:
        st.markdown("#### 📤 Upload Vehicle Image")
        uploaded_file = st.file_uploader(
            "Choose a vehicle image",
            type=["jpg", "jpeg", "png"],
            help="Upload a clear, front-facing photo of a vehicle with a visible number plate.",
            label_visibility="collapsed",
        )

    with col_tip:
        st.markdown("""
        <div style='background:#0d1f3c; border:1px solid #1e3a5f; border-radius:10px; padding:16px; margin-top:28px;'>
            <b style='color:#60a5fa;'>📸 Tips for Best Results</b>
            <ul style='color:#94a3b8; font-size:0.82rem; margin-top:8px; line-height:1.8;'>
                <li>Front-facing vehicle photo</li>
                <li>Plate clearly visible & in focus</li>
                <li>Good lighting, no glare</li>
                <li>Minimal angle / skew</li>
                <li>Resolution: at least 640×480</li>
            </ul>
        </div>""", unsafe_allow_html=True)

    # Manual plate text override
    st.markdown("#### ✏️ Manual Plate Text (Optional Override)")
    manual_plate = st.text_input(
        "If OCR fails or produces incorrect text, type the plate number here:",
        placeholder="e.g.  MH12AB1234",
        label_visibility="collapsed",
    )

    st.markdown("---")

    if uploaded_file is not None:
        # Validate file
        try:
            pil_img = Image.open(io.BytesIO(uploaded_file.read()))
            pil_img.verify()
            uploaded_file.seek(0)
            pil_img = Image.open(io.BytesIO(uploaded_file.read())).convert("RGB")
        except Exception as e:
            st.markdown(f"""
            <div class='result-error'>
                <b>❌ Invalid Image File</b><br>
                Could not open this file as an image. Please upload a valid JPG or PNG.<br>
                <small>Error: {e}</small>
            </div>""", unsafe_allow_html=True)
            st.stop()

        # Show original
        col_orig, col_proc = st.columns(2)
        with col_orig:
            st.markdown("#### 🖼️ Original Image")
            st.image(pil_img, use_container_width=True)
            st.caption(f"Size: {pil_img.width}×{pil_img.height} px | Mode: {pil_img.mode}")

        # Recognition button
        btn_col, _ = st.columns([1, 2])
        with btn_col:
            run_recognition = st.button("🔍  Recognize Number Plate", type="primary")

        if run_recognition:
            with st.spinner("⚙️ Processing image through recognition pipeline…"):
                pipeline_result = rec.full_pipeline(pil_img)

            # ── Preprocessing stages ───────────────────────────────────────
            with col_proc:
                st.markdown("#### 🔧 Preprocessing Stages")
                stages = pipeline_result.get("stages", {})
                if stages:
                    stage_tabs = st.tabs(["Grayscale", "Denoised", "Threshold", "Edges"])
                    stage_keys = ["grayscale", "denoised", "threshold", "edges"]
                    for tab, key in zip(stage_tabs, stage_keys):
                        with tab:
                            if key in stages:
                                st.image(stages[key], use_container_width=True)

            st.markdown("---")

            # ── Detection result ───────────────────────────────────────────
            st.markdown("#### 🔲 Plate Detection")
            det_col1, det_col2 = st.columns(2)

            with det_col1:
                if pipeline_result["annotated_image"]:
                    st.image(pipeline_result["annotated_image"],
                             caption="📍 Detected Region (green box)",
                             use_container_width=True)

            with det_col2:
                if pipeline_result["plate_detected"]:
                    st.markdown(f"""
                    <div class='result-info'>
                        <b>✅ Plate Region Detected</b><br>
                        <small style='color:#94a3b8;'>{pipeline_result['detection_note']}</small>
                    </div>""", unsafe_allow_html=True)
                    if pipeline_result["plate_image"]:
                        st.image(pipeline_result["plate_image"],
                                 caption="✂️ Cropped Plate Region",
                                 use_container_width=True)
                else:
                    st.markdown(f"""
                    <div class='result-warn'>
                        <b>⚠️ Auto-detection Not Confident</b><br>
                        {pipeline_result['detection_note']}<br><br>
                        <small>OCR will be attempted on the full image.
                        For better results, manually crop the plate region
                        and upload the cropped image directly.</small>
                    </div>""", unsafe_allow_html=True)

            st.markdown("---")

            # ── OCR result ────────────────────────────────────────────────
            st.markdown("#### 🔤 OCR Extraction")

            # Use manual override if provided
            if manual_plate.strip():
                final_text = manual_plate.strip().upper()
                ocr_source = "manual input"
                ocr_ok = True
            else:
                final_text = pipeline_result.get("ocr_cleaned", "")
                ocr_source = "Tesseract OCR"
                ocr_ok = pipeline_result.get("ocr_success", False)

            if not rec.TESSERACT_AVAILABLE and not manual_plate.strip():
                st.markdown("""
                <div class='result-error'>
                    <b>❌ OCR Skipped – Tesseract Not Installed</b><br>
                    Install Tesseract and restart, or type the plate number manually above.
                </div>""", unsafe_allow_html=True)

            elif ocr_ok and final_text:
                st.markdown(f"""
                <div style='text-align:center; margin:20px 0;'>
                    <div style='color:#94a3b8; font-size:0.85rem; margin-bottom:10px;'>
                        Extracted via {ocr_source}
                    </div>
                    <span class='plate-text'>{final_text}</span>
                </div>""", unsafe_allow_html=True)

                if pipeline_result.get("ocr_raw") and ocr_source == "Tesseract OCR":
                    with st.expander("🔬 Raw OCR Output (debug)"):
                        st.code(pipeline_result.get("ocr_raw", ""), language=None)

            else:
                err_msg = pipeline_result.get("ocr_error") or "No text could be extracted."
                st.markdown(f"""
                <div class='result-error'>
                    <b>❌ OCR Extraction Failed</b><br>
                    {err_msg}
                </div>""", unsafe_allow_html=True)

                if pipeline_result.get("ocr_raw"):
                    with st.expander("🔬 Raw OCR Output (debug)"):
                        st.code(pipeline_result.get("ocr_raw", ""), language=None)

            st.markdown("---")

            # ── Database lookup ────────────────────────────────────────────
            st.markdown("#### 🗄️ Database Lookup")

            if final_text:
                vehicle = db.lookup_vehicle(final_text)
                normalized = db.normalize_plate(final_text)

                if vehicle:
                    status = vehicle["registration_status"]
                    badge_cls = {
                        "Active": "badge-active",
                        "Expired": "badge-expired",
                        "Suspended": "badge-suspended"
                    }.get(status, "badge-active")

                    st.markdown(f"""
                    <div class='result-match'>
                        <b>✅ Registered Vehicle Found</b>
                        &nbsp;<span class='badge {badge_cls}'>{status}</span><br>
                        <small style='color:#6ee7b7;'>{vehicle.get('note','')}</small>
                    </div>""", unsafe_allow_html=True)

                    v1, v2 = st.columns(2)
                    with v1:
                        st.markdown(f"""
                        <div style='background:#0a1628; border:1px solid #1e3a5f; border-radius:10px; padding:16px; margin-top:10px;'>
                            <table style='width:100%; color:#cbd5e1; font-size:0.9rem; border-collapse:collapse;'>
                                <tr><td style='padding:6px 0; color:#94a3b8; width:40%;'>Registration</td>
                                    <td style='color:#facc15; font-family:monospace; font-weight:700;'>{vehicle['registration_no']}</td></tr>
                                <tr><td style='padding:6px 0; color:#94a3b8;'>Owner</td>
                                    <td>{vehicle['owner_name']}</td></tr>
                                <tr><td style='padding:6px 0; color:#94a3b8;'>Vehicle Type</td>
                                    <td>{vehicle['vehicle_type']}</td></tr>
                                <tr><td style='padding:6px 0; color:#94a3b8;'>Model</td>
                                    <td>{vehicle['vehicle_model']}</td></tr>
                                <tr><td style='padding:6px 0; color:#94a3b8;'>Status</td>
                                    <td><span class='badge {badge_cls}'>{status}</span></td></tr>
                            </table>
                        </div>""", unsafe_allow_html=True)

                    # Save scan
                    db.save_scan(
                        raw_ocr=pipeline_result.get("ocr_raw", final_text),
                        normalized=normalized,
                        matched=True,
                        owner_name=vehicle["owner_name"],
                        vehicle_type=vehicle["vehicle_type"],
                        vehicle_model=vehicle["vehicle_model"],
                    )

                else:
                    st.markdown(f"""
                    <div class='result-nomatch'>
                        <b>❌ Vehicle Not Found in Database</b><br>
                        No record matches plate: <code style='color:#facc15;'>{normalized}</code><br>
                        <small style='color:#94a3b8;'>This vehicle is not in the demo database,
                        or the OCR result may be inaccurate. Verify visually.</small>
                    </div>""", unsafe_allow_html=True)

                    # Save scan
                    db.save_scan(
                        raw_ocr=pipeline_result.get("ocr_raw", final_text),
                        normalized=normalized,
                        matched=False,
                    )

            else:
                st.markdown("""
                <div class='result-info'>
                    <b>ℹ️ No text to look up.</b><br>
                    OCR did not produce a result. Use the manual input above to enter the plate text.
                </div>""", unsafe_allow_html=True)

    else:
        # No image uploaded yet
        st.markdown("""
        <div style='text-align:center; padding:50px 20px; color:#475569;'>
            <div style='font-size:4rem;'>📷</div>
            <p style='font-size:1.1rem; margin-top:12px;'>Upload a vehicle image to begin recognition</p>
            <p style='font-size:0.85rem;'>Supported formats: JPG, JPEG, PNG</p>
        </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: VEHICLE DATABASE
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "🗄️  Vehicle Database":
    st.markdown("## 🗄️ Vehicle Database")
    st.markdown("""
    <div class='result-warn'>
        ⚠️ <b>All records below are entirely fictional demo data</b> for academic demonstration purposes only.
        They do not represent real people or vehicles.
    </div><br>
    """, unsafe_allow_html=True)

    vehicles = db.get_all_vehicles()

    if vehicles:
        # Quick search
        search = st.text_input("🔍 Search by registration, owner, or model:", placeholder="e.g. MH12 or Kumar")

        filtered = vehicles
        if search.strip():
            q = search.strip().lower()
            filtered = [
                v for v in vehicles
                if q in v["registration_no"].lower()
                or q in v["owner_name"].lower()
                or q in v["vehicle_model"].lower()
                or q in v["vehicle_type"].lower()
            ]

        st.markdown(f"<p style='color:#94a3b8;'>Showing <b>{len(filtered)}</b> of {len(vehicles)} records</p>",
                    unsafe_allow_html=True)

        for v in filtered:
            status = v["registration_status"]
            badge_cls = {
                "Active": "badge-active",
                "Expired": "badge-expired",
                "Suspended": "badge-suspended"
            }.get(status, "badge-active")

            st.markdown(f"""
            <div style='background:#0d1f3c; border:1px solid #1e3a5f; border-radius:10px;
                        padding:14px 20px; margin:8px 0; display:flex; justify-content:space-between; align-items:center;'>
                <div>
                    <span style='font-family:monospace; font-size:1.1rem; color:#facc15; font-weight:700;'>
                        {v['registration_no']}
                    </span>
                    &nbsp;&nbsp;
                    <span class='badge {badge_cls}'>{status}</span>
                </div>
                <div style='color:#cbd5e1; font-size:0.9rem;'>
                    👤 {v['owner_name']}&nbsp;&nbsp;|&nbsp;&nbsp;
                    🚗 {v['vehicle_type']}&nbsp;&nbsp;|&nbsp;&nbsp;
                    🔧 {v['vehicle_model']}
                </div>
                <div style='color:#475569; font-size:0.75rem;'>{v.get('note','')}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No vehicles in the database.")


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: SCAN HISTORY
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "📋  Scan History":
    st.markdown("## 📋 Scan History")
    st.markdown("<p style='color:#94a3b8;'>Record of all recognition attempts made in this session.</p>",
                unsafe_allow_html=True)

    history = db.get_scan_history()

    col_stat, col_btn = st.columns([3, 1])
    with col_stat:
        st.markdown(f"<p style='color:#94a3b8;'>Total entries: <b>{len(history)}</b></p>",
                    unsafe_allow_html=True)

    with col_btn:
        if st.button("🗑️  Clear All History"):
            st.session_state["confirm_clear"] = True

    if st.session_state.get("confirm_clear"):
        st.warning("⚠️ Are you sure you want to delete all scan history?")
        c1, c2, _ = st.columns([1, 1, 3])
        with c1:
            if st.button("✅ Yes, Delete"):
                db.clear_scan_history()
                st.success("Scan history cleared.")
                st.session_state["confirm_clear"] = False
                st.rerun()
        with c2:
            if st.button("❌ Cancel"):
                st.session_state["confirm_clear"] = False
                st.rerun()

    if history:
        st.markdown("---")
        for entry in history:
            matched_badge = (
                "<span class='badge badge-active'>✅ Matched</span>"
                if entry["matched"]
                else "<span class='badge badge-expired'>❌ No Match</span>"
            )
            owner_info = ""
            if entry["matched"] and entry["owner_name"]:
                owner_info = f"&nbsp;&nbsp;|&nbsp;&nbsp;👤 {entry['owner_name']} · {entry['vehicle_model']}"

            st.markdown(f"""
            <div style='background:#0d1f3c; border:1px solid #1e3a5f; border-radius:10px;
                        padding:12px 18px; margin:6px 0;'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <div>
                        <span style='font-family:monospace; color:#facc15; font-size:1rem; font-weight:700;'>
                            {entry['normalized'] or entry['raw_ocr'] or '(empty)'}
                        </span>
                        &nbsp;&nbsp;{matched_badge}{owner_info}
                    </div>
                    <div style='color:#475569; font-size:0.8rem;'>🕐 {entry['timestamp']}</div>
                </div>
                <div style='color:#475569; font-size:0.75rem; margin-top:4px;'>
                    Raw OCR: <code style='color:#64748b;'>{entry['raw_ocr'] or '—'}</code>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='text-align:center; padding:50px; color:#475569;'>
            <div style='font-size:3rem;'>📋</div>
            <p>No scan history yet. Run a recognition to see results here.</p>
        </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: ABOUT THE PROJECT
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "ℹ️  About the Project":
    st.markdown("## ℹ️ About the Project")

    tabs = st.tabs([
        "Overview", "Objectives", "Workflow",
        "Technologies", "Applications", "Limitations & Future"
    ])

    with tabs[0]:
        st.markdown("""
        ### Problem Statement
        Manual vehicle identification at checkpoints, parking lots, toll booths, and traffic monitoring
        stations is slow, error-prone, and labor-intensive. An automated system that can read number
        plates from camera images reduces human effort and improves response time.

        ### Project Overview
        This academic project demonstrates a complete **Number Plate Recognition (NPR)** pipeline
        built entirely with open-source Python libraries. It covers the full workflow from image
        upload to database lookup, presented in a professional Streamlit web interface.

        The system is designed for educational purposes and runs locally on a standard student laptop
        without any paid APIs, cloud services, or internet connectivity.
        """)

    with tabs[1]:
        st.markdown("""
        ### Objectives
        1. **Demonstrate** an end-to-end image processing pipeline for number plate recognition.
        2. **Apply** computer vision techniques (grayscale conversion, noise reduction, edge detection,
           contour analysis) to locate the plate region.
        3. **Integrate** Tesseract OCR to extract alphanumeric text from the plate.
        4. **Build** a SQLite-backed vehicle database and perform registration lookup.
        5. **Deliver** a clean, professional Streamlit web interface suitable for academic demonstration.
        6. **Document** limitations, accuracy constraints, and future improvement paths.
        """)

    with tabs[2]:
        st.markdown("""
        ### System Workflow

        ```
        ┌────────────────────┐
        │   Image Upload     │  JPG / JPEG / PNG via browser
        └────────┬───────────┘
                 │
        ┌────────▼───────────┐
        │  Image Validation  │  Format check, size handling
        └────────┬───────────┘
                 │
        ┌────────▼───────────┐
        │  Preprocessing     │  Resize → Grayscale → Bilateral Filter
        │                    │  → Adaptive Threshold → Edge Detection
        └────────┬───────────┘
                 │
        ┌────────▼───────────┐
        │  Plate Localization│  Contour detection, aspect-ratio filtering,
        │                    │  bounding box extraction
        └────────┬───────────┘
                 │
        ┌────────▼───────────┐
        │  Plate Crop + Zoom │  Crop ROI, upscale, sharpen, Otsu threshold
        └────────┬───────────┘
                 │
        ┌────────▼───────────┐
        │  Tesseract OCR     │  PSM 7/8, character whitelist A-Z0-9
        └────────┬───────────┘
                 │
        ┌────────▼───────────┐
        │  Normalization     │  Remove non-alphanumeric, uppercase
        └────────┬───────────┘
                 │
        ┌────────▼───────────┐
        │  SQLite Lookup     │  Match against vehicle records table
        └────────┬───────────┘
                 │
        ┌────────▼───────────┐
        │  Result Display    │  Owner info / "Not Found" message
        └────────┬───────────┘
                 │
        ┌────────▼───────────┐
        │  History Logging   │  Save timestamp, OCR text, match status
        └────────────────────┘
        ```
        """)

    with tabs[3]:
        st.markdown("""
        ### Technologies Used

        | Component | Technology | Purpose |
        |-----------|-----------|---------|
        | Web Interface | **Streamlit 1.x** | Interactive dashboard and UI |
        | Image Processing | **OpenCV 4/5** | Preprocessing, edge detection, contours |
        | OCR Engine | **Tesseract + pytesseract** | Text extraction from plate images |
        | Image Handling | **Pillow (PIL)** | Image I/O and format conversion |
        | Numerical Processing | **NumPy** | Array operations on image data |
        | Database | **SQLite 3** | Vehicle records and scan history |
        | Language | **Python 3.11** | Core application logic |

        ### Key Algorithms
        - **Bilateral Filter**: Edge-preserving noise reduction (better than Gaussian for OCR prep)
        - **Canny Edge Detection**: Identify plate boundaries
        - **Contour Analysis + Douglas-Peucker**: Approximate rectangular shapes (license plates)
        - **Adaptive Thresholding + Otsu**: Binarize plate image for OCR
        - **Tesseract PSM 7**: Single-line text extraction mode ideal for plates
        """)

    with tabs[4]:
        st.markdown("""
        ### Real-World Applications
        - 🚧 **Traffic Monitoring** – Speed cameras, red-light detection
        - 🅿️ **Parking Management** – Automated entry/exit gates
        - 🛣️ **Toll Collection** – Contactless toll booth systems
        - 🔒 **Security & Access Control** – Gated communities, corporate campuses
        - 🚔 **Law Enforcement** – Identifying stolen or flagged vehicles
        - 🏭 **Fleet Management** – Tracking delivery and logistics vehicles

        ### Advantages of This System
        - 100% open-source, no paid APIs required
        - Runs offline on a standard laptop
        - Modular codebase (easy to extend)
        - Configurable OCR pipeline
        - Persistent scan history
        """)

    with tabs[5]:
        st.markdown("""
        ### Known Limitations
        | Limitation | Impact |
        |------------|--------|
        | OCR accuracy depends heavily on image quality | Poor lighting → wrong text |
        | Contour detection may miss non-standard plates | Fancy fonts, damaged plates |
        | No real-time video processing | Static images only |
        | No angle/perspective correction | Tilted plates reduce accuracy |
        | Small demo database | Only 8 fictional records |
        | Single-country plate format bias | May struggle with foreign plates |

        ### Future Enhancements
        1. **Deep Learning Plate Detection** – YOLOv8 or SSD model for robust localization
        2. **Perspective Correction** – Homography-based plate de-warping
        3. **Real-Time Video** – Process webcam or CCTV stream frame by frame
        4. **Multi-Country Support** – Region-specific OCR configs and format validators
        5. **REST API** – Expose recognition endpoint for integration with other systems
        6. **Admin Panel** – Add/edit/remove vehicle records via UI
        7. **Email/SMS Alerts** – Notify on flagged vehicle detection
        8. **Cloud Deployment** – Docker container deployable to AWS / GCP / Azure
        """)

    st.markdown("---")
    st.markdown("""
    <div style='text-align:center; color:#475569; font-size:0.82rem; padding:10px;'>
        Number Plate Recognition System · Academic Project · Python + OpenCV + Tesseract + Streamlit<br>
        ⚠️ All vehicle data is fictional and for demonstration purposes only.
    </div>
    """, unsafe_allow_html=True)
