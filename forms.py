from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FieldList
from wtforms.validators import DataRequired, URL, Email
from flask_ckeditor import CKEditorField

class SermonForm(FlaskForm):
    title = StringField("Sermon Title", validators=[DataRequired()])
    body = CKEditorField("Please provide a summary.\n   (single-verse:/*/genesis1:2/*/, multiple-verses:/*/1peter+3:1-4/*/)\nWrong format will cause errors.Just go back incase this happens."
                         "You may choose not to use this format, if so don't use these symbols /*/ in that order.", validators=[DataRequired()])
    author = StringField("Author", validators=[DataRequired()])
    submit = SubmitField("Post Sermon")

class PrayerForm(FlaskForm):
    requests = FieldList(StringField("Prayer Requests"), min_entries=1, max_entries=6)
    testimonies = FieldList(StringField("Testimonies"), min_entries=1, max_entries=6)
    submit = SubmitField("Post")

class Userform(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    img_url = StringField("Image", validators=[DataRequired()])
    submit = SubmitField("Post")




