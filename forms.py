from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FieldList
from wtforms.validators import DataRequired, URL, Email
from flask_ckeditor import CKEditorField

class SermonForm(FlaskForm):
    title = StringField("Sermon Title", validators=[DataRequired()])
    body = CKEditorField("Please provide a summary.", validators=[DataRequired()])
    author = StringField("Author", validators=[DataRequired()])
    submit = SubmitField("Post Sermon")

class PrayerForm(FlaskForm):
    requests = FieldList(StringField("Prayer Requests"), min_entries=1, max_entries=6)
    testimonies = FieldList(StringField("Testimonies"), min_entries=1, max_entries=6)
    submit = SubmitField("Post")





