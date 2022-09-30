"""Allows the user to contact the admin via email."""
from flask import render_template, redirect, url_for, Blueprint
from hiking_blog.forms import ContactForm
import smtplib
from threading import Thread
import os


EMAIL = os.environ["EMAIL"]
EMAIL_PW = os.environ["EMAIL_PW"]

contact_bp = Blueprint(
    "contact_bp", __name__
)


@contact_bp.route("/contact", methods=["GET", "POST"])
def contact():
    """
    Upon form submission, sends a message from the user to the admin via email.

    The Thread object allows the email sending functionality to run in the background while the user continues
    navigating the site. The user is redirected to the home page after submitting.
    """
    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data,
        email = form.email.data,
        subject = form.subject.data,
        message = form.message.data
        thread = Thread(target=send_email, args=(name, message, subject, email))
        thread.daemon = True
        thread.start()
        return redirect(url_for("home"))
    return render_template("contact.html", form=form)


def send_email(name, message, subject, email):
    """
    Sends an email from the user to the admin containing the information gathered in the contact() function.

    Parameters
    ----------
    name : str
        The users entered name
    message : str
        A message entered by the user
    subject : str
        An email subject line entered by the user
    email : str
        The users entered email address
    """
    print("starting to send email")
    with smtplib.SMTP("smtp.mail.yahoo.com") as connection:
        print("Initiating TLS")
        connection.starttls()
        print("logging in")
        connection.login(user=EMAIL, password=EMAIL_PW)
        print("sending email")
        connection.sendmail(
            from_addr=EMAIL,
            to_addrs=EMAIL,
            msg=f"Subject: {subject}\n\nSent by:{name}, {email}\n{message}</body></html>"
        )
        print("done")