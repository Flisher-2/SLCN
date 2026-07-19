#!/usr/bin/env python3
"""
Church Website - Flask Application
Admin: Username=Eugene, Password=almighty
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import json

app = Flask(__name__)
app.secret_key = 'church_secret_key_almighty_2024'

# ─── Database Config ───────────────────────────────────────────────
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'church.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ─── Upload Config ─────────────────────────────────────────────────
UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
ALLOWED_IMAGE = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'}
ALLOWED_VIDEO = {'mp4', 'webm', 'ogg', 'mov', 'avi', 'mkv'}
ALLOWED_ALL   = ALLOWED_IMAGE | ALLOWED_VIDEO
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024   # 500 MB

db = SQLAlchemy(app)

# ─── Models ────────────────────────────────────────────────────────

class SiteSettings(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    key         = db.Column(db.String(100), unique=True, nullable=False)
    value       = db.Column(db.Text, default='')

class Background(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    filename    = db.Column(db.String(255), nullable=False)
    label       = db.Column(db.String(100), default='')
    active      = db.Column(db.Boolean, default=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

class Pastor(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(150), nullable=False)
    title       = db.Column(db.String(100), default='Pastor')
    phone       = db.Column(db.String(50), default='')
    email       = db.Column(db.String(150), default='')
    bio         = db.Column(db.Text, default='')
    photo       = db.Column(db.String(255), default='')
    order_num   = db.Column(db.Integer, default=0)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

class Elder(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(150), nullable=False)
    title       = db.Column(db.String(100), default='Elder')
    phone       = db.Column(db.String(50), default='')
    email       = db.Column(db.String(150), default='')
    bio         = db.Column(db.Text, default='')
    photo       = db.Column(db.String(255), default='')
    order_num   = db.Column(db.Integer, default=0)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

class MediaItem(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    filename    = db.Column(db.String(255), nullable=False)
    media_type  = db.Column(db.String(10), default='image')   # 'image' | 'video'
    caption     = db.Column(db.String(255), default='')
    category    = db.Column(db.String(100), default='Service')
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

class Event(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    event_date  = db.Column(db.Date, nullable=False)
    event_time  = db.Column(db.String(20), default='')
    location    = db.Column(db.String(200), default='')
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

class DescriptionSection(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(200), default='')
    body        = db.Column(db.Text, default='')
    image       = db.Column(db.String(255), default='')
    order_num   = db.Column(db.Integer, default=0)

class Announcement(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    text        = db.Column(db.Text, nullable=False)
    active      = db.Column(db.Boolean, default=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

# ─── Helpers ───────────────────────────────────────────────────────

def allowed_file(filename, allowed):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed

def save_upload(file, subfolder, allowed):
    """Save uploaded file, return relative path or None."""
    if not file or file.filename == '':
        return None
    if not allowed_file(file.filename, allowed):
        return None
    fname = secure_filename(file.filename)
    # Add timestamp to avoid collisions
    base, ext = os.path.splitext(fname)
    fname = f"{base}_{int(datetime.utcnow().timestamp())}{ext}"
    dest = os.path.join(app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(dest, exist_ok=True)
    file.save(os.path.join(dest, fname))
    return f"uploads/{subfolder}/{fname}"

def get_setting(key, default=''):
    s = SiteSettings.query.filter_by(key=key).first()
    return s.value if s else default

def set_setting(key, value):
    s = SiteSettings.query.filter_by(key=key).first()
    if s:
        s.value = value
    else:
        s = SiteSettings(key=key, value=value)
        db.session.add(s)
    db.session.commit()

def is_admin():
    return session.get('admin_logged_in') is True

# ─── Context Processor ─────────────────────────────────────────────

@app.context_processor
def inject_globals():
    logo       = get_setting('logo', '')
    church_name= get_setting('church_name', 'Grace Community Church')
    tagline    = get_setting('tagline', 'A Place of Love, Faith & Community')
    theme_color= get_setting('theme_color', '#7c3aed')
    accent_color=get_setting('accent_color', '#f59e0b')
    bg_list    = Background.query.filter_by(active=True).order_by(Background.id.desc()).all()
    announcements = Announcement.query.filter_by(active=True).order_by(Announcement.created_at.desc()).all()
    return dict(
        LOGO=logo,
        CHURCH_NAME=church_name,
        TAGLINE=tagline,
        THEME_COLOR=theme_color,
        ACCENT_COLOR=accent_color,
        BG_LIST=bg_list,
        SITE_ANNOUNCEMENTS=announcements,
        IS_ADMIN=is_admin(),
        get_setting=get_setting,          # expose helper to all templates
    )

# ─── Public Routes ──────────────────────────────────────────────────

@app.route('/')
def index():
    pastors   = Pastor.query.order_by(Pastor.order_num, Pastor.id).all()
    elders    = Elder.query.order_by(Elder.order_num, Elder.id).all()
    images    = MediaItem.query.filter_by(media_type='image').order_by(MediaItem.created_at.desc()).limit(12).all()
    videos    = MediaItem.query.filter_by(media_type='video').order_by(MediaItem.created_at.desc()).limit(6).all()
    today     = datetime.utcnow().date()
    events    = Event.query.filter(Event.event_date >= today).order_by(Event.event_date).limit(6).all()
    sections  = DescriptionSection.query.order_by(DescriptionSection.order_num).all()
    map_code  = get_setting('map_location', 'VP22+2EZC')
    service_times = get_setting('service_times', 'Sunday: 9:00 AM & 11:00 AM\nWednesday: 7:00 PM')
    welcome_msg   = get_setting('welcome_message', 'Welcome to our Church Family! We are glad you are here.')
    return render_template('index.html',
        pastors=pastors, elders=elders, images=images, videos=videos,
        events=events, sections=sections, map_code=map_code,
        service_times=service_times, welcome_msg=welcome_msg)

@app.route('/gallery')
def gallery():
    media = MediaItem.query.order_by(MediaItem.created_at.desc()).all()
    return render_template('gallery.html', media=media)

@app.route('/events')
def events():
    today  = datetime.utcnow().date()
    upcoming = Event.query.filter(Event.event_date >= today).order_by(Event.event_date).all()
    past     = Event.query.filter(Event.event_date < today).order_by(Event.event_date.desc()).all()
    return render_template('events.html', upcoming=upcoming, past=past)

@app.route('/about')
def about():
    pastors  = Pastor.query.order_by(Pastor.order_num, Pastor.id).all()
    elders   = Elder.query.order_by(Elder.order_num, Elder.id).all()
    sections = DescriptionSection.query.order_by(DescriptionSection.order_num).all()
    return render_template('about.html', pastors=pastors, elders=elders, sections=sections)

@app.route('/contact')
def contact():
    map_code  = get_setting('map_location', 'VP22+2EZC')
    address   = get_setting('address', '')
    phone     = get_setting('contact_phone', '')
    email     = get_setting('contact_email', '')
    return render_template('contact.html', map_code=map_code, address=address, phone=phone, email=email)

# ─── Admin Login ───────────────────────────────────────────────────

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if is_admin():
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username == 'Eugene' and password == 'almighty':
            session['admin_logged_in'] = True
            flash('Welcome back, Eugene!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# ─── Admin Dashboard ───────────────────────────────────────────────

@app.route('/admin/dashboard')
def admin_dashboard():
    if not is_admin():
        return redirect(url_for('admin_login'))
    stats = {
        'pastors': Pastor.query.count(),
        'elders': Elder.query.count(),
        'media': MediaItem.query.count(),
        'events': Event.query.count(),
        'backgrounds': Background.query.count(),
    }
    recent_events = Event.query.order_by(Event.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats, recent_events=recent_events)

# ─── Admin: Site Settings ──────────────────────────────────────────

@app.route('/admin/settings', methods=['GET', 'POST'])
def admin_settings():
    if not is_admin():
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        for key in ['church_name','tagline','welcome_message','service_times',
                    'address','contact_phone','contact_email','map_location',
                    'theme_color','accent_color','facebook_url','youtube_url',
                    'instagram_url','twitter_url','footer_text']:
            set_setting(key, request.form.get(key, ''))
        # Logo upload
        logo_file = request.files.get('logo')
        path = save_upload(logo_file, 'logos', ALLOWED_IMAGE)
        if path:
            set_setting('logo', path)
        flash('Settings saved successfully!', 'success')
        return redirect(url_for('admin_settings'))
    settings = {
        'church_name': get_setting('church_name','Grace Community Church'),
        'tagline': get_setting('tagline','A Place of Love, Faith & Community'),
        'welcome_message': get_setting('welcome_message','Welcome to our Church Family!'),
        'service_times': get_setting('service_times','Sunday: 9:00 AM & 11:00 AM\nWednesday: 7:00 PM'),
        'address': get_setting('address',''),
        'contact_phone': get_setting('contact_phone',''),
        'contact_email': get_setting('contact_email',''),
        'map_location': get_setting('map_location','VP22+2EZC'),
        'theme_color': get_setting('theme_color','#7c3aed'),
        'accent_color': get_setting('accent_color','#f59e0b'),
        'facebook_url': get_setting('facebook_url',''),
        'youtube_url': get_setting('youtube_url',''),
        'instagram_url': get_setting('instagram_url',''),
        'twitter_url': get_setting('twitter_url',''),
        'footer_text': get_setting('footer_text',''),
        'logo': get_setting('logo',''),
    }
    return render_template('admin/settings.html', settings=settings)

# ─── Admin: Backgrounds ────────────────────────────────────────────

@app.route('/admin/backgrounds', methods=['GET', 'POST'])
def admin_backgrounds():
    if not is_admin():
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        files = request.files.getlist('backgrounds')
        label = request.form.get('label', '')
        count = 0
        for f in files:
            path = save_upload(f, 'backgrounds', ALLOWED_IMAGE)
            if path:
                db.session.add(Background(filename=path, label=label))
                count += 1
        db.session.commit()
        flash(f'{count} background(s) uploaded!', 'success')
        return redirect(url_for('admin_backgrounds'))
    bgs = Background.query.order_by(Background.created_at.desc()).all()
    return render_template('admin/backgrounds.html', bgs=bgs)

@app.route('/admin/backgrounds/delete/<int:bg_id>')
def delete_background(bg_id):
    if not is_admin(): return redirect(url_for('admin_login'))
    bg = Background.query.get_or_404(bg_id)
    db.session.delete(bg)
    db.session.commit()
    flash('Background deleted.', 'success')
    return redirect(url_for('admin_backgrounds'))

@app.route('/admin/backgrounds/toggle/<int:bg_id>')
def toggle_background(bg_id):
    if not is_admin(): return redirect(url_for('admin_login'))
    bg = Background.query.get_or_404(bg_id)
    bg.active = not bg.active
    db.session.commit()
    return redirect(url_for('admin_backgrounds'))

# ─── Admin: Pastors ────────────────────────────────────────────────

@app.route('/admin/pastors', methods=['GET', 'POST'])
def admin_pastors():
    if not is_admin():
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        photo_path = save_upload(request.files.get('photo'), 'pastors', ALLOWED_IMAGE) or ''
        p = Pastor(
            name=request.form.get('name',''),
            title=request.form.get('title','Pastor'),
            phone=request.form.get('phone',''),
            email=request.form.get('email',''),
            bio=request.form.get('bio',''),
            photo=photo_path,
            order_num=int(request.form.get('order_num', 0) or 0),
        )
        db.session.add(p)
        db.session.commit()
        flash('Pastor added!', 'success')
        return redirect(url_for('admin_pastors'))
    pastors = Pastor.query.order_by(Pastor.order_num, Pastor.id).all()
    return render_template('admin/pastors.html', pastors=pastors)

@app.route('/admin/pastors/edit/<int:pid>', methods=['GET', 'POST'])
def edit_pastor(pid):
    if not is_admin(): return redirect(url_for('admin_login'))
    p = Pastor.query.get_or_404(pid)
    if request.method == 'POST':
        p.name      = request.form.get('name', p.name)
        p.title     = request.form.get('title', p.title)
        p.phone     = request.form.get('phone', p.phone)
        p.email     = request.form.get('email', p.email)
        p.bio       = request.form.get('bio', p.bio)
        p.order_num = int(request.form.get('order_num', p.order_num) or 0)
        new_photo   = save_upload(request.files.get('photo'), 'pastors', ALLOWED_IMAGE)
        if new_photo:
            p.photo = new_photo
        db.session.commit()
        flash('Pastor updated!', 'success')
        return redirect(url_for('admin_pastors'))
    return render_template('admin/edit_pastor.html', pastor=p)

@app.route('/admin/pastors/delete/<int:pid>')
def delete_pastor(pid):
    if not is_admin(): return redirect(url_for('admin_login'))
    db.session.delete(Pastor.query.get_or_404(pid))
    db.session.commit()
    flash('Pastor deleted.', 'success')
    return redirect(url_for('admin_pastors'))

# ─── Admin: Elders ─────────────────────────────────────────────────

@app.route('/admin/elders', methods=['GET', 'POST'])
def admin_elders():
    if not is_admin():
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        photo_path = save_upload(request.files.get('photo'), 'elders', ALLOWED_IMAGE) or ''
        e = Elder(
            name=request.form.get('name',''),
            title=request.form.get('title','Elder'),
            phone=request.form.get('phone',''),
            email=request.form.get('email',''),
            bio=request.form.get('bio',''),
            photo=photo_path,
            order_num=int(request.form.get('order_num', 0) or 0),
        )
        db.session.add(e)
        db.session.commit()
        flash('Elder added!', 'success')
        return redirect(url_for('admin_elders'))
    elders = Elder.query.order_by(Elder.order_num, Elder.id).all()
    return render_template('admin/elders.html', elders=elders)

@app.route('/admin/elders/edit/<int:eid>', methods=['GET', 'POST'])
def edit_elder(eid):
    if not is_admin(): return redirect(url_for('admin_login'))
    e = Elder.query.get_or_404(eid)
    if request.method == 'POST':
        e.name      = request.form.get('name', e.name)
        e.title     = request.form.get('title', e.title)
        e.phone     = request.form.get('phone', e.phone)
        e.email     = request.form.get('email', e.email)
        e.bio       = request.form.get('bio', e.bio)
        e.order_num = int(request.form.get('order_num', e.order_num) or 0)
        new_photo   = save_upload(request.files.get('photo'), 'elders', ALLOWED_IMAGE)
        if new_photo:
            e.photo = new_photo
        db.session.commit()
        flash('Elder updated!', 'success')
        return redirect(url_for('admin_elders'))
    return render_template('admin/edit_elder.html', elder=e)

@app.route('/admin/elders/delete/<int:eid>')
def delete_elder(eid):
    if not is_admin(): return redirect(url_for('admin_login'))
    db.session.delete(Elder.query.get_or_404(eid))
    db.session.commit()
    flash('Elder deleted.', 'success')
    return redirect(url_for('admin_elders'))

# ─── Admin: Media ──────────────────────────────────────────────────

@app.route('/admin/media', methods=['GET', 'POST'])
def admin_media():
    if not is_admin():
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        files    = request.files.getlist('media_files')
        caption  = request.form.get('caption', '')
        category = request.form.get('category', 'Service')
        count = 0
        for f in files:
            ext = f.filename.rsplit('.', 1)[-1].lower() if '.' in f.filename else ''
            if ext in ALLOWED_IMAGE:
                path = save_upload(f, 'media', ALLOWED_IMAGE)
                mtype = 'image'
            elif ext in ALLOWED_VIDEO:
                path = save_upload(f, 'media', ALLOWED_VIDEO)
                mtype = 'video'
            else:
                path = None
                mtype = None
            if path:
                db.session.add(MediaItem(filename=path, media_type=mtype, caption=caption, category=category))
                count += 1
        db.session.commit()
        flash(f'{count} file(s) uploaded!', 'success')
        return redirect(url_for('admin_media'))
    media = MediaItem.query.order_by(MediaItem.created_at.desc()).all()
    return render_template('admin/media.html', media=media)

@app.route('/admin/media/delete/<int:mid>')
def delete_media(mid):
    if not is_admin(): return redirect(url_for('admin_login'))
    m = MediaItem.query.get_or_404(mid)
    # Try to remove file
    try:
        fp = os.path.join(basedir, 'static', m.filename)
        if os.path.exists(fp):
            os.remove(fp)
    except Exception:
        pass
    db.session.delete(m)
    db.session.commit()
    flash('Media deleted.', 'success')
    return redirect(url_for('admin_media'))

# ─── Admin: Events ─────────────────────────────────────────────────

@app.route('/admin/events', methods=['GET', 'POST'])
def admin_events():
    if not is_admin():
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        date_str = request.form.get('event_date', '')
        try:
            ev_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'error')
            return redirect(url_for('admin_events'))
        ev = Event(
            title=request.form.get('title', ''),
            description=request.form.get('description', ''),
            event_date=ev_date,
            event_time=request.form.get('event_time', ''),
            location=request.form.get('location', ''),
        )
        db.session.add(ev)
        db.session.commit()
        flash('Event added!', 'success')
        return redirect(url_for('admin_events'))
    today = datetime.utcnow().date()
    upcoming = Event.query.filter(Event.event_date >= today).order_by(Event.event_date).all()
    past     = Event.query.filter(Event.event_date < today).order_by(Event.event_date.desc()).all()
    return render_template('admin/events.html', upcoming=upcoming, past=past)

@app.route('/admin/events/edit/<int:eid>', methods=['GET', 'POST'])
def edit_event(eid):
    if not is_admin(): return redirect(url_for('admin_login'))
    ev = Event.query.get_or_404(eid)
    if request.method == 'POST':
        ev.title       = request.form.get('title', ev.title)
        ev.description = request.form.get('description', ev.description)
        ev.event_time  = request.form.get('event_time', ev.event_time)
        ev.location    = request.form.get('location', ev.location)
        date_str = request.form.get('event_date', '')
        try:
            ev.event_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            pass
        db.session.commit()
        flash('Event updated!', 'success')
        return redirect(url_for('admin_events'))
    return render_template('admin/edit_event.html', event=ev)

@app.route('/admin/events/delete/<int:eid>')
def delete_event(eid):
    if not is_admin(): return redirect(url_for('admin_login'))
    db.session.delete(Event.query.get_or_404(eid))
    db.session.commit()
    flash('Event deleted.', 'success')
    return redirect(url_for('admin_events'))

# ─── Admin: Description Sections ──────────────────────────────────

@app.route('/admin/sections', methods=['GET', 'POST'])
def admin_sections():
    if not is_admin():
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        img_path = save_upload(request.files.get('image'), 'sections', ALLOWED_IMAGE) or ''
        s = DescriptionSection(
            title=request.form.get('title',''),
            body=request.form.get('body',''),
            image=img_path,
            order_num=int(request.form.get('order_num', 0) or 0),
        )
        db.session.add(s)
        db.session.commit()
        flash('Section added!', 'success')
        return redirect(url_for('admin_sections'))
    sections = DescriptionSection.query.order_by(DescriptionSection.order_num).all()
    return render_template('admin/sections.html', sections=sections)

@app.route('/admin/sections/edit/<int:sid>', methods=['GET', 'POST'])
def edit_section(sid):
    if not is_admin(): return redirect(url_for('admin_login'))
    s = DescriptionSection.query.get_or_404(sid)
    if request.method == 'POST':
        s.title     = request.form.get('title', s.title)
        s.body      = request.form.get('body', s.body)
        s.order_num = int(request.form.get('order_num', s.order_num) or 0)
        new_img     = save_upload(request.files.get('image'), 'sections', ALLOWED_IMAGE)
        if new_img:
            s.image = new_img
        db.session.commit()
        flash('Section updated!', 'success')
        return redirect(url_for('admin_sections'))
    return render_template('admin/edit_section.html', section=s)

@app.route('/admin/sections/delete/<int:sid>')
def delete_section(sid):
    if not is_admin(): return redirect(url_for('admin_login'))
    db.session.delete(DescriptionSection.query.get_or_404(sid))
    db.session.commit()
    flash('Section deleted.', 'success')
    return redirect(url_for('admin_sections'))

# ─── Admin: Announcements ──────────────────────────────────────────

@app.route('/admin/announcements', methods=['GET', 'POST'])
def admin_announcements():
    if not is_admin():
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        a = Announcement(text=request.form.get('text',''))
        db.session.add(a)
        db.session.commit()
        flash('Announcement added!', 'success')
        return redirect(url_for('admin_announcements'))
    ann = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template('admin/announcements.html', announcements=ann)

@app.route('/admin/announcements/delete/<int:aid>')
def delete_announcement(aid):
    if not is_admin(): return redirect(url_for('admin_login'))
    db.session.delete(Announcement.query.get_or_404(aid))
    db.session.commit()
    flash('Announcement deleted.', 'success')
    return redirect(url_for('admin_announcements'))

@app.route('/admin/announcements/toggle/<int:aid>')
def toggle_announcement(aid):
    if not is_admin(): return redirect(url_for('admin_login'))
    a = Announcement.query.get_or_404(aid)
    a.active = not a.active
    db.session.commit()
    return redirect(url_for('admin_announcements'))

# ─── Serve uploaded files ──────────────────────────────────────────

@app.route('/static/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join(basedir, 'static', 'uploads'), filename)

# ─── Init DB & Run ─────────────────────────────────────────────────

def init_db():
    db.create_all()
    # Default settings
    defaults = {
        'church_name': 'Grace Community Church',
        'tagline': 'A Place of Love, Faith & Community',
        'welcome_message': 'Welcome to our Church Family! We are so glad you found us. Join us as we grow together in faith, love, and community.',
        'service_times': 'Sunday Morning: 9:00 AM & 11:00 AM\nWednesday Evening: 7:00 PM\nFriday Prayer: 6:00 PM',
        'address': '123 Church Street, Your City',
        'contact_phone': '+1 (555) 000-0000',
        'contact_email': 'info@gracechurch.org',
        'map_location': 'VP22+2EZC',
        'theme_color': '#7c3aed',
        'accent_color': '#f59e0b',
        'footer_text': '© 2024 Grace Community Church. All rights reserved.',
        'facebook_url': '',
        'youtube_url': '',
        'instagram_url': '',
        'twitter_url': '',
        'logo': '',
    }
    for k, v in defaults.items():
        if not SiteSettings.query.filter_by(key=k).first():
            db.session.add(SiteSettings(key=k, value=v))
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        init_db()
    print("=" * 60)
    print("  Church Website Running!")
    print("  Open: http://localhost:5000")
    print("  Admin: http://localhost:5000/admin")
    print("  Username: Eugene | Password: almighty")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
