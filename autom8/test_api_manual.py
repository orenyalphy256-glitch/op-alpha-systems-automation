"""
test_api_manual.py - Interactive API testing script
Run: python -m autom8.test_api_manual
"""
import requests
import json
from time import sleep

BASE_URL = "http://localhost:5000/api/v1"

def print_response(response, title):
    """Pretty print API response."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def main():
    print("AUTOM8 API MANUAL TEST SUITE")
    print("="*60)
    print("Ensure API server is running: python run_api.py")
    input("Press Enter to continue...")
    
    # Test 1: Health Check
    print("\n[TEST 1] Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response, "GET /health")
    sleep(1)
    

    # Test 2: List contacts (should be empty or have seed data)
    print("\n[TEST 2] List All Contacts")
    response = requests.get(f"{BASE_URL}/contacts")
    print_response(response, "GET /contacts")
    sleep(1)
    

    # Test 3: Create new contact
    print("\n[TEST 3] Create New Contact")
    new_contact = {
        "name": "API Test User",
        "phone": "0798888888",
        "email": "apitest@example.com"
    }
    response = requests.post(f"{BASE_URL}/contacts", json=new_contact)
    print_response(response, "POST /contacts")
    
    if response.status_code == 201:
        contact_id = response.json()['id']
        print(f"\nContact created with ID: {contact_id}")
        sleep(1)
        

    # Test 4: Get single contact
    print("\n[TEST 4] Get Single Contact")
    response = requests.get(f"{BASE_URL}/contacts/{contact_id}")
    print_response(response, f"GET /contacts/{contact_id}")
    sleep(1)
        
    # Test 5: Update contact
    print("\n[TEST 5] Update Contact")
    update_data = {"email": "updated@example.com"}
    response = requests.put(f"{BASE_URL}/contacts/{contact_id}", json=update_data)
    print_response(response, f"PUT /contacts/{contact_id}")
    sleep(1)
        
    # Test 6: Search contacts
    print("\n[TEST 6] Search Contacts")
    response = requests.get(f"{BASE_URL}/contacts?search=API")
    print_response(response, "GET /contacts?search=API")
    sleep(1)
        
    # Test 7: Delete contact
    print("\n[TEST 7] Delete Contact")
    response = requests.delete(f"{BASE_URL}/contacts/{contact_id}")
    print(f"\n{'='*60}")
    print(f"DELETE /contacts/{contact_id}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    if response.status_code == 204:
        print("Contact deleted successfully (204 No Content)")
    sleep(1)
        
    # Test 8: Verify deletion
    print("\n[TEST 8] Verify Deletion (should return 404)")
    response = requests.get(f"{BASE_URL}/contacts/{contact_id}")
    print_response(response, f"GET /contacts/{contact_id} (after delete)")
    
    # Test 9: Error handling - duplicate phone
    print("\n[TEST 9] Error Handling - Duplicate Phone")
    duplicate = {"name": "Duplicate Test", "phone": "0712345678"}
    response = requests.post(f"{BASE_URL}/contacts", json=duplicate)
    print_response(response, "POST /contacts (duplicate)")
    
    # Create another with same phone
    response = requests.post(f"{BASE_URL}/contacts", json=duplicate)
    print_response(response, "POST /contacts (duplicate attempt 2)")
    
    # Test 10: Validation - missing fields
    print("\n[TEST 10] Validation - Missing Required Fields")
    invalid = {"name": "No Phone"}
    response = requests.post(f"{BASE_URL}/contacts", json=invalid)
    print_response(response, "POST /contacts (missing phone)")
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\nERROR: Cannot connect to API server")
        print("Please start the server first: python run_api.py")
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")