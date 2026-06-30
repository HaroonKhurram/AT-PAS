from app import app

def test_routes():
    # List of routes to test
    routes = [
        ('/admin_dashboard', 'admin'),
        ('/teacher_dashboard', 'teacher'),
        ('/student_dashboard', 'student'),
        ('/admin/user_management', 'admin'),
        ('/teacher/mark_attendance', 'teacher'),
        ('/student/attendance', 'student')
    ]
    
    # Run in test client
    with app.test_client() as client:
        print("Testing unauthorized access (No Session)...")
        for route, role in routes:
            response = client.get(route)
            print(f"Route: {route} | Status Code: {response.status_code}")
            if response.status_code != 404:
                print(f"!!! FAILED: {route} should return 404 but returned {response.status_code}")
            else:
                print(f"PASSED: {route} returned 404")
        
        print("\nTesting cross-role access (Logged in as Teacher, trying Admin)...")
        with client.session_transaction() as sess:
            sess['user_id'] = 1 # Assuming teacher ID 1 exists
            # We need to mock the User query or have a real DB. 
            # Since we're using the real app context, it will check the DB.
            pass
            
if __name__ == "__main__":
    test_routes()
