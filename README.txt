======================================================
  CHURCH WEBSITE – Python Flask Application
======================================================

ADMIN LOGIN
  URL:      http://localhost:5000/admin
  Username: Eugene
  Password: almighty

======================================================
QUICK START (Windows)
======================================================

1. Make sure Python 3.8+ is installed.
   Download from: https://python.org

2. Open Command Prompt (cmd) in this folder and run:

   python -m pip install -r requirements.txt

3. Start the website:

   python app.py

4. Open your browser and visit:
   http://localhost:5000

======================================================
QUICK START (Mac / Linux)
======================================================

1. Open Terminal in this folder and run:

   pip3 install -r requirements.txt

2. Start the website:

   python3 app.py

3. Open your browser:
   http://localhost:5000

======================================================
ADMIN PANEL FEATURES
======================================================

1. SITE SETTINGS
   - Change church name, tagline, welcome message
   - Upload website logo
   - Set theme colors (primary & accent)
   - Set contact info: address, phone, email
   - Set Google Maps location (Plus Code or address)
   - Add social media links
   - Change footer text

2. BACKGROUNDS
   - Upload multiple hero slideshow images
   - Show/hide individual backgrounds
   - Delete backgrounds

3. PASTORS
   - Add pastors with name, title, phone, email, bio, photo
   - Edit or delete pastors
   - Control display order

4. ELDERS
   - Same as pastors section

5. MEDIA (Photos & Videos)
   - Upload photos: JPG, PNG, GIF, WEBP
   - Upload videos: MP4, MOV, AVI, WEBM
   - Add captions and categories
   - Delete files

6. EVENTS CALENDAR
   - Add events with date, time, location, description
   - View calendar for current month
   - Events auto-appear on website

7. DESCRIPTION SECTIONS
   - Add text+image sections to About & Home pages
   - Control display order

8. ANNOUNCEMENTS
   - Add scrolling banner announcements
   - Toggle on/off

======================================================
GOOGLE MAPS LOCATION
======================================================

To update the church map location:
1. Log in to Admin → Site Settings
2. In "Map Location" field, enter:
   - A Google Plus Code (e.g. VP22+2EZC), OR
   - A full address (e.g. "123 Main St, Lagos, Nigeria")
3. Save settings

======================================================
FOLDERS
======================================================

church_website/
├── app.py              ← Main application file
├── requirements.txt    ← Python dependencies
├── church.db           ← Database (created automatically)
├── templates/          ← HTML templates
│   ├── base.html
│   ├── index.html
│   ├── about.html
│   ├── events.html
│   ├── gallery.html
│   ├── contact.html
│   └── admin/
│       ├── login.html
│       ├── dashboard.html
│       ├── settings.html
│       ├── backgrounds.html
│       ├── pastors.html
│       ├── elders.html
│       ├── media.html
│       ├── events.html
│       └── ...
└── static/
    └── uploads/
        ├── backgrounds/
        ├── logos/
        ├── pastors/
        ├── elders/
        ├── media/
        └── sections/

======================================================
MAKE IT ACCESSIBLE FROM OTHER DEVICES
======================================================

By default the site runs on: http://localhost:5000
It's already configured with host='0.0.0.0' so devices
on the same WiFi network can access it using your
computer's IP address: http://YOUR_IP_ADDRESS:5000

To find your IP:
  Windows: open cmd → type: ipconfig
  Mac/Linux: open terminal → type: ifconfig

For public internet access, consider:
  - PythonAnywhere (free): pythonanywhere.com
  - Railway: railway.app
  - Render: render.com

======================================================
