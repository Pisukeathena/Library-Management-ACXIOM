from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
from functools import wraps
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ─────────────────────────────────────────
# MODELS
# ─────────────────────────────────────────

class User(UserMixin, db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    password   = db.Column(db.String(200), nullable=False)
    role       = db.Column(db.String(20), default='user')   # admin / user
    is_active_user = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Category(db.Model):
    id    = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(100), unique=True, nullable=False)
    books = db.relationship('Book', backref='category', lazy=True)

class Book(db.Model):
    id               = db.Column(db.Integer, primary_key=True)
    serial_no        = db.Column(db.String(30), unique=True, nullable=False)
    title            = db.Column(db.String(200), nullable=False)
    author           = db.Column(db.String(150), nullable=False)
    item_type        = db.Column(db.String(10), default='book')   # book / movie
    isbn             = db.Column(db.String(20), unique=True, nullable=False)
    category_id      = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    total_copies     = db.Column(db.Integer, default=1)
    available_copies = db.Column(db.Integer, default=1)
    published_year   = db.Column(db.Integer)
    added_on         = db.Column(db.DateTime, default=datetime.utcnow)
    transactions     = db.relationship('Transaction', backref='book', lazy=True)

class Membership(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    membership_no   = db.Column(db.String(20), unique=True, nullable=False)
    name            = db.Column(db.String(100), nullable=False)
    email           = db.Column(db.String(120), unique=True, nullable=False)
    phone           = db.Column(db.String(20), nullable=False)
    address         = db.Column(db.String(200))
    duration        = db.Column(db.String(20), default='6months')  # 6months/1year/2years
    start_date      = db.Column(db.Date, default=date.today)
    expiry_date     = db.Column(db.Date)
    status          = db.Column(db.String(20), default='Active')   # Active/Cancelled
    transactions    = db.relationship('Transaction', backref='membership', lazy=True)

class Transaction(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    book_id       = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    membership_id = db.Column(db.Integer, db.ForeignKey('membership.id'), nullable=False)
    serial_no     = db.Column(db.String(30), nullable=False)
    issue_date    = db.Column(db.Date, default=date.today)
    return_date   = db.Column(db.Date)
    actual_return = db.Column(db.Date, nullable=True)
    status        = db.Column(db.String(20), default='Issued')   # Issued/Returned/Overdue
    fine_amount   = db.Column(db.Float, default=0.0)
    fine_paid     = db.Column(db.Boolean, default=False)
    remarks       = db.Column(db.String(300))

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# ─────────────────────────────────────────
# DECORATORS
# ─────────────────────────────────────────

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Access denied. Admin only.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────

def calculate_fine(due_date, return_date=None):
    check = return_date or date.today()
    if check > due_date:
        return (check - due_date).days * 5
    return 0

def generate_membership_no():
    last = Membership.query.order_by(Membership.id.desc()).first()
    num  = (last.id + 1) if last else 1
    return f'MEM{num:04d}'

def get_expiry(start, duration):
    if duration == '6months':
        return start + timedelta(days=183)
    elif duration == '1year':
        return start + timedelta(days=365)
    elif duration == '2years':
        return start + timedelta(days=730)
    return start + timedelta(days=183)

def update_overdue():
    issued = Transaction.query.filter_by(status='Issued').all()
    for t in issued:
        if t.return_date and date.today() > t.return_date:
            t.status = 'Overdue'
            t.fine_amount = calculate_fine(t.return_date)
    db.session.commit()

# ─────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user     = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ─────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    update_overdue()
    total_books       = Book.query.count()
    total_members     = Membership.query.filter_by(status='Active').count()
    total_issued      = Transaction.query.filter_by(status='Issued').count()
    total_overdue     = Transaction.query.filter_by(status='Overdue').count()
    recent_tx         = Transaction.query.order_by(Transaction.id.desc()).limit(6).all()
    return render_template('dashboard.html',
        total_books=total_books, total_members=total_members,
        total_issued=total_issued, total_overdue=total_overdue,
        recent_tx=recent_tx)

# ─────────────────────────────────────────
# BOOK AVAILABLE (Search)
# ─────────────────────────────────────────

@app.route('/books/search', methods=['GET', 'POST'])
@login_required
def book_search():
    results = []
    searched = False
    title  = request.args.get('title', '').strip()
    author = request.args.get('author', '').strip()
    category = request.args.get('category', '').strip()

    if request.method == 'GET' and (title or author or category):
        if not title and not author and not category:
            flash('Please enter at least one search criteria before submitting.', 'danger')
        else:
            searched = True
            q = Book.query.filter(Book.available_copies > 0)
            if title:
                q = q.filter(Book.title.ilike(f'%{title}%'))
            if author:
                q = q.filter(Book.author.ilike(f'%{author}%'))
            if category:
                q = q.filter(Book.category_id == category)
            results = q.all()

    categories = Category.query.all()
    return render_template('book_search.html',
        results=results, searched=searched,
        title=title, author=author, category=category,
        categories=categories)

# ─────────────────────────────────────────
# BOOK ISSUE
# ─────────────────────────────────────────

@app.route('/books/issue', methods=['GET', 'POST'])
@login_required
def book_issue():
    book_id = request.args.get('book_id') or request.form.get('book_id')
    book    = db.session.get(Book, int(book_id)) if book_id else None

    if request.method == 'POST':
        book_id       = request.form.get('book_id')
        membership_no = request.form.get('membership_no', '').strip()
        issue_date_s  = request.form.get('issue_date')
        return_date_s = request.form.get('return_date')
        remarks       = request.form.get('remarks', '')

        errors = []
        if not book_id:    errors.append('Book selection is required.')
        if not membership_no: errors.append('Membership number is required.')
        if not issue_date_s:  errors.append('Issue date is required.')
        if not return_date_s: errors.append('Return date is required.')

        issue_date  = None
        return_date = None
        membership  = None

        if issue_date_s:
            try:
                issue_date = datetime.strptime(issue_date_s, '%Y-%m-%d').date()
                if issue_date < date.today():
                    errors.append('Issue date cannot be earlier than today.')
            except:
                errors.append('Invalid issue date format.')

        if return_date_s:
            try:
                return_date = datetime.strptime(return_date_s, '%Y-%m-%d').date()
                if issue_date and return_date > issue_date + timedelta(days=15):
                    errors.append('Return date cannot be more than 15 days from issue date.')
                if issue_date and return_date < issue_date:
                    errors.append('Return date cannot be before issue date.')
            except:
                errors.append('Invalid return date format.')

        if membership_no:
            membership = Membership.query.filter_by(membership_no=membership_no, status='Active').first()
            if not membership:
                errors.append(f'No active membership found for number: {membership_no}')

        if errors:
            for e in errors:
                flash(e, 'danger')
            book = db.session.get(Book, int(book_id)) if book_id else None
            return render_template('book_issue.html', book=book,
                today=date.today().isoformat(),
                max_return=(date.today() + timedelta(days=15)).isoformat(),
                membership=membership, membership_no=membership_no)

        book_obj = db.session.get(Book, int(book_id))
        if not book_obj or book_obj.available_copies < 1:
            flash('Book not available.', 'danger')
            return redirect(url_for('book_search'))

        tx = Transaction(
            book_id       = int(book_id),
            membership_id = membership.id,
            serial_no     = book_obj.serial_no,
            issue_date    = issue_date,
            return_date   = return_date,
            status        = 'Issued',
            remarks       = remarks
        )
        book_obj.available_copies -= 1
        db.session.add(tx)
        db.session.commit()
        flash(f'Book "{book_obj.title}" issued successfully to {membership.name}!', 'success')
        return redirect(url_for('transactions'))

    today      = date.today().isoformat()
    max_return = (date.today() + timedelta(days=15)).isoformat()
    default_return = (date.today() + timedelta(days=15)).isoformat()
    return render_template('book_issue.html', book=book,
        today=today, max_return=max_return, default_return=default_return)

# API: get member by membership_no
@app.route('/api/membership/<membership_no>')
@login_required
def api_membership(membership_no):
    m = Membership.query.filter_by(membership_no=membership_no.strip()).first()
    if m:
        return jsonify({'found': True, 'name': m.name, 'email': m.email, 'status': m.status})
    return jsonify({'found': False})

# API: get book author by id
@app.route('/api/book/<int:book_id>')
@login_required
def api_book(book_id):
    b = db.session.get(Book, book_id)
    if b:
        return jsonify({'found': True, 'author': b.author, 'serial_no': b.serial_no, 'title': b.title})
    return jsonify({'found': False})

# ─────────────────────────────────────────
# RETURN BOOK
# ─────────────────────────────────────────

@app.route('/books/return', methods=['GET', 'POST'])
@login_required
def book_return():
    if request.method == 'POST':
        tx_id       = request.form.get('tx_id')
        serial_no   = request.form.get('serial_no', '').strip()
        return_date_s = request.form.get('return_date')

        errors = []
        if not serial_no:     errors.append('Serial number is mandatory.')
        if not return_date_s: errors.append('Return date is required.')

        tx = db.session.get(Transaction, int(tx_id)) if tx_id else None
        if not tx:
            flash('Transaction not found.', 'danger')
            return redirect(url_for('transactions'))

        if serial_no and serial_no != tx.serial_no:
            errors.append(f'Serial number does not match. Expected: {tx.serial_no}')

        return_date = None
        if return_date_s:
            try:
                return_date = datetime.strptime(return_date_s, '%Y-%m-%d').date()
            except:
                errors.append('Invalid return date.')

        if errors:
            for e in errors: flash(e, 'danger')
            return render_template('book_return.html', tx=tx)

        # Calculate fine
        fine = calculate_fine(tx.return_date, return_date)
        tx.actual_return = return_date
        tx.fine_amount   = fine
        db.session.commit()

        # Go to fine page
        return redirect(url_for('fine_pay', tx_id=tx.id))

    # GET — find transaction by book search
    tx_id = request.args.get('tx_id')
    tx    = db.session.get(Transaction, int(tx_id)) if tx_id else None
    issued_txs = Transaction.query.filter(Transaction.status.in_(['Issued','Overdue'])).all()
    return render_template('book_return.html', tx=tx, issued_txs=issued_txs)

# ─────────────────────────────────────────
# FINE PAY
# ─────────────────────────────────────────

@app.route('/fine/pay/<int:tx_id>', methods=['GET', 'POST'])
@login_required
def fine_pay(tx_id):
    tx = db.session.get(Transaction, tx_id)
    if not tx:
        flash('Transaction not found.', 'danger')
        return redirect(url_for('transactions'))

    if request.method == 'POST':
        fine_paid_cb = request.form.get('fine_paid')
        remarks      = request.form.get('remarks', '')

        if tx.fine_amount > 0 and not fine_paid_cb:
            flash('Fine must be marked as paid before completing the return.', 'danger')
            return render_template('fine_pay.html', tx=tx)

        tx.fine_paid  = True if fine_paid_cb else False
        tx.status     = 'Returned'
        tx.remarks    = remarks
        tx.book.available_copies += 1
        db.session.commit()
        flash('Book returned successfully!', 'success')
        return redirect(url_for('transactions'))

    return render_template('fine_pay.html', tx=tx)

# ─────────────────────────────────────────
# TRANSACTIONS (view)
# ─────────────────────────────────────────

@app.route('/transactions')
@login_required
def transactions():
    update_overdue()
    all_tx = Transaction.query.order_by(Transaction.id.desc()).all()
    return render_template('transactions.html', transactions=all_tx)

# ─────────────────────────────────────────
# REPORTS
# ─────────────────────────────────────────

@app.route('/reports')
@login_required
def reports():
    update_overdue()
    total_books      = Book.query.count()
    total_members    = Membership.query.filter_by(status='Active').count()
    total_issued     = Transaction.query.filter_by(status='Issued').count()
    total_overdue    = Transaction.query.filter_by(status='Overdue').count()
    total_returned   = Transaction.query.filter_by(status='Returned').count()
    fine_collected   = db.session.query(db.func.sum(Transaction.fine_amount)).filter_by(fine_paid=True).scalar() or 0
    fine_pending     = db.session.query(db.func.sum(Transaction.fine_amount)).filter_by(fine_paid=False).scalar() or 0

    popular = db.session.query(Book.title, db.func.count(Transaction.id).label('cnt'))\
        .join(Transaction).group_by(Book.id).order_by(db.text('cnt DESC')).limit(5).all()
    active_members = db.session.query(Membership.name, db.func.count(Transaction.id).label('cnt'))\
        .join(Transaction).group_by(Membership.id).order_by(db.text('cnt DESC')).limit(5).all()

    return render_template('reports.html',
        total_books=total_books, total_members=total_members,
        total_issued=total_issued, total_overdue=total_overdue,
        total_returned=total_returned, fine_collected=fine_collected,
        fine_pending=fine_pending, popular=popular, active_members=active_members)

# ─────────────────────────────────────────
# MAINTENANCE — ADMIN ONLY
# ─────────────────────────────────────────

@app.route('/maintenance')
@login_required
@admin_required
def maintenance():
    return render_template('maintenance.html')

# ── ADD BOOK ──────────────────────────────

@app.route('/maintenance/book/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_book():
    categories = Category.query.all()
    if request.method == 'POST':
        item_type  = request.form.get('item_type', 'book')
        serial_no  = request.form.get('serial_no', '').strip()
        title      = request.form.get('title', '').strip()
        author     = request.form.get('author', '').strip()
        isbn       = request.form.get('isbn', '').strip()
        cat_id     = request.form.get('category_id') or None
        copies     = request.form.get('total_copies', '').strip()
        year       = request.form.get('published_year', '').strip()

        errors = []
        if not serial_no: errors.append('Serial number is required.')
        if not title:     errors.append('Title is required.')
        if not author:    errors.append('Author is required.')
        if not isbn:      errors.append('ISBN is required.')
        if not copies:    errors.append('Number of copies is required.')
        if not year:      errors.append('Published year is required.')
        if Book.query.filter_by(serial_no=serial_no).first():
            errors.append('Serial number already exists.')
        if Book.query.filter_by(isbn=isbn).first():
            errors.append('ISBN already exists.')

        if errors:
            for e in errors: flash(e, 'danger')
            return render_template('add_book.html', categories=categories,
                form=request.form)

        copies_int = int(copies)
        book = Book(item_type=item_type, serial_no=serial_no, title=title,
                    author=author, isbn=isbn, category_id=cat_id,
                    total_copies=copies_int, available_copies=copies_int,
                    published_year=int(year) if year else None)
        db.session.add(book)
        db.session.commit()
        flash(f'{"Book" if item_type=="book" else "Movie"} "{title}" added successfully!', 'success')
        return redirect(url_for('add_book'))

    return render_template('add_book.html', categories=categories, form={})

# ── UPDATE BOOK ───────────────────────────

@app.route('/maintenance/book/update', methods=['GET', 'POST'])
@login_required
@admin_required
def update_book():
    categories = Category.query.all()
    book = None
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'search':
            serial_no = request.form.get('search_serial', '').strip()
            isbn_s    = request.form.get('search_isbn', '').strip()
            if not serial_no and not isbn_s:
                flash('Enter Serial No or ISBN to search.', 'danger')
            else:
                book = Book.query.filter(
                    (Book.serial_no == serial_no) | (Book.isbn == isbn_s)
                ).first()
                if not book:
                    flash('No book found with given details.', 'danger')
        elif action == 'update':
            book_id   = request.form.get('book_id')
            book      = db.session.get(Book, int(book_id))
            item_type = request.form.get('item_type', 'book')
            serial_no = request.form.get('serial_no', '').strip()
            title     = request.form.get('title', '').strip()
            author    = request.form.get('author', '').strip()
            isbn      = request.form.get('isbn', '').strip()
            cat_id    = request.form.get('category_id') or None
            copies    = request.form.get('total_copies', '').strip()
            year      = request.form.get('published_year', '').strip()

            errors = []
            if not title:  errors.append('Title is required.')
            if not author: errors.append('Author is required.')
            if not isbn:   errors.append('ISBN is required.')
            if not copies: errors.append('Copies is required.')
            if not year:   errors.append('Published year is required.')

            if errors:
                for e in errors: flash(e, 'danger')
                return render_template('update_book.html', categories=categories, book=book)

            book.item_type      = item_type
            book.serial_no      = serial_no
            book.title          = title
            book.author         = author
            book.isbn           = isbn
            book.category_id    = cat_id
            book.total_copies   = int(copies)
            book.published_year = int(year) if year else None
            db.session.commit()
            flash(f'Book "{title}" updated successfully!', 'success')
            return redirect(url_for('update_book'))

    return render_template('update_book.html', categories=categories, book=book)

# ── ADD MEMBERSHIP ────────────────────────

@app.route('/maintenance/membership/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_membership():
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip()
        phone    = request.form.get('phone', '').strip()
        address  = request.form.get('address', '').strip()
        duration = request.form.get('duration', '6months')

        errors = []
        if not name:    errors.append('Name is required.')
        if not email:   errors.append('Email is required.')
        if not phone:   errors.append('Phone is required.')
        if not address: errors.append('Address is required.')
        if not duration:errors.append('Please select membership duration.')
        if Membership.query.filter_by(email=email).first():
            errors.append('A membership with this email already exists.')

        if errors:
            for e in errors: flash(e, 'danger')
            return render_template('add_membership.html', form=request.form)

        mem_no  = generate_membership_no()
        start   = date.today()
        expiry  = get_expiry(start, duration)
        m = Membership(membership_no=mem_no, name=name, email=email,
                       phone=phone, address=address, duration=duration,
                       start_date=start, expiry_date=expiry)
        db.session.add(m)
        db.session.commit()
        flash(f'Membership created! Membership No: {mem_no}', 'success')
        return redirect(url_for('add_membership'))

    return render_template('add_membership.html', form={})

# ── UPDATE MEMBERSHIP ─────────────────────

@app.route('/maintenance/membership/update', methods=['GET', 'POST'])
@login_required
@admin_required
def update_membership():
    membership = None
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'search':
            mem_no = request.form.get('membership_no', '').strip()
            if not mem_no:
                flash('Membership number is required.', 'danger')
            else:
                membership = Membership.query.filter_by(membership_no=mem_no).first()
                if not membership:
                    flash(f'No membership found for number: {mem_no}', 'danger')
        elif action == 'update':
            mem_id   = request.form.get('mem_id')
            membership = db.session.get(Membership, int(mem_id))
            sub_action = request.form.get('sub_action')

            if sub_action == 'cancel':
                membership.status = 'Cancelled'
                db.session.commit()
                flash(f'Membership {membership.membership_no} cancelled.', 'info')
                return redirect(url_for('update_membership'))
            elif sub_action == 'extend':
                extension = request.form.get('extension', '6months')
                new_expiry = get_expiry(membership.expiry_date or date.today(), extension)
                membership.expiry_date = new_expiry
                membership.status      = 'Active'
                db.session.commit()
                flash(f'Membership extended until {new_expiry}!', 'success')
                return redirect(url_for('update_membership'))

    return render_template('update_membership.html', membership=membership)

# ── USER MANAGEMENT ───────────────────────

@app.route('/maintenance/users', methods=['GET', 'POST'])
@login_required
@admin_required
def user_management():
    all_users = User.query.order_by(User.id.desc()).all()
    if request.method == 'POST':
        action    = request.form.get('user_action', 'new')
        name      = request.form.get('name', '').strip()
        email     = request.form.get('email', '').strip()
        password  = request.form.get('password', '').strip()
        role      = request.form.get('role', 'user')

        if action == 'new':
            errors = []
            if not name:  errors.append('Name is required.')
            if not email: errors.append('Email is required.')
            if not password: errors.append('Password is required.')
            if User.query.filter_by(email=email).first():
                errors.append('Email already exists.')
            if errors:
                for e in errors: flash(e, 'danger')
                return render_template('user_management.html', all_users=all_users, form=request.form)

            u = User(name=name, email=email,
                     password=generate_password_hash(password), role=role)
            db.session.add(u)
            db.session.commit()
            flash(f'User "{name}" created successfully!', 'success')

        elif action == 'existing':
            user_id    = request.form.get('user_id')
            sub_action = request.form.get('sub_action')
            if not name:
                flash('Name is required.', 'danger')
                return render_template('user_management.html', all_users=all_users, form=request.form)
            user = db.session.get(User, int(user_id)) if user_id else None
            if user:
                if sub_action == 'deactivate':
                    user.is_active_user = False
                    db.session.commit()
                    flash(f'User "{user.name}" deactivated.', 'info')
                elif sub_action == 'activate':
                    user.is_active_user = True
                    db.session.commit()
                    flash(f'User "{user.name}" activated.', 'success')
                elif sub_action == 'update':
                    user.name = name
                    user.role = role
                    if password:
                        user.password = generate_password_hash(password)
                    db.session.commit()
                    flash(f'User "{name}" updated.', 'success')

        return redirect(url_for('user_management'))

    return render_template('user_management.html', all_users=all_users, form={})

# ── CATEGORIES (admin) ────────────────────

@app.route('/maintenance/categories', methods=['GET', 'POST'])
@login_required
@admin_required
def categories():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Category name is required.', 'danger')
        elif Category.query.filter_by(name=name).first():
            flash('Category already exists.', 'warning')
        else:
            db.session.add(Category(name=name))
            db.session.commit()
            flash('Category added!', 'success')
    all_cats = Category.query.all()
    return render_template('categories.html', categories=all_cats)

@app.route('/maintenance/categories/delete/<int:cat_id>')
@login_required
@admin_required
def delete_category(cat_id):
    cat = db.session.get(Category, cat_id)
    if cat:
        db.session.delete(cat)
        db.session.commit()
        flash('Category deleted.', 'info')
    return redirect(url_for('categories'))

# ─────────────────────────────────────────
# SEED DATA
# ─────────────────────────────────────────

def seed_data():
    if User.query.count() == 0:
        db.session.add(User(name='Admin', email='admin@library.com',
                            password=generate_password_hash('admin123'), role='admin'))
        db.session.add(User(name='John User', email='user@library.com',
                            password=generate_password_hash('user123'), role='user'))

    if Category.query.count() == 0:
        for c in ['Fiction','Non-Fiction','Science','Technology','History','Biography','Drama']:
            db.session.add(Category(name=c))

    if Book.query.count() == 0:
        books = [
            Book(serial_no='BK001', title='The Great Gatsby', author='F. Scott Fitzgerald',
                 isbn='9780743273565', item_type='book', total_copies=3, available_copies=3, published_year=1925),
            Book(serial_no='BK002', title='Clean Code', author='Robert C. Martin',
                 isbn='9780132350884', item_type='book', total_copies=2, available_copies=2, published_year=2008),
            Book(serial_no='BK003', title='Sapiens', author='Yuval Noah Harari',
                 isbn='9780062316097', item_type='book', total_copies=4, available_copies=4, published_year=2011),
            Book(serial_no='MV001', title='Inception', author='Christopher Nolan',
                 isbn='DVD0001', item_type='movie', total_copies=2, available_copies=2, published_year=2010),
            Book(serial_no='BK004', title='Atomic Habits', author='James Clear',
                 isbn='9780735211292', item_type='book', total_copies=3, available_copies=3, published_year=2018),
        ]
        db.session.add_all(books)

    if Membership.query.count() == 0:
        memberships = [
            Membership(membership_no='MEM0001', name='Ayushi Sharma', email='ayushi@example.com',
                       phone='9876543210', address='Mumbai, Maharashtra',
                       duration='1year', start_date=date.today(),
                       expiry_date=date.today()+timedelta(days=365), status='Active'),
            Membership(membership_no='MEM0002', name='Rahul Verma', email='rahul@example.com',
                       phone='9123456780', address='Delhi, India',
                       duration='6months', start_date=date.today(),
                       expiry_date=date.today()+timedelta(days=183), status='Active'),
        ]
        db.session.add_all(memberships)

    db.session.commit()

with app.app_context():
    db.create_all()
    seed_data()

if __name__ == '__main__':
    app.run(debug=True)
