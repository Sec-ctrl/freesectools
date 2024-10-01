from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    SelectField,
    FileField,
    PasswordField,
    SubmitField,
)
from wtforms.validators import DataRequired, Length, ValidationError


class BlogForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(min=5, max=200)])
    summary = TextAreaField(
        "Summary", validators=[DataRequired(), Length(min=10, max=500)]
    )
    content = TextAreaField("Content", validators=[DataRequired()])
    category = SelectField(
        "Category", coerce=int, validators=[DataRequired()]
    )  # Populate this dynamically
    image = FileField("Image")  # Handle file uploads

    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

    def validate_image(form, field):
        if field.data:
            filename = field.data.filename
            if (
                "." in filename
                and filename.rsplit(".", 1)[1].lower()
                not in BlogForm.ALLOWED_EXTENSIONS
            ):
                raise ValidationError(
                    "File extension not allowed. Allowed types are png, jpg, jpeg, gif."
                )


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")
