# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.

"""

Load testing with locust.
Usage: locust -f locustfile.py --host=http://localhost:5000
Then open: https://localhost:8089
"""

from locust import HttpLocust, task, between, HttpUser
import random


class AutomUser(HttpUser):
    """Simulate user behavior for load testing."""

    # Wait 1-3 seconds between tasks
    wait_time = between(1, 3)
    
    # Store IDs discovered or created during the test
    discovered_ids = set()

    def on_start(self):
        """Called when a simulated user starts."""
        self.refresh_ids()

    def refresh_ids(self):
        """Fetch the latest contact IDs from the API."""
        response = self.client.get("/api/v1/contacts?limit=100")
        if response.status_code == 200:
            contacts = response.json()
            # Handle both list and paginated dict response
            if isinstance(contacts, dict) and "contacts" in contacts:
                contacts = contacts["contacts"]
            
            if isinstance(contacts, list):
                for c in contacts:
                    self.discovered_ids.add(c["id"])

    @task(10)
    def get_health(self):
        """Health check endpoint."""
        self.client.get("/api/v1/health")

    @task(5)
    def get_contacts(self):
        """Get all contacts and refresh internal list."""
        self.refresh_ids()

    @task(5)
    def create_contact(self):
        """Create a new contact and store its ID."""
        contact_data = {
            "name": f"User {random.randint(1, 10000)}",
            "phone": f"070{random.randint(1000000, 9999999)}",
        }
        with self.client.post("/api/v1/contacts", json=contact_data, catch_response=True) as response:
            if response.status_code == 201:
                new_id = response.json().get("id")
                if new_id:
                    self.discovered_ids.add(new_id)
            elif response.status_code == 409:
                response.success()  # Duplicates are expected in stress tests

    @task(3)
    def get_specific_contact(self):
        """Get a specific discovered contact."""
        if not self.discovered_ids:
            return
        
        contact_id = random.choice(list(self.discovered_ids))
        self.client.get(f"/api/v1/contacts/{contact_id}")

    @task(1)
    def delete_contact(self):
        """Delete a contact and remove from internal list."""
        if not self.discovered_ids:
            return
            
        contact_id = random.choice(list(self.discovered_ids))
        with self.client.delete(f"/api/v1/contacts/{contact_id}", catch_response=True) as response:
            if response.status_code == 200:
                self.discovered_ids.discard(contact_id)
            elif response.status_code == 404:
                # Might have been deleted by another user, that's okay
                self.discovered_ids.discard(contact_id)
                response.success()

    @task(5)
    def get_metrics(self):
        """Get system metrics."""
        self.client.get("/api/v1/metrics")

    @task(3)
    def get_performance_stats(self):
        """Get performance statistics."""
        self.client.get("/api/v1/performance/stats")


class AdminUser(HttpUser):
    """Simulate admin user with heavier operations."""

    wait_time = between(2, 5)

    @task(5)
    def view_all_contacts(self):
        """Admin views all contacts."""
        self.client.get("/api/v1/contacts")

    @task(3)
    def check_system_health(self):
        """Admin checks system health."""
        self.client.get("/api/v1/performance/health")

    @task(1)
    def bulk_create_contacts(self):
        """Admin bulk creates contacts."""
        for i in range(5):  # Reduced from 10 to be slightly kinder to the DB
            contact_data = {
                "name": f"Bulk User {i}_{random.randint(1, 1000)}",
                "phone": f"071{random.randint(1000000, 9999999)}",
            }
            self.client.post("/api/v1/contacts", json=contact_data)
