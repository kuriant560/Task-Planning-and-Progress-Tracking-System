import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.coursework.me.readonly'
]

def get_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                return None
            # Using run_local_server for local Streamlit apps
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def fetch_google_classroom_assignments():
    creds = get_credentials()
    if not creds:
        return None, "Missing credentials.json file. Please place it in the project root."
        
    try:
        service = build('classroom', 'v1', credentials=creds)
        
        # 1. Get active courses
        results = service.courses().list(courseStates=['ACTIVE']).execute()
        courses = results.get('courses', [])
        
        assignments = []
        for course in courses:
            course_id = course['id']
            course_name = course['name']
            
            # 2. Get coursework for each course
            try:
                cw_results = service.courses().courseWork().list(courseId=course_id).execute()
                course_work = cw_results.get('courseWork', [])
                
                for work in course_work:
                    if work.get('workType') == 'ASSIGNMENT':
                        # Extract due date if available
                        due_date = work.get('dueDate')
                        due_date_str = None
                        if due_date:
                            due_date_str = f"{due_date.get('year')}-{due_date.get('month'):02d}-{due_date.get('day'):02d}"
                        
                        assignments.append({
                            'title': f"[{course_name}] {work.get('title')}",
                            'description': work.get('description', ''),
                            'due_date': due_date_str,
                            'external_id': work.get('id')
                        })
            except Exception as e:
                # User might not have access to a specific course's coursework
                continue
                    
        return assignments, "Successfully fetched assignments."
        
    except Exception as e:
        return None, f"An API error occurred: {str(e)}"
