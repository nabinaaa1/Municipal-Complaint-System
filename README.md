# MechinagarSewa – Citizen Voice Portal

A web-based Citizen Complaint Management System developed for **Mechinagar Municipality**, Jhapa, Koshi Province, Nepal. The platform enables citizens to submit, track, and provide feedback on civic complaints across all 15 wards, while giving municipal administrators tools to manage and resolve them efficiently.

---

## Features

### Citizen
- Register and login with email-based authentication
- Submit complaints with ward selection, category, description, and photo upload
- Track complaint status in real-time (Pending / In Progress / Resolved)
- View complaint history with pagination and date filters
- Submit 5-star feedback on resolved complaints

### Admin
- Dashboard with total, pending, in-progress, and resolved complaint counts
- Ward-wise and category-wise complaint distribution with progress bars
- Manage all complaints with multi-filter system (status, ward, category, date range, keyword search)
- Update complaint status and add internal remarks (invisible to citizens)
- Auto-priority escalation — complaints older than 7 days flagged as Urgent
- Detailed statistics page with 7-day, 30-day metrics and resolution rate
- Export filtered complaints to CSV with timestamped filenames

### System
- Fully bilingual interface — English and Nepali (session-based switching)
- Role-based access control — citizen vs admin
- Automatic image compression (max 1920x1080, 85% quality) using Pillow
- Database indexing for optimized query performance
- Responsive design with Bootstrap 5

---

## Tech Stack

- Backend → Python 3.12, Django 6.0
- Frontend → Bootstrap 5, HTML5, CSS3, JavaScript
- Database → SQLite3
- Image Processing → Pillow
- Icons → Font Awesome 6
- Fonts → Plus Jakarta Sans, Sora

---

## Installation

**1. Clone the repository**

```
git clone https://github.com/nabinaaa1/Municipal-Complaint-System.git
cd Municipal-Complaint-System
```

**2. Create and activate virtual environment**

```
python -m venv venv
```

Windows:

```
venv\Scripts\activate
```

macOS/Linux:

```
source venv/bin/activate
```

**3. Install dependencies**

```
pip install django pillow
```

**4. Apply migrations**

```
python manage.py migrate
```

**5. Create a superuser (admin account)**

```
python manage.py createsuperuser
```

**6. Run the development server**

```
python manage.py runserver
```

**7. Open in browser**

```
http://127.0.0.1:8000/
```

---

## Project Structure

```
Municipal-Complaint-System/
├── mechinagar_system/   # Project config (settings, urls, wsgi, asgi)
├── accounts/            # Custom User model, registration, login, citizen dashboard
├── complaints/          # Complaint model, citizen views, admin views, admin dashboard
├── feedback/            # Feedback model, star rating, feedback listing
├── core/                # Home page, language switching, translation system
├── templates/           # Base template and all HTML templates
├── static/              # Static files (CSS, JS, images)
├── media/               # Uploaded complaint images
├── db.sqlite3           # SQLite database
└── manage.py
```

---

## Database Models

- **User** → extends AbstractUser with fullname, phone, address, ward (1-15)
- **Complaint** → user, ward, category, description, image, status, priority, timestamps
- **Remark** → complaint, admin_user, remark, timestamp (admin-only internal notes)
- **Feedback** → user, complaint, rating (1-5), message, timestamp

---

## Management Commands

Auto-update complaint priorities for complaints older than 7 days:

```
python manage.py update_priorities
```

Can be scheduled as a cron job:

```
0 0 * * * /path/to/venv/bin/python /path/to/manage.py update_priorities
```

---

## Usage

### Citizen Flow
1. Register at `/accounts/register/`
2. Login at `/accounts/login/`
3. Submit a complaint at `/complaints/submit/`
4. Track complaints at `/complaints/my-complaints/`
5. Give feedback on resolved complaints at `/feedback/submit/<complaint_id>/`

### Admin Flow
1. Login at `/admin/` using your superuser credentials
2. View dashboard at `/complaints/admin/dashboard/`
3. Manage complaints at `/complaints/admin/list/`
4. View statistics at `/complaints/admin/statistics/`
5. Export data via the CSV export button on the complaint list page

### Language Switching
Click **EN / NE** in the navbar to switch between English and Nepali. Preference is saved for the session.

---

## License

This project was developed as part of an internship at **Mechinagar Municipality IT Department**, Jhapa, Nepal.