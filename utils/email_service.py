from flask_mail import Mail, Message

# Initialize the Flask-Mail object
mail = Mail()

def configure_mail(app):
    """Configure Flask-Mail with the app."""
    # Looking to send emails in production? Check out our Email API/SMTP product!
    app.config['MAIL_SERVER']='sandbox.smtp.mailtrap.io'
    app.config['MAIL_PORT'] = 2525
    app.config['MAIL_USERNAME'] = '42c4937b63b7bc'
    app.config['MAIL_PASSWORD'] = 'fac5cacbef7e28'
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    mail.init_app(app)

def send_verification_email(email, verification_link):
    """Send a verification email."""
    subject = "Verify Your Email - Quotes API"
    body = f"""
    Hello,
    Thank you for chosing Quotz API. This is small API service created to help developers to easily get a good quotes from our store of quotes.

    Please verify your email by clicking the link below:

    {verification_link}

    If you did not request this, please ignore this email.

    Thank you!
    """
    try:
        msg = Message(subject=subject, recipients=[email], body=body)
        mail.send(msg)
        print(f"Verification email sent to {email}.")
    except Exception as e:
        print(f"Failed to send email to {email}: {e}")