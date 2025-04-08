from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import json
from content_generator import ContentGenerator
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
import tempfile

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Configure CORS to allow all origins
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///educational_content.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    generation_requests = db.relationship('GenerationRequest', backref='user', lazy=True)

class GenerationRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(200), nullable=False)
    grade_level = db.Column(db.String(50), nullable=False)
    content_types = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    contents = db.relationship('GeneratedContent', backref='request', lazy=True)

class GeneratedContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content_type = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    request_id = db.Column(db.Integer, db.ForeignKey('generation_request.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

# Initialize content generator
content_generator = ContentGenerator()

def init_db():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if default user exists
        default_user = User.query.filter_by(username='default_user').first()
        if not default_user:
            # Create default user
            default_user = User(
                username='default_user',
                email='default@example.com'
            )
            db.session.add(default_user)
            db.session.commit()
            print("Default user created successfully")
        else:
            print("Default user already exists")

@app.route('/api/generate', methods=['POST'])
def generate_content():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('subject'):
            return jsonify({"error": "Le sujet est requis"}), 400
        if not data.get('gradeLevel'):
            return jsonify({"error": "Le niveau scolaire est requis"}), 400
        if not data.get('contentTypes'):
            return jsonify({"error": "Les types de contenu sont requis"}), 400

        # Generate content using the content generator
        generated_content = content_generator.generate_all_content(data)
        
        if not generated_content:
            return jsonify({"error": "Aucun contenu n'a pu être généré"}), 500

        return jsonify(generated_content)
    
    except Exception as e:
        print(f"Error in generate_content: {str(e)}")  # Log the error
        return jsonify({"error": str(e)}), 500

@app.route('/api/save', methods=['POST'])
def save_content():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Aucune donnée reçue"}), 400

        content = data.get('content')
        form_data = data.get('formData')
        
        if not content or not form_data:
            return jsonify({"error": "Contenu ou données du formulaire manquants"}), 400

        # Get default user
        default_user = User.query.filter_by(username='default_user').first()
        if not default_user:
            return jsonify({"error": "Utilisateur par défaut non trouvé"}), 500

        # Create a new generation request
        new_request = GenerationRequest(
            subject=form_data['subject'],
            grade_level=form_data['gradeLevel'],
            content_types=json.dumps(form_data['contentTypes']),
            user_id=default_user.id
        )
        db.session.add(new_request)
        db.session.flush()  # Get the ID of the new request
        
        # Save each content type
        for content_type, content_data in content.items():
            try:
                generated_content = GeneratedContent(
                    content_type=content_type,
                    content=json.dumps(content_data),
                    request_id=new_request.id
                )
                db.session.add(generated_content)
            except Exception as e:
                print(f"Error saving content type {content_type}: {str(e)}")
                db.session.rollback()
                return jsonify({"error": f"Erreur lors de la sauvegarde du type de contenu {content_type}"}), 500
        
        db.session.commit()
        return jsonify({"message": "Contenu sauvegardé avec succès"})
    
    except Exception as e:
        db.session.rollback()
        print(f"Error in save_content: {str(e)}")  # Log the error
        return jsonify({"error": f"Erreur lors de la sauvegarde: {str(e)}"}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    try:
        # Get default user
        default_user = User.query.filter_by(username='default_user').first()
        if not default_user:
            return jsonify({"error": "Utilisateur par défaut non trouvé"}), 500

        # Get all requests for the default user
        requests = GenerationRequest.query.filter_by(user_id=default_user.id).all()
        history = []
        
        for req in requests:
            history.append({
                "id": req.id,
                "subject": req.subject,
                "grade_level": req.grade_level,
                "content_types": json.loads(req.content_types),
                "created_at": req.created_at.isoformat(),
                "contents": [
                    {
                        "type": content.content_type,
                        "content": json.loads(content.content)
                    }
                    for content in req.contents
                ]
            })
        
        return jsonify(history)
    
    except Exception as e:
        print(f"Error in get_history: {str(e)}")  # Log the error
        return jsonify({"error": str(e)}), 500

def generate_pdf_content(request_data):
    # Create a BytesIO object to store the PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    
    # Add title
    elements.append(Paragraph(f"Contenu pédagogique: {request_data['subject']}", title_style))
    elements.append(Paragraph(f"Niveau: {request_data['grade_level']}", styles['Heading2']))
    elements.append(Spacer(1, 20))
    
    # Add each content type
    for content_type, content in request_data['content'].items():
        # Content type header
        elements.append(Paragraph(content_type, styles['Heading3']))
        elements.append(Spacer(1, 10))
        
        if content_type == 'QCM':
            # Format QCM questions
            for q in content:
                elements.append(Paragraph(f"Question: {q['question']}", styles['Normal']))
                elements.append(Spacer(1, 5))
                for i, option in enumerate(q['options'], 1):
                    elements.append(Paragraph(f"{i}. {option}", styles['Normal']))
                elements.append(Spacer(1, 10))
        
        elif content_type == 'Exercices':
            # Format exercises
            for ex in content:
                elements.append(Paragraph(f"Exercice: {ex['question']}", styles['Normal']))
                elements.append(Paragraph(f"Réponse: {ex['answer']}", styles['Normal']))
                elements.append(Spacer(1, 10))
        
        elif content_type == 'Textes à trous':
            # Format fill-in-the-blanks
            for t in content:
                elements.append(Paragraph(f"Texte: {t['text']}", styles['Normal']))
                elements.append(Paragraph(f"Réponses: {', '.join(t['answers'])}", styles['Normal']))
                elements.append(Spacer(1, 10))
        
        elif content_type == 'Résumés':
            # Format summaries
            for r in content:
                elements.append(Paragraph(r['summary'], styles['Normal']))
                elements.append(Spacer(1, 10))
        
        elif content_type == 'Cartes conceptuelles':
            # Format concept maps
            for c in content:
                elements.append(Paragraph(f"Concept: {c['concept']}", styles['Normal']))
                elements.append(Paragraph(f"Description: {c['description']}", styles['Normal']))
                elements.append(Spacer(1, 10))
        
        elements.append(Spacer(1, 20))
    
    # Build the PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

@app.route('/api/download-pdf/<int:request_id>', methods=['GET'])
def download_pdf(request_id):
    try:
        # Get the generation request
        generation_request = GenerationRequest.query.get_or_404(request_id)
        
        # Get the default user
        default_user = User.query.filter_by(username='default_user').first()
        if not default_user or generation_request.user_id != default_user.id:
            return jsonify({"error": "Accès non autorisé"}), 403
        
        # Prepare data for PDF generation
        request_data = {
            'subject': generation_request.subject,
            'grade_level': generation_request.grade_level,
            'content': {}
        }
        
        # Add each content type
        for content in generation_request.contents:
            request_data['content'][content.content_type] = json.loads(content.content)
        
        # Generate PDF
        pdf_buffer = generate_pdf_content(request_data)
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(pdf_buffer.getvalue())
            tmp_path = tmp.name
        
        # Send the file
        return send_file(
            tmp_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"contenu_{generation_request.subject}_{generation_request.grade_level}.pdf"
        )
    
    except Exception as e:
        print(f"Error in download_pdf: {str(e)}")
        return jsonify({"error": f"Erreur lors de la génération du PDF: {str(e)}"}), 500

if __name__ == '__main__':
    # Initialize database and create default user
    init_db()
    # Run the server on all available network interfaces
    app.run(host='0.0.0.0', port=5000, debug=True)
