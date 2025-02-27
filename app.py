from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gallery.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Fixed typo
db = SQLAlchemy(app)

# Ensure the upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(100), nullable=False)  # Store filename

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        image = request.files['image']

        if image:
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)

            # Save the image details in the database
            new_image = Image(title=title, category=category, filename=filename)
            db.session.add(new_image)
            db.session.commit()
            return redirect(url_for('gallery'))

    return render_template('index.html')

@app.route('/gallery')
def gallery():
    category_filter = request.args.get('category', None)

    if category_filter:
        images = Image.query.filter_by(category=category_filter).all()
    else:
        images = Image.query.all()

    # Fetch all distinct categories for filtering
    categories = [c[0] for c in db.session.query(Image.category).distinct().all()]

    return render_template('gallery.html', images=images, categories=categories)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
