# 🔥 Real-Time Fire Detection System

A sophisticated fire detection system using computer vision and a community-driven verification approach to detect and verify fire incidents in real-time.

## 🌟 Features

### 1. Fire Detection
- Real-time fire and smoke detection using YOLO model
- Confidence-based detection (threshold: 50%)
- Automatic image annotation showing detection boxes
- Support for both Raspberry Pi camera and laptop webcam

### 2. Three-Wave Verification System
1. **First Wave (30s)**
   - Sends alerts to 5 random rookie/guardian users
   - Moves to second wave if no response in 30s

2. **Second Wave (30s)**
   - Sends to 5 new random rookie/guardian users
   - Escalates to final wave if no response in 30s

3. **Final Wave**
   - Sends to all expert/master ranked users
   - Higher verification priority and points

### 3. User Ranking System
- **Rookie**: New users (0-499 points)
- **Guardian**: Regular users (500-999 points)
- **Expert**: Experienced users (1000-1999 points)
- **Master**: Elite users (2000+ points)

### 4. Points System
- Base points per verification:
  - Regular users: 10 points
  - Ranked users (Expert/Master): 20 points
- Speed bonus: Up to 30 points based on response time
- Alert verification requires 3 votes
- Alert confirmed if 2+ votes are positive

## 📡 API Endpoints

### Camera Management
```http
POST /api/cameras/
```
- Register a new camera in the system
- **Body**: 
  ```json
  {
    "name": "string",
    "location_name": "string",
    "latitude": "float",
    "longitude": "float"
  }
  ```
- **Response**: Camera details with ID

```http
GET /api/cameras/
```
- List all registered cameras
- **Response**: Array of camera objects

### Fire Alerts
```http
POST /api/fire-alerts/
```
- Submit a new fire alert
- **Body**: 
  ```json
  {
    "camera_id": "integer",
    "image": "file",
    "latitude": "float",
    "longitude": "float",
    "fire_size": "string (small/medium/large)"
  }
  ```
- **Response**: Alert details with verification status

```http
GET /api/fire-alerts/
```
- List all fire alerts
- **Query Parameters**:
  - `status`: Filter by status (pending/confirmed/false_alarm)
  - `camera_id`: Filter by camera
- **Response**: Array of fire alerts

### User Management
```http
POST /api/profile/
```
- Create a new user profile
- **Body**:
  ```json
  {
    "username": "string",
    "guardian_points": "integer",
    "rank": "string (rookie/guardian/expert/master)",
    "is_available": "boolean"
  }
  ```
- **Response**: User profile details

```http
GET /api/profile/
```
- List all user profiles
- **Query Parameters**:
  - `rank`: Filter by rank
  - `is_available`: Filter by availability
- **Response**: Array of user profiles

### Alert Verification
```http
POST /api/verify-fire/
```
- Submit a verification vote for a fire alert
- **Body**:
  ```json
  {
    "alert_id": "integer",
    "user_id": "integer",
    "vote": "boolean"
  }
  ```
- **Response**:
  ```json
  {
    "status": "success/error",
    "points_earned": "integer",
    "new_total_points": "integer"
  }
  ```

### Response Status Codes
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `404`: Not Found
- `500`: Server Error

## 🛠️ Technical Stack

### Backend (Django)
- Django REST Framework for API
- PostgreSQL database
- Authentication and permission system
- Real-time alert processing
- User management and ranking system

### Fire Detection
- YOLO model (fire_s.pt) for detection
- OpenCV for image processing
- Support for multiple camera types
- Real-time image annotation

### Simulation Tools
1. **Camera Simulator** (`camera_simulator.py`)
   - Uses laptop webcam for testing
   - Real-time fire detection
   - Automatic alert generation

2. **User Simulator** (`user_simulator.py`)
   - Simulates user behavior with different ranks
   - Realistic response times based on rank
   - Automatic verification decisions
   - Multi-threaded user simulation

## 🚀 Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start Django server:
   ```bash
   python manage.py runserver
   ```

3. Run simulations:
   ```bash
   cd simulation
   ./run_simulation.sh
   ```

## 📁 Project Structure

### Core Components
- `fire_detection_app/`: Main Django application
  - `views.py`: API endpoints and business logic
  - `models.py`: Database models
  - `urls.py`: URL routing

### Simulation Tools
- `simulation/`: Testing and simulation tools
  - `camera_simulator.py`: Fire detection simulation
  - `user_simulator.py`: User behavior simulation
  - `run_simulation.sh`: Automated test script

## 🔒 Security Features
- Secure API endpoints
- User authentication system
- Rate limiting for verifications
- Timeout system for alerts
- Ranked user verification system

## 🎯 Use Cases

1. **Fire Detection**
   - Continuous monitoring via camera
   - Real-time detection using YOLO
   - Automatic alert generation

2. **Alert Verification**
   - Three-wave verification system
   - Community-driven verification
   - Ranked user escalation

3. **User Management**
   - Point-based ranking system
   - Performance tracking
   - Response time monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License.
