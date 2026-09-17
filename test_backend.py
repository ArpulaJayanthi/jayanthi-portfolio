"""
Automated backend verification test suite for Jayanthi's Full-Stack Portfolio.
Tests all RESTful endpoints, database updates, and data structures.
"""

from fastapi.testclient import TestClient
from app import app
import database

client = TestClient(app)

def test_api_suite():
    print("[TEST] Running Full-Stack Portfolio Backend Tests...")
    
    # 1. Test Profile Endpoint
    response = client.get("/api/profile")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    profile_data = response.json()
    assert profile_data["name"] == "Jayanthi"
    assert "Cyber Security" in profile_data["headline"]
    print("  [OK] /api/profile PASSED")
    
    # 2. Test Projects Endpoint (all)
    response = client.get("/api/projects")
    assert response.status_code == 200
    projects_data = response.json()
    assert projects_data["count"] >= 6
    first_project = projects_data["projects"][0]
    first_id = first_project["id"]
    initial_likes = first_project["likes"]
    print(f"  [OK] /api/projects PASSED (Found {projects_data['count']} projects)")
    
    # 3. Test Project Filter and Search
    response = client.get("/api/projects?category=Cyber%20Security")
    assert response.status_code == 200
    cyber_projects = response.json()["projects"]
    assert len(cyber_projects) > 0
    assert any("Cyber" in p["category"] for p in cyber_projects)
    print(f"  [OK] /api/projects filter by category PASSED")

    response = client.get("/api/projects?search=Spring")
    assert response.status_code == 200
    spring_projects = response.json()["projects"]
    assert len(spring_projects) > 0
    print(f"  [OK] /api/projects search keyword PASSED")
    
    # 4. Test Project Like Increment
    response = client.post(f"/api/projects/{first_id}/like")
    assert response.status_code == 200
    like_res = response.json()
    assert like_res["likes"] == initial_likes + 1
    print(f"  [OK] /api/projects/{first_id}/like PASSED (Likes: {initial_likes} -> {like_res['likes']})")
    
    # 5. Test Skills Endpoint
    response = client.get("/api/skills")
    assert response.status_code == 200
    skills_data = response.json()
    assert skills_data["total"] == 5
    assert any("Java" in s["name"] for s in skills_data["skills"])
    assert any("Python" in s["name"] for s in skills_data["skills"])
    assert any("Cyber" in s["name"] for s in skills_data["skills"])
    first_skill = skills_data["skills"][0]
    skill_id = first_skill["id"]
    initial_endorsements = first_skill["endorsements"]
    print(f"  [OK] /api/skills PASSED (Found {skills_data['total']} core skills in {len(skills_data['categories'])} categories)")
    
    # 6. Test Skill Endorsement
    response = client.post(f"/api/skills/{skill_id}/endorse")
    assert response.status_code == 200
    endorse_res = response.json()
    assert endorse_res["endorsements"] == initial_endorsements + 1
    print(f"  [OK] /api/skills/{skill_id}/endorse PASSED")
    
    # 7. Test Contact Form Submission
    test_contact = {
        "name": "Sarah Connor",
        "email": "sarah.connor@cyberdyne.org",
        "subject": "Cyber Security Internship",
        "message": "Hi Jayanthi, we are impressed with your security projects and would like to talk."
    }
    response = client.post("/api/contact", json=test_contact)
    assert response.status_code == 201
    contact_res = response.json()
    assert contact_res["success"] is True
    new_msg_id = contact_res["message_id"]
    print(f"  [OK] /api/contact PASSED (Created message ID: {new_msg_id})")
    
    # 8. Test Admin Messages Listing
    response = client.get("/api/admin/messages")
    assert response.status_code == 200
    admin_msgs = response.json()["messages"]
    found_msg = next((m for m in admin_msgs if m["id"] == new_msg_id), None)
    assert found_msg is not None
    assert found_msg["name"] == "Sarah Connor"
    print(f"  [OK] /api/admin/messages PASSED (Inbox contains {len(admin_msgs)} messages)")
    
    # 9. Test Delete Message
    response = client.delete(f"/api/admin/messages/{new_msg_id}")
    assert response.status_code == 200
    assert response.json()["success"] is True
    print(f"  [OK] /api/admin/messages/{new_msg_id} DELETE PASSED")
    
    # 10. Test Analytics / Stats & Visit
    response = client.get("/api/stats")
    assert response.status_code == 200
    stats = response.json()
    assert "total_visits" in stats
    
    response = client.post("/api/stats/visit")
    assert response.status_code == 200
    assert response.json()["visits"] >= stats["total_visits"]
    print(f"  [OK] /api/stats and /api/stats/visit PASSED")
    
    print("\nSUCCESS: ALL BACKEND TESTS PASSED!")

if __name__ == "__main__":
    test_api_suite()
