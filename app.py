from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)

# Models
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    products = db.relationship('Product', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    cost_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=0)
    min_quantity = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    image = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Product {self.name}>'

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Supplier {self.name}>'

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    quantity = db.Column(db.Integer, nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)  # 'in' or 'out'
    unit_price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    reference_number = db.Column(db.String(50))
    notes = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    product = db.relationship('Product', backref=db.backref('transactions', lazy=True))
    supplier = db.relationship('Supplier', backref=db.backref('transactions', lazy=True))
    
    def __repr__(self):
        return f'<Transaction {self.id}>'

# Routes
@app.route('/')
def index():
    products = Product.query.all()
    categories = Category.query.all()
    suppliers = Supplier.query.all()
    return render_template('index.html', products=products, categories=categories, suppliers=suppliers)

@app.route('/category/new', methods=['GET', 'POST'])
def new_category():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        
        category = Category(name=name, description=description)
        db.session.add(category)
        db.session.commit()
        
        flash('Danh mục đã được thêm thành công!', 'success')
        return redirect(url_for('index'))
    
    return render_template('new_category.html')

@app.route('/supplier/new', methods=['GET', 'POST'])
def new_supplier():
    if request.method == 'POST':
        name = request.form['name']
        contact_person = request.form['contact_person']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        
        supplier = Supplier(
            name=name,
            contact_person=contact_person,
            email=email,
            phone=phone,
            address=address
        )
        db.session.add(supplier)
        db.session.commit()
        
        flash('Nhà cung cấp đã được thêm thành công!', 'success')
        return redirect(url_for('index'))
    
    return render_template('new_supplier.html')

@app.route('/product/new', methods=['GET', 'POST'])
def new_product():
    if request.method == 'POST':
        name = request.form['name']
        sku = request.form['sku']
        description = request.form['description']
        price = float(request.form['price'])
        cost_price = float(request.form['cost_price'])
        quantity = int(request.form['quantity'])
        min_quantity = int(request.form['min_quantity'])
        category_id = int(request.form['category_id'])
        
        # Handle image upload
        image = request.files['image']
        if image:
            filename = f"{sku}_{image.filename}"
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            filename = None
        
        product = Product(
            name=name,
            sku=sku,
            description=description,
            price=price,
            cost_price=cost_price,
            quantity=quantity,
            min_quantity=min_quantity,
            category_id=category_id,
            image=filename
        )
        db.session.add(product)
        db.session.commit()
        
        flash('Sản phẩm đã được thêm thành công!', 'success')
        return redirect(url_for('index'))
    
    categories = Category.query.all()
    return render_template('new_product.html', categories=categories)

@app.route('/product/<int:id>/edit', methods=['GET', 'POST'])
def edit_product(id):
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        product.name = request.form['name']
        product.sku = request.form['sku']
        product.description = request.form['description']
        product.price = float(request.form['price'])
        product.cost_price = float(request.form['cost_price'])
        product.quantity = int(request.form['quantity'])
        product.min_quantity = int(request.form['min_quantity'])
        product.category_id = int(request.form['category_id'])
        
        # Handle image upload
        image = request.files['image']
        if image:
            filename = f"{product.sku}_{image.filename}"
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            product.image = filename
        
        db.session.commit()
        flash('Sản phẩm đã được cập nhật thành công!', 'success')
        return redirect(url_for('index'))
    
    categories = Category.query.all()
    return render_template('edit_product.html', product=product, categories=categories)

@app.route('/product/<int:id>/delete')
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Sản phẩm đã được xóa thành công!', 'success')
    return redirect(url_for('index'))

@app.route('/transaction/new', methods=['GET', 'POST'])
def new_transaction():
    if request.method == 'POST':
        product_id = int(request.form['product_id'])
        supplier_id = int(request.form['supplier_id']) if request.form['supplier_id'] else None
        quantity = int(request.form['quantity'])
        transaction_type = request.form['transaction_type']
        unit_price = float(request.form['unit_price'])
        reference_number = request.form['reference_number']
        notes = request.form['notes']
        
        product = Product.query.get_or_404(product_id)
        
        if transaction_type == 'out' and product.quantity < quantity:
            flash('Số lượng sản phẩm trong kho không đủ!', 'error')
            return redirect(url_for('new_transaction'))
        
        total_amount = quantity * unit_price
        
        transaction = Transaction(
            product_id=product_id,
            supplier_id=supplier_id,
            quantity=quantity,
            transaction_type=transaction_type,
            unit_price=unit_price,
            total_amount=total_amount,
            reference_number=reference_number,
            notes=notes
        )
        
        if transaction_type == 'in':
            product.quantity += quantity
        else:
            product.quantity -= quantity
        
        db.session.add(transaction)
        db.session.commit()
        
        flash('Giao dịch đã được thêm thành công!', 'success')
        return redirect(url_for('index'))
    
    products = Product.query.all()
    suppliers = Supplier.query.all()
    return render_template('new_transaction.html', products=products, suppliers=suppliers)

@app.route('/reports/inventory')
def inventory_report():
    products = Product.query.all()
    return render_template('inventory_report.html', products=products)
@app.route('/category/<int:id>/delete', methods=['POST'])
def delete_category(id):
    category = Category.query.get_or_404(id)
    
    # Kiểm tra nếu danh mục có sản phẩm liên quan
    if category.products:
        flash('Không thể xóa danh mục vì vẫn còn sản phẩm liên quan!', 'error')
        return redirect(url_for('index'))
    
    db.session.delete(category)
    db.session.commit()
    flash('Danh mục đã được xóa thành công!', 'success')
    return redirect(url_for('index'))
@app.route('/supplier/<int:id>/delete', methods=['POST'])
def delete_supplier(id):
    supplier = Supplier.query.get_or_404(id)
    
    # Kiểm tra nếu nhà cung cấp có giao dịch liên quan
    if supplier.transactions:
        flash('Không thể xóa nhà cung cấp vì vẫn còn giao dịch liên quan!', 'error')
        return redirect(url_for('index'))
    
    db.session.delete(supplier)
    db.session.commit()
    flash('Nhà cung cấp đã được xóa thành công!', 'success')
    return redirect(url_for('index'))
@app.route('/reports/transactions')
def transaction_report():
    transactions = Transaction.query.order_by(Transaction.date.desc()).all()
    return render_template('transaction_report.html', transactions=transactions)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)