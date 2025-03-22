# Raspberry Pi Fire Detection Setup

This guide will help you set up the fire detection system on your Raspberry Pi.

## Hardware Requirements
- Raspberry Pi (3 or newer recommended)
- Raspberry Pi Camera Module
- Power supply
- (Optional) Display for debugging

## Installation Steps

1. **Enable Camera Interface**
   ```bash
   sudo raspi-config
   # Navigate to Interface Options > Camera > Enable
   ```

2. **Install System Dependencies**
   ```bash
   sudo apt update
   sudo apt install -y python3-pip python3-opencv libcamera-dev
   ```

3. **Install Python Dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

4. **Download YOLO Model**
   - Place your trained YOLO model (`fire_m.pt`) in the same directory as `fire_detector.py`

5. **Configure the Script**
   - Open `fire_detector.py`
   - Update the following variables:
     - `backend_url`: Your backend server URL
     - `latitude` and `longitude`: Your camera's location coordinates

## Running the Detection System

1. **Start the detector**
   ```bash
   python3 fire_detector.py
   ```

2. **Run on Startup (Optional)**
   To make the detector start automatically when the Raspberry Pi boots:

   ```bash
   sudo nano /etc/systemd/system/fire_detector.service
   ```

   Add the following content:
   ```ini
   [Unit]
   Description=Fire Detection Service
   After=network.target

   [Service]
   ExecStart=/usr/bin/python3 /path/to/fire_detector.py
   WorkingDirectory=/path/to/directory
   StandardOutput=inherit
   StandardError=inherit
   Restart=always
   User=pi

   [Install]
   WantedBy=multi-user.target
   ```

   Then enable and start the service:
   ```bash
   sudo systemctl enable fire_detector
   sudo systemctl start fire_detector
   ```

## Monitoring

- Check the captured_images directory for detected fire images
- Monitor the console output for detection status
- Check system logs for service status:
  ```bash
  sudo journalctl -u fire_detector -f
  ```

## Troubleshooting

1. **Camera Issues**
   - Check if camera is properly connected
   - Verify camera is enabled in raspi-config
   - Test camera with `libcamera-still -o test.jpg`

2. **Network Issues**
   - Verify internet connection
   - Check backend URL is correct
   - Ensure firewall allows outgoing connections

3. **Detection Issues**
   - Verify YOLO model file exists
   - Check console for error messages
   - Verify camera is properly positioned and clean
