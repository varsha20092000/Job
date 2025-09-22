# JOB365 – Job Portal Platform

A full-stack Django-based web application where jobseekers and companies can interact.  
Complete with dashboards for companies, admin controls, job listings, and responsive front end.

---

## 🚀 Features

- Role based user types: **Company**, **Jobseeker**, **Admin**
- Company dashboard to post, manage, edit, and delete job listings  
- Jobseeker dashboard to browse jobs, apply, save, check status  
- Tour package listing as an added module  
- Admin panel to review users, listings, applications  
- Uses Tailwind CSS + Vite for modern frontend workflow

---

## 🛠 Tech Stack

- **Backend:** Django, Python  
- **Frontend:** Tailwind CSS, Vite, HTML, JavaScript  
- **Database:** SQLite (development) / PostgreSQL (prod-ready)  
- **Build/Deployment-ready:** Setup includes Render / Railway / Heroku compatibility  
- **Tools:** Git, VS Code, GitHub

---

## 🔧 Installation & Local Setup

```bash
git clone https://github.com/varsha20092000/Job.git
cd Job
python3 -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
npm install
npm run dev   # if you have a dev script for Vite
python manage.py migrate
python manage.py runserver
