from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy import desc, Integer, String, Text, ForeignKey,Column
# Import your forms from the forms.py
from forms import SermonForm, PrayerForm
import requests
import os


api_url = "https://bible-api.com/"
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
Bootstrap5(app)
ckeditor = CKEditor(app)

login_manager = LoginManager()
login_manager.init_app(app)

def make_list(input):
    list = input.split(',')
    number_list = [int(num) for num in list]
    return number_list

def not_in(input, num):
    list = input.split(',')
    number_list = [int(num) for num in list]
    if num not in number_list:
        return 2
    else:
        return 1

class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI",'sqlite:///family-cell.db')
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class User(Base, db.Model, UserMixin):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String(250), unique=True, nullable=False)
    img_url = Column(String(250), nullable=False)
    sermons = Column(String(250))
    comments = relationship("Comment", back_populates="comment_author")
    testimonies = relationship('Testimony', back_populates='author')

class Sermon(db.Model, Base):
    __tablename__ = "sermon"
    id = Column(Integer, primary_key=True)
    title = Column(String(250), unique=True, nullable=False)
    date = Column(String(250), nullable=False)
    body = Column(Text, nullable=False)
    author = Column(Text, nullable=False)
    comments = relationship("Comment", back_populates="sermon")

class Comment(Base):
    __tablename__ = "comment"
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    comment_author = relationship("User", back_populates="comments")
    sermon_id = Column(Integer, ForeignKey('sermon.id'))
    sermon = relationship("Sermon", back_populates="comments")

class Testimony(Base, db.Model):
    __tablename__ = "testimony"
    id = Column(Integer, primary_key=True)
    testimony = Column(String(250), nullable=True)
    request = Column(String(250), nullable=True)
    date = Column(String(250), nullable=False)
    author_id = Column(Integer, ForeignKey('user.id'))
    author = relationship('User', back_populates='testimonies')


with app.app_context():
   db.create_all()

base_url = 1

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    users = db.session.query(User).all()
    return render_template('home.html', guys=users, x=0)

@app.route("/about")
def about():
    users = db.session.query(User).all()
    return render_template('about.html', guys=users, x =0)

@app.route("/sermons/<int:num>", methods=['POST','GET'])
def sermons(num):
    global base_url
    sermon = db.get_or_404(Sermon, num)
    if current_user.is_authenticated:
        user = db.get_or_404(User, current_user.id)
        if user.sermons:
            not_saved = not_in(user.sermons, sermon.id)
        else:
            not_saved = 2
    else:
        not_saved = 2
    sermons = db.session.query(Sermon).filter(Sermon.id != num).order_by(desc(Sermon.date)).all()
    users = db.session.query(User).all()
    comments = db.session.query(Comment).filter_by(sermon_id=num).order_by(Comment.id.desc()).all()

    body = sermon.body
    list = body.split('/')
    print(list)
    numbers = []
    for i in range(0, len(list)):
        if list[i] == '*':
            numbers.append(i)
    print(numbers)
    for i in range(0, len(numbers), 2):
        verse = list[numbers[i] + 1]
        print(verse)
        response = requests.get(api_url + verse)
        data = response.json()
        print(data)
        list[numbers[i] + 1] = f'''
                <button type="button" data-popover class="btn" data-bs-toggle="popover" 
                title="{data["text"]}" 
                data-content="{verse}">
                {data["reference"]}</button>'''

    body = '/'.join(list)

    base_url= 1
    if request.method == 'POST':
        comment = request.form['comment']
        new_comment = Comment(text=comment, user_id=current_user.id, sermon_id=num)
        db.session.add(new_comment)
        db.session.commit()
        redirect(url_for('sermons', num=1))
    length = len(sermons) + 1

    return render_template('sermon.html',body=body, sermon=sermon, sermons=sermons, guys=users, x = 1, num=int(num), comments=comments, len=length, not_saved=not_saved)

@app.route("/new-sermon", methods=['POST','GET'])
def new():
    form=SermonForm()
    users = db.session.query(User).all()
    if form.validate_on_submit():
        current_date = datetime.now()
        title =form.title.data
        s = Sermon(title= title,
               date= current_date.strftime('%d/%m/%y'),
               body=form.body.data,
               author=form.author.data,
               )
        db.session.add(s)
        db.session.commit()
        sermon = Sermon.query.filter_by(title=title).first()
        num = sermon.id

        return redirect(url_for('sermons', num=num))
    url = url_for('new')
    return render_template('new.html', form=form, url=url, guys=users, x=0)

@app.route("/edit/<id>", methods=['GET','POST'])
def edit(id):
    sermon = db.get_or_404(Sermon, id)
    date = sermon.date
    users = db.session.query(User).all()
    form= SermonForm(
        title= sermon.title,
        body=sermon.body,
        author=sermon.author,
    )
    if form.validate_on_submit():
        sermon.title = form.title.data
        sermon.body = form.body.data
        sermon.author = form.author.data
        sermon.date = date
        db.session.commit()
        return redirect(url_for('sermons', num=id))

    url = url_for('edit', id=id)

    return render_template('new.html', url=url, form=form, guys=users, x=0)

@app.route('/prayer/<id>', methods=['POST','GET'])
def prayer(id):
    global base_url
    base_url = 2
    form =PrayerForm()
    users = db.session.query(User).all()
    if form.validate_on_submit():
        current_date = datetime.now()
        list_of_requests = [field.data for field in form.requests.entries if field.data]
        list_of_testimonies = [field.data for field in form.testimonies.entries if field.data]
        dynamic_fields = request.form.getlist('dynamic_fields')
        dynamic_field = request.form.getlist('dynamic_field')
        print(dynamic_fields)
        print(dynamic_field)

        for item in dynamic_fields:
            list_of_requests.append(item)
        for item in dynamic_field:
            list_of_testimonies.append(item)
        if len(list_of_requests) >= len(list_of_testimonies):
            print('equal')
            for i in range(0,len(list_of_testimonies)):
                first =Testimony( testimony=list_of_testimonies[i],
                           request=list_of_requests[i],
                           date= current_date.strftime('%d/%B/%Y'),
                           author=current_user
                           )
                print('yes')
                db.session.add(first)
                db.session.commit()
            for i in range(len(list_of_testimonies),len(list_of_requests)):
                second = Testimony(testimony=None,
                          request=list_of_requests[i],
                          date=current_date.strftime('%d/%m/%y'),
                          author=current_user
                          )
                print('no')
                db.session.add(second)
                db.session.commit()
            return redirect(url_for('prayer', id=id))
        else:
            for i in range(0,len(list_of_requests)):
                first =Testimony( testimony=list_of_testimonies[i],
                           request=list_of_requests[i],
                           date= current_date.strftime('%d/%B/%Y'),
                           author=current_user
                           )
                db.session.add(first)
                db.session.commit()
            for i in range(len(list_of_requests),len(list_of_testimonies)):
                second = Testimony(testimony=list_of_testimonies[i],
                          request=None,
                          date=current_date.strftime('%d/%m/%y'),
                          author=current_user
                          )
                db.session.add(second)
                db.session.commit()
            return redirect(url_for('prayer', id=id))

    user_requests_testimonies = (
        db.session.query(Testimony)
        .filter(Testimony.author_id == id)
        .all()
    )

    # Separate requests and testimonies into different lists
    requests_list = [item for item in user_requests_testimonies if item.request]
    testimonies_list = [item.testimony for item in user_requests_testimonies if item.testimony]
    testimonies_list.reverse()

    print(base_url)
    return render_template('prayer.html', form=form, guys=users, req=requests_list, tes=testimonies_list, x=1)

@app.route('/login/<id>')
def login(id):
    if current_user.is_authenticated:
        logout_user()
    user = db.get_or_404(User, id)
    login_user(user)
    print(current_user.is_authenticated)
    if base_url == 2:
        return redirect(url_for('prayer', id=id))
    elif base_url ==1:
        return redirect(url_for('sermons', num=1))
    else:
        return redirect(url_for('personal', id=id))


@app.route('/delete/<id>', methods=['POST','DELETE', 'GET'])
@login_required
def delete(id):
    testimony= db.get_or_404(Testimony, id)
    testimony.request = None
    db.session.commit()
    return redirect(url_for('prayer', id=current_user.id))

@app.route('/save/<id>', methods=['POST','GET'])
@login_required
def save(id):
    number = current_user.id
    user = db.get_or_404(User, number)
    sermon = user.sermons
    if sermon:
        if not_in(sermon, int(id)):
            user.sermons = sermon + f",{id}"
            db.session.commit()
        else:
            flash('Already saved')
    else:
        user.sermons = f"{id}"
        db.session.commit()
    return redirect(url_for('sermons', num=id))

@app.route('/saved/<id>', methods=['POST','GET'])
@login_required
def unsave(id):
    print(type(id))
    number = current_user.id
    user = db.get_or_404(User, number)
    sermon = user.sermons
    my_list = make_list(sermon)
    print(my_list)
    my_list.remove(int(id))
    string_list = [str(x) for x in my_list]
    user.sermons = ','.join(string_list)
    print(user.sermons)
    db.session.commit()
    return redirect(url_for('sermons', num=id))

@app.route('/personal/<id>', methods=['POST','GET'])
def personal(id):
    global base_url
    base_url =3
    users = db.session.query(User).all()
    user = db.get_or_404(User, id)
    saved = []
    subtext=[]
    length=0
    if user.sermons:
        saved_sermons = make_list(user.sermons)
        length = len(saved_sermons)

        for num in saved_sermons:
            sermon = db.get_or_404(Sermon, num)
            saved.append(sermon)
            body = sermon.body
            p_list = body.split('<p>')
            print(p_list)
            subtext.append(p_list[1])

    return render_template('personal.html', saved=saved, x=1, guys=users, subtext=subtext, len=length)

if __name__ == "__main__":
    app.run(debug=False)