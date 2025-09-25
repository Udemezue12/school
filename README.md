🎓📚 Secondary School Portal

🌍 Live Demo: School Portal

📝 About

The Secondary School Portal is a full-featured digital school management system designed to simplify and modernize school operations.

✅ Teachers can:

Upload results, assignments, and class materials

Manage subjects and student records

Send notifications and updates

✅ Students can:

Check results online securely

Access assignments and uploaded materials

View school activities and announcements

🎯 The system enhances communication, transparency, and digital learning in secondary schools.

🚀 Features

👩‍🏫 Teacher’s Dashboard – upload results, assignments, materials

👨‍🎓 Student’s Dashboard – view results, assignments, and announcements

🏫 School Activities – announcements, events, timetables

🔒 Authentication – secure login with JWT & Flask-Login

💳 Payment Integration – Paystack & Stripe support for fees

📧 Email Notifications – via Flask-Mail

🎨 Clean UI – responsive HTML templates with Flask-WTF forms

⚡ Production Ready – Gunicorn/Waitress + Whitenoise for static files

📂 Project Structure
school-portal/
│── __pycache__/           # Python cache
│── school_project/        # Core app (models, routes, views)
│── .gitignore             # Ignore unnecessary files
│── Procfile               # For Render/Heroku deployment
│── app.py                 # Main app entry
│── clean.py               # Maintenance/utility scripts
│── config.py              # Main configuration
│── config-1.py            # Alternate config
│── requirements.txt       # Python dependencies

🛠️ Tech Stack
Layer	Technology
🌐 Backend	Flask 3.0.3 + Flask-RESTful
🎨 Frontend	Jinja2 templates, HTML, CSS, JS
🗄️ Database	SQLAlchemy + Flask-Migrate (supports MySQL via PyMySQL)
🔒 Auth	Flask-Login + Flask-JWT + Bcrypt
💳 Payments	Paystack + Stripe
💌 Email	Flask-Mail
🚀 Deployment	Render + Gunicorn + Waitress + Whitenoise
⚙️ Installation
1️⃣ Clone the repo
git clone https://github.com/your-username/school-portal.git
cd school-portal

2️⃣ Create virtual environment
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Setup environment variables (.env)
SECRET_KEY=supersecretkey
DATABASE_URL=mysql+pymysql://user:password@localhost/school_portal
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_password
PAYSTACK_SECRET_KEY=your_paystack_key
STRIPE_SECRET_KEY=your_stripe_key

5️⃣ Run database migrations
flask db init
flask db migrate
flask db upgrade

6️⃣ Start development server
python app.py


App runs at 👉 http://127.0.0.1:5000/

🐳 Deployment (Render/Heroku)
Run locally with Gunicorn
gunicorn app:app

Render Deployment

Uses Procfile

Push code to GitHub → Connect to Render → Deploy

Live: https://school-portal-dsyf.onrender.com

🤝 Contributing

Fork this repo 🍴

Create a branch (feature/awesome) 🌱

Commit changes ✅

Push branch 🚀

Open a PR 🔥

📜 License

MIT License © 2025 — Free to use & modify for school projects.

✨ Ready to take your secondary school digital?
👉 Try it now: School Portal