# Faculty Attendance Portal

A comprehensive Django-based portal system with three dashboards (Admin, Faculty, and Student) featuring face recognition-based attendance tracking.

## Features

### Admin Dashboard
- Manage faculty and student accounts
- Create and manage courses
- View attendance reports
- System configuration

### Faculty Dashboard
- Mark attendance using face recognition
- View student attendance records
- Manage course materials
- Update profile information

### Student Dashboard
- View personal attendance records
- Access course materials
- View timetable
- Update profile information

## Face Recognition Attendance System
- Automatically recognizes student faces from profile pictures
- Marks students as present/absent in real-time
- Stores attendance records for specific courses
- Faculty can review attendance results before finalizing

## Technology Stack

- **Backend**: Django 5.1.7
- **Database**: SQLite (default)
- **Frontend**: HTML, CSS, JavaScript
- **Face Recognition**: face_recognition library
- **Image Processing**: OpenCV

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment tool (recommended)
- Webcam (for face recognition functionality)

### Setting Up Development Environment

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Project
   ```

2. **Create and activate a virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # Linux/Mac
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install face recognition dependencies**
   
   The face recognition functionality requires additional dependencies:
   ```bash
   pip install face_recognition opencv-python
   ```

5. **Configure the database**
   ```bash
   cd portal
   python manage.py migrate
   ```

6. **Create a superuser (admin)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the portal**
   - Admin dashboard: http://127.0.0.1:8000/admin/
   - Main portal: http://127.0.0.1:8000/

## Usage

### Admin
1. Log in with your superuser credentials
2. Create courses through the admin dashboard
3. Add faculty members and assign them to courses
4. Add students and enroll them in courses

### Faculty
1. Log in with your faculty credentials (default password: "faculty123")
2. Navigate to your dashboard
3. Select a course to mark attendance
4. Use the face recognition system to mark attendance
5. Review and finalize attendance records

### Students
1. Log in with your student credentials
2. View your attendance records
3. Check your course schedule
4. Update your profile picture for the face recognition system

## Directory Structure

```
portal/
├── admin_dashboard/    # Admin dashboard application
├── core/               # Core models and functionality
├── faculty_dashboard/  # Faculty dashboard application
├── media/              # User uploaded files
│   ├── faculty/        # Faculty profile pictures
│   └── students/       # Student profile pictures
├── portal/             # Main project settings
├── scripts/            # Utility scripts including face recognition
├── static/             # Static files (CSS, JS, images)
├── student_dashboard/  # Student dashboard application
└── templates/          # HTML templates
```

## Face Recognition Setup

For the face recognition system to work properly:
1. Ensure all students have profile pictures uploaded
2. Profile pictures should contain only one clearly visible face
3. Good lighting conditions are necessary for accurate recognition
4. The system works best with frontal face images

## Development

### Adding New Features
1. Create a new branch for your feature
2. Implement your changes
3. Write tests for your feature
4. Submit a pull request

### Database Migrations
When making changes to models:
```bash
python manage.py makemigrations
python manage.py migrate
```

## Troubleshooting

### Face Recognition Issues
- Ensure proper lighting when using the webcam
- Make sure student profile pictures are clear and contain only one face
- Check that the webcam is properly connected and accessible

### Login Issues
- Default faculty password is "faculty123"
- Use the password reset functionality if needed
- Contact an administrator for account issues

## License

[Your License Information]

## Contributors

[List of Contributors]
