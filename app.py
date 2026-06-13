from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, send_file
from werkzeug.utils import secure_filename
import os
import uuid
import base64
import cv2
from datetime import datetime 
from PIL import Image
import io

from config import Config
from database.models import db, User, Report, VisionReport
from utils.prediction import HyphemaPredictor
from utils.heatmap import GradCAMHeatmap
from utils.recommendation import RecommendationSystem
from utils.vision_screening import VisionScreener
from utils.hospital_finder import HospitalFinder
from utils.sms_alert import sms_alert

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)

# Initialize components
predictor = HyphemaPredictor()
recommender = RecommendationSystem()
vision_screener = VisionScreener()
hospital_finder = HospitalFinder()

# Create tables and folders
with app.app_context():
    db.create_all()
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.HEATMAP_FOLDER, exist_ok=True)
    os.makedirs(Config.REPORTS_FOLDER, exist_ok=True)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        return filepath, unique_filename
    return None, None

# ==================== MAIN ROUTES ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/capture')
def capture():
    return render_template('capture.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    """Handle image upload and analysis"""
    print(">>> UPLOAD ROUTE CALLED <<<")
    
    if 'image' not in request.files:
        flash('No image uploaded', 'error')
        return redirect(url_for('capture'))
    
    file = request.files['image']
    
    if file.filename == '':
        flash('No image selected', 'error')
        return redirect(url_for('capture'))
    
    filepath, filename = save_uploaded_file(file)
    
    if not filepath:
        flash('Invalid file type. Use PNG, JPG, or JPEG', 'error')
        return redirect(url_for('capture'))
    
    session['current_image'] = filepath
    session['current_image_filename'] = filename
    
    return redirect(url_for('result'))

@app.route('/capture-image', methods=['POST'])
def capture_image_route():
    """Handle captured image from camera"""
    print(">>> CAPTURE ROUTE CALLED <<<")
    
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data received'}), 400
        
        image_data = data['image']
        
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        filename = f"capture_{uuid.uuid4().hex}.jpg"
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        
        image = Image.open(io.BytesIO(image_bytes))
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        image.save(filepath, 'JPEG', quality=90)
        
        session['current_image'] = filepath
        session['current_image_filename'] = filename
        
        return jsonify({'success': True, 'redirect': '/result'})
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/result')
def result():
    image_path = session.get('current_image')
    filename = session.get('current_image_filename', '')

    session.pop('current_image', None)
    session.pop('current_image_filename', None)

    if not image_path or not os.path.exists(image_path):
        flash('No image to analyze.', 'warning')
        return redirect(url_for('capture'))

    img = cv2.imread(image_path)

    if img is None:
        flash("Error reading image.", "error")
        return redirect(url_for('capture'))

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    eye_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_eye.xml'
    )

    eyes = eye_cascade.detectMultiScale(gray, 1.3, 6)

    import numpy as np

    # ================= EYE DETECTION =================
    if len(eyes) == 0:
        if filename.startswith("capture_"):
            flash("No eye detected. Show eye clearly.", "warning")
            return redirect(url_for('capture'))
        
        # Upload fallback → allow full image
        eye_crop = img.copy()
        x = y = w = h = 0

    else:
        # Take biggest eye
        eye = max(eyes, key=lambda e: e[2] * e[3])
        x, y, w, h = eye

        pad = 25
        x1 = max(0, x - pad)
        y1 = max(0, y - pad)
        x2 = min(img.shape[1], x + w + pad)
        y2 = min(img.shape[0], y + h + pad)

        eye_crop = img[y1:y2, x1:x2]

    # ================= MODEL IMAGE =================
    model_img = cv2.resize(eye_crop, (224, 224))

    # ================= VALIDATION =================
    gray_eye = cv2.cvtColor(model_img, cv2.COLOR_BGR2GRAY)

    dark_pixels = cv2.countNonZero((gray_eye < 60).astype('uint8'))
    total_pixels = gray_eye.size

    dark_ratio = dark_pixels / total_pixels

    if filename.startswith("capture_") and dark_ratio < 0.02:
        flash("Invalid eye. Capture properly.", "warning")
        return redirect(url_for('capture'))

    # ================= RED DETECTION =================
    hsv = cv2.cvtColor(model_img, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

    mask = mask1 + mask2

    red_pixels = cv2.countNonZero(mask)
    total_pixels = model_img.shape[0] * model_img.shape[1]

    red_ratio = red_pixels / total_pixels

    # ================= FINAL RESULT =================
    if red_ratio > 0.05:
        prediction = "Possible Hyphema"
        confidence = 0.80
        severity = 2
    else:
        prediction = "Normal"
        confidence = 0.85
        severity = 0
    # ================= HEATMAP =================
    heatmap_filename = f"heatmap_{uuid.uuid4().hex}.jpg"
    heatmap_path = os.path.join(Config.HEATMAP_FOLDER, heatmap_filename)

    heatmap_generator = GradCAMHeatmap(predictor.model)

    # Step 1: Generate original heatmap
    heatmap_generator.generate_heatmap(image_path, heatmap_path)

    heat_img = cv2.imread(heatmap_path)

    if heat_img is not None:

        # ✅ Resize to match original
        heat_img = cv2.resize(heat_img, (img.shape[1], img.shape[0]))

        # ================= COLOR CONTROL =================
        # Split channels (BGR)
        b, g, r = cv2.split(heat_img)

        # Reduce blue (20%)
        b = cv2.convertScaleAbs(b, alpha=0.5)

        # Medium green → gives yellow effect (30%)
        g = cv2.convertScaleAbs(g, alpha=1.2)

        # Boost red strongly (50%)
        r = cv2.convertScaleAbs(r, alpha=2.0)

        # Merge back
        heat_img = cv2.merge([b, g, r])

        # ================= MULTI EYE MASK =================
        mask = np.zeros((img.shape[0], img.shape[1]), dtype="uint8")

        if len(eyes) > 0:
            for (x, y, w, h) in eyes:
                center = (x + w//2, y + h//2)
                radius = int(max(w, h) * 0.65)

                # Draw circle for BOTH eyes
                cv2.circle(mask, center, radius, 255, -1)
        else:
            # Upload fallback
            mask[:] = 255

        # Smooth mask
        mask = cv2.GaussianBlur(mask, (51, 51), 0)

        # Convert to 3-channel
        mask = cv2.merge([mask, mask, mask]) / 255.0

        # ================= APPLY MASK =================
        focused = heat_img * mask
        background = img * (1 - mask)

        combined = cv2.add(
            background.astype("uint8"),
            focused.astype("uint8")
        )

        # ================= FINAL BLEND =================
        final = cv2.addWeighted(img, 0.6, combined, 0.8, 0)

        cv2.imwrite(heatmap_path, final)
        # ================= OUTPUT =================
        recommendation = recommender.format_recommendation(severity)
        severity_info = predictor.get_severity_info(severity)

        return render_template(
            'result.html',
            image_path=f"images/uploads/{os.path.basename(image_path)}",
            heatmap_path=f"images/heatmaps/{heatmap_filename}",
            prediction=prediction,
            confidence=f"{confidence*100:.1f}%",
            severity=severity,
            severity_info=severity_info,
            recommendation=recommendation
        )
# ==================== HISTORY ROUTES ====================

@app.route('/history')
def history():
    if 'user_id' not in session:
        flash('Please login to view history', 'warning')
        return redirect(url_for('login'))
    
    reports = Report.query.filter_by(user_id=session['user_id']).order_by(Report.created_at.desc()).all()
    vision_reports = VisionReport.query.filter_by(user_id=session['user_id']).order_by(VisionReport.created_at.desc()).all()
    
    return render_template('history.html', reports=reports, vision_reports=vision_reports)

@app.route('/download-report/<int:report_id>')
def download_report(report_id):
    report = Report.query.get_or_404(report_id)
    
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    
    pdf_filename = f"report_{report.id}.pdf"
    pdf_path = os.path.join(Config.REPORTS_FOLDER, pdf_filename)
    
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "Hyphema Detection Report")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Date: {report.created_at.strftime('%Y-%m-%d %H:%M')}")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 120, "Results:")
    
    c.setFont("Helvetica", 12)
    c.drawString(70, height - 140, f"Prediction: {report.prediction}")
    c.drawString(70, height - 160, f"Confidence: {report.confidence*100:.1f}%")
    c.drawString(70, height - 180, f"Severity: {report.severity_label}")
    
    c.save()
    
    return send_file(pdf_path, as_attachment=True)

# ==================== AI ASSISTANT ROUTES ====================

@app.route('/assistant')
def assistant():
    return render_template('assistant.html')

@app.route('/api/assistant/ask', methods=['POST'])
def ask_assistant():
    data = request.get_json()
    question = data.get('question', '').lower()
    
    responses = {
    # BASIC
    'what is hyphema': 'Hyphema is bleeding inside the front chamber of the eye, usually caused by injury.',
    'symptoms': 'Symptoms include red eye, blurred vision, pain, light sensitivity, and visible blood.',
    'treatment': 'Treatment includes rest, eye protection, head elevation, and doctor supervision.',
    'emergency': 'Seek emergency care if vision loss, severe pain, or heavy bleeding occurs.',
    'precautions': 'Avoid rubbing eyes, heavy activity, and keep head elevated.',
    'recovery time': 'Recovery depends on severity: mild (5-7 days), severe (2-4 weeks).',

    # EXTRA EYE QUESTIONS
    'eye pain': 'Eye pain can be due to infection, injury, dryness, or pressure. Consult a doctor if severe.',
    'red eye': 'Red eye can be caused by irritation, infection, or hyphema. If persistent, seek medical help.',
    'blurred vision': 'Blurred vision may result from refractive error, injury, or internal bleeding.',
    'dry eyes': 'Dry eyes happen due to lack of tears. Use artificial tears and reduce screen time.',
    'eye infection': 'Eye infections cause redness, swelling, discharge. Antibiotics may be needed.',
    'vision loss': 'Sudden vision loss is serious. Seek immediate medical attention.',
    'eye pressure': 'High eye pressure can damage vision and may indicate glaucoma.',
    'glaucoma': 'Glaucoma is increased eye pressure damaging optic nerve. Needs early treatment.',
    'cataract': 'Cataract causes cloudy vision due to lens opacity. Surgery can fix it.',
    'eye injury': 'Eye injuries can lead to hyphema or vision damage. Immediate care is important.',
    'eye strain': 'Eye strain is caused by screen overuse. Follow 20-20-20 rule.',
    'floaters': 'Floaters are small spots in vision. Sudden increase may need checkup.',
    'flashes': 'Flashes of light may indicate retinal issues. Consult doctor immediately.',
    'light sensitivity': 'Light sensitivity is common in eye injuries and infections.',
    'itchy eyes': 'Itchy eyes are usually due to allergies or dryness.',
    'watering eyes': 'Excess tears may indicate irritation or blocked tear ducts.',
    'double vision': 'Double vision can be serious and requires medical evaluation.',
    'eye swelling': 'Swelling may be due to infection or injury.',
    'when to see doctor': 'See a doctor if pain, redness, or vision changes persist.',
}
    
    answer = "I can help with eye-related problems like hyphema, symptoms, treatment, vision issues, and eye care. Please ask clearly."

    for key in responses:
        if key in question.lower():
            answer = responses[key]
            break
    return jsonify({'answer': answer, 'timestamp': datetime.now().strftime('%H:%M')})

# ==================== HOSPITAL ROUTES ====================

@app.route('/hospitals')
def hospitals():
    user_location = hospital_finder.get_user_location()
    nearby_hospitals = hospital_finder.find_nearby_hospitals(user_location)
    return render_template('hospitals.html', hospitals=nearby_hospitals, user_location=user_location)

@app.route('/api/hospitals/nearby')
def api_nearby_hospitals():
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    user_location = (lat, lon) if lat and lon else None
    hospitals_list = hospital_finder.find_nearby_hospitals(user_location)
    return jsonify(hospitals_list)

# ==================== VISION SCREENING ROUTES ====================

@app.route('/vision-screening')
def vision_screening():
    return render_template('vision.html')

@app.route('/api/vision/test', methods=['POST'])
def run_vision_test():
    data = request.get_json()
    responses = data.get('responses', [])
    result = vision_screener.simulate_vision_test(responses)
    return jsonify(result)

@app.route('/api/save-vision-report', methods=['POST'])
def save_vision_report():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Please login'}), 401
    
    data = request.get_json()
    
    vision_entry = VisionReport(
        user_id=session['user_id'],
        left_eye_score=data.get('left_eye'),
        right_eye_score=data.get('right_eye'),
        interpretation=data.get('interpretation')
    )
    db.session.add(vision_entry)
    db.session.commit()
    
    return jsonify({'success': True})



# ==================== AUTHENTICATION ROUTES ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.password_hash == password:
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
        elif User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
        else:
            user = User(username=username, email=email, password_hash=password, phone=phone)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

# ==================== ADMIN ROUTES ====================

@app.route('/admin')
def admin_panel():
    if 'username' not in session or session.get('username') != 'admin':
        flash('Admin access required', 'error')
        return redirect(url_for('index'))
    
    users = User.query.all()
    all_reports = Report.query.order_by(Report.created_at.desc()).all()
   
    vision_reports = VisionReport.query.all()
    
    return render_template('admin.html',
                         total_users=len(users),
                         total_reports=len(all_reports),
                         hyphema_cases=len([r for r in all_reports if r.prediction == 'Hyphema Detected']),
                        
                         total_vision_tests=len(vision_reports),
                         users=users,
                         all_reports=all_reports)

# ==================== MAIN ====================

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Hyphema Detection System")
    print("📍 Server: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(host="127.0.0.1", port=5000, debug=True)