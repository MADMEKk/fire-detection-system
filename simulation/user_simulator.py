import requests
import time
import random
from datetime import datetime, timedelta
import threading
import json

class UserSimulator:
    def __init__(self):
        self.backend_url = "http://localhost:8000/api"
        self.regular_users = []  # rookie and guardian users
        self.ranked_users = []   # expert and master users
        self.response_times = {
            'rookie': (20, 40),    # 20-40 second response time
            'guardian': (15, 35),  # 15-35 second response time
            'expert': (5, 15),     # 5-15 second response time
            'master': (3, 10)      # 3-10 second response time
        }

    def create_test_users(self):
        """Create test users with different ranks"""
        ranks = [
            # rank, points, count
            ('rookie', 0, 5),
            ('guardian', 500, 5),
            ('expert', 1000, 3),
            ('master', 2000, 2)
        ]

        print("🧑‍🚒 Creating test users...")
        for rank, points, count in ranks:
            for i in range(count):
                username = f"{rank}_{i+1}"
                user_data = {
                    "username": username,
                    "guardian_points": points,
                    "rank": rank,
                    "is_available": True
                }

                try:
                    response = requests.post(f"{self.backend_url}/profile/", json=user_data)
                    if response.status_code == 201:
                        user = response.json()
                        if rank in ['expert', 'master']:
                            self.ranked_users.append(user)
                        else:
                            self.regular_users.append(user)
                        print(f"✅ Created {rank} user: {username} ({points} points)")
                except Exception as e:
                    print(f"❌ Error creating {username}: {e}")

    def simulate_user_behavior(self, user):
        """Simulate a user's verification behavior"""
        rank = user.get('rank', 'rookie')
        min_time, max_time = self.response_times[rank]
        
        while True:
            try:
                # Check for pending verifications
                response = requests.get(f"{self.backend_url}/fire-alerts/")
                if response.status_code == 200:
                    alerts = response.json()
                    
                    for alert in alerts:
                        if alert['status'] == 'pending':
                            # Simulate thinking time
                            response_time = random.uniform(min_time, max_time)
                            time.sleep(response_time)
                            
                            # Make verification decision
                            accuracy = 0.9 if rank in ['expert', 'master'] else 0.7
                            is_correct = random.random() < accuracy
                            
                            verification_data = {
                                "alert_id": alert['id'],
                                "user_id": user['id'],
                                "vote": is_correct
                            }
                            
                            try:
                                verify_response = requests.post(
                                    f"{self.backend_url}/verify-fire/",
                                    json=verification_data
                                )
                                
                                if verify_response.status_code == 200:
                                    result = verify_response.json()
                                    print(f"✨ {user['username']} verified alert {alert['id']}:")
                                    print(f"   Response time: {response_time:.1f}s")
                                    print(f"   Points earned: {result['points_earned']}")
                                    print(f"   New total: {result['new_total_points']}")
                            except:
                                pass
                
                time.sleep(1)  # Check for new alerts every second
                
            except KeyboardInterrupt:
                break
            except:
                time.sleep(5)  # Wait on error

    def run(self):
        """Run the user simulation"""
        print("\n🚀 Starting Fire Detection User Simulation")
        print("----------------------------------------")
        self.create_test_users()
        
        print("\n👥 Starting user behaviors...")
        threads = []
        
        # Start threads for each user
        for user in self.regular_users + self.ranked_users:
            thread = threading.Thread(
                target=self.simulate_user_behavior,
                args=(user,),
                daemon=True
            )
            thread.start()
            threads.append(thread)
            print(f"▶️  Started {user['username']} simulation")
        
        print("\n✅ All users are now monitoring for alerts")
        print("Press Ctrl+C to stop the simulation\n")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Stopping user simulation...")

if __name__ == "__main__":
    simulator = UserSimulator()
    simulator.run()
