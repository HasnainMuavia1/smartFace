import os
import sys
import numpy as np
import cv2
import face_recognition
import datetime
from django.utils import timezone
import django
from django.conf import settings

# Configure project environment
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
django.setup()

from core.models import Student, Attendance, Course, Faculty
from django.db import transaction


def load_student_faces(course_id):
    """Load and encode faces from student profile pictures for a specific course"""
    known_face_encodings = []
    known_student_ids = []
    student_names = []
    
    print(f"\nLoading student faces for course ID: {course_id}")
    
    try:
        # Get all students enrolled in the course
        students = Student.objects.filter(courses__id=course_id)
        print(f"Found {students.count()} students enrolled in this course")
        
        for student in students:
            if not student.profile_picture:
                print(f"Student {student.user.get_full_name()} has no profile picture. Skipping.")
                continue
                
            try:
                # Get the file path of the student's profile picture
                file_path = os.path.join(settings.MEDIA_ROOT, student.profile_picture.name)
                print(f"\nProcessing: {student.user.get_full_name()} - {file_path}")
                
                if not os.path.exists(file_path):
                    print(f"File not found: {file_path}. Skipping.")
                    continue
                
                # Load the image and find faces
                image = face_recognition.load_image_file(file_path)
                face_locations = face_recognition.face_locations(image, model="hog")
                
                if len(face_locations) != 1:
                    print(f"Skipping {student.user.get_full_name()}: Contains {len(face_locations)} faces (need exactly 1)")
                    continue
                
                # Encode the face and add to our list
                face_encoding = face_recognition.face_encodings(image, face_locations)[0]
                known_face_encodings.append(face_encoding)
                known_student_ids.append(student.id)
                student_names.append(student.user.get_full_name())
                print(f"Successfully loaded: {student.user.get_full_name()}")
                
            except Exception as e:
                print(f"Error processing {student.user.get_full_name()}: {str(e)}")
    
    except Exception as e:
        print(f"Error loading students: {str(e)}")
    
    print(f"\nTotal student faces loaded: {len(known_student_ids)}")
    return known_face_encodings, known_student_ids, student_names


def mark_student_attendance(student_id, course_id, is_present, faculty_user):
    """Mark attendance for a student in a specific course"""
    try:
        student = Student.objects.get(id=student_id)
        course = Course.objects.get(id=course_id)
        today = timezone.now().date()
        
        # Update or create attendance record
        attendance, created = Attendance.objects.update_or_create(
            student=student,
            course=course,
            date=today,
            defaults={
                'is_present': is_present,
                'marked_by': faculty_user
            }
        )
        
        action = "Created" if created else "Updated"
        status = "present" if is_present else "absent"
        print(f"{action} attendance record: {student.user.get_full_name()} marked as {status}")
        return True
    
    except Exception as e:
        print(f"Error marking attendance: {str(e)}")
        return False


def run_face_recognition_attendance(course_id, faculty_user):
    """Run face recognition to mark attendance for a specific course"""
    results = {
        'success': False,
        'present_students': [],
        'absent_students': [],
        'error': None
    }
    
    try:
        # Get course information
        course = Course.objects.get(id=course_id)
        print(f"Starting attendance for course: {course.name} ({course.code})")
        
        # Load student faces for this course
        known_face_encodings, known_student_ids, student_names = load_student_faces(course_id)
        
        if not known_face_encodings:
            results['error'] = "No valid student faces found. Make sure students have profile pictures."
            return results
        
        # Get all students in this course for marking absences later
        all_students = set(Student.objects.filter(courses__id=course_id).values_list('id', flat=True))
        recognized_students = set()
        
        # Initialize webcam
        video_capture = cv2.VideoCapture(0)
        if not video_capture.isOpened():
            results['error'] = "Could not access webcam. Please check your camera connection."
            return results
        
        video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Display instructions
        print("\nFace Recognition Attendance System")
        print("--------------------------------")
        print("Press 'q' to quit and save attendance")
        print("Students recognized will be marked present")
        print("All other enrolled students will be marked absent\n")
        
        try:
            while True:
                ret, frame = video_capture.read()
                if not ret:
                    continue
                
                # Resize frame for faster face recognition
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                
                # Find faces in the frame (coordinates in small_frame scale)
                face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                
                # Process each face found in the frame
                for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                    # Check for a frontal face by examining the eye positions.
                    # Get landmarks for this face
                    landmarks_list = face_recognition.face_landmarks(rgb_small_frame, [(top, right, bottom, left)])
                    if landmarks_list:
                        landmarks = landmarks_list[0]
                        if 'left_eye' in landmarks and 'right_eye' in landmarks:
                            left_eye = np.array(landmarks['left_eye'])
                            right_eye = np.array(landmarks['right_eye'])
                            left_eye_center = left_eye.mean(axis=0)
                            right_eye_center = right_eye.mean(axis=0)
                            eye_distance = np.linalg.norm(left_eye_center - right_eye_center)
                            face_width_small = right - left
                            ratio = eye_distance / face_width_small
                            # If the eye distance ratio is less than 0.4, assume a side face and skip it
                            if ratio < 0.4:
                                # Draw a red rectangle with label "Side Face"
                                cv2.rectangle(frame, (left*4, top*4), (right*4, bottom*4), (0, 0, 255), 2)
                                cv2.rectangle(frame, (left*4, (bottom*4) - 35), (right*4, bottom*4), (0, 0, 255), cv2.FILLED)
                                cv2.putText(frame, "Side Face", (left*4 + 6, (bottom*4) - 6),
                                            cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
                                continue
                    
                    # Scale back up face locations for display (multiply by 4)
                    top_display = top * 4
                    right_display = right * 4
                    bottom_display = bottom * 4
                    left_display = left * 4
                    
                    # Check if the face matches any known student using a stricter threshold (0.4)
                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    name = "Unknown"
                    
                    if face_distances[best_match_index] < 0.4:
                        student_id = known_student_ids[best_match_index]
                        name = student_names[best_match_index]
                        
                        # Add to recognized students set
                        recognized_students.add(student_id)
                        
                        if name not in results['present_students']:
                            results['present_students'].append(name)
                            print(f"Recognized: {name}")
                    
                    # Draw rectangle and name on the original frame
                    color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                    cv2.rectangle(frame, (left_display, top_display), (right_display, bottom_display), color, 2)
                    cv2.rectangle(frame, (left_display, bottom_display - 35), (right_display, bottom_display), color, cv2.FILLED)
                    cv2.putText(frame, name, (left_display + 6, bottom_display - 6),
                                cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
                
                # Display the resulting frame
                cv2.imshow('Attendance System', frame)
                
                # Break loop on 'q' key press
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        finally:
            # Release webcam and close windows
            video_capture.release()
            cv2.destroyAllWindows()
            
            # Mark attendance for all students
            print("\nSaving attendance records...")
            
            # Mark recognized students as present
            for student_id in recognized_students:
                mark_student_attendance(student_id, course_id, True, faculty_user)
                
            # Mark absent students
            absent_student_ids = all_students - recognized_students
            for student_id in absent_student_ids:
                student = Student.objects.get(id=student_id)
                mark_student_attendance(student_id, course_id, False, faculty_user)
                results['absent_students'].append(student.user.get_full_name())
            
            # Get final attendance counts
            results['success'] = True
            print("\nAttendance Summary:")
            print(f"Total students: {len(all_students)}")
            print(f"Present: {len(recognized_students)}")
            print(f"Absent: {len(absent_student_ids)}")
            
    except Exception as e:
        results['error'] = str(e)
        print(f"Error: {str(e)}")
        if 'video_capture' in locals():
            video_capture.release()
        cv2.destroyAllWindows()
    
    return results


if __name__ == '__main__':
    # This is for testing the script directly.
    # In production, this will be called from the faculty_dashboard views.
    if len(sys.argv) > 1:
        course_id = int(sys.argv[1])
        from django.contrib.auth.models import User
        faculty_user = User.objects.filter(role='faculty').first()
        run_face_recognition_attendance(course_id, faculty_user)
    else:
        print("Please provide a course ID as an argument")
