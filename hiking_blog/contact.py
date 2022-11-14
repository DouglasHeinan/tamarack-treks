"""Allows the user to contact the admin via email."""
from flask import render_template, redirect, url_for, Blueprint, flash, current_app
from flask_login import current_user
from bs4 import BeautifulSoup
from hiking_blog.forms import ContactForm, UsernameRecoveryForm
from hiking_blog.models import User
from itsdangerous import URLSafeTimedSerializer
from threading import Thread
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import os

CHARACTERS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
              'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
              'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
              '!', '#', '$', '%', '&', '*', '+']
PW_RESET_MESSAGE = "Here is your password reset code:"
EMAIL = os.environ["EMAIL"]


contact_bp = Blueprint(
    "contact_bp", __name__
)


@contact_bp.route("/contact/contact_admin", methods=["GET", "POST"])
def contact():
    """
    A function allowing the user to send information to the admin via email.

    The function takes in the information from the Contact Form and sends the data to the send_async_email function
    to start the emailing process.
    """

    form = ContactForm()
    if form.validate_on_submit():
        email = EMAIL
        subject = form.subject.data
        message_body = BeautifulSoup(form.message.data, features="html.parser").text
        message = f"from user {form.name.data} at {form.email.data}:\n{message_body}"
        send_async_email(email, subject, message, send_email)
        return redirect(url_for("home_bp.home"))
    return render_template("form_page.html",
                           form=form,
                           form_header="Contact Us",
                           form_sub_header="Thanks for reaching out. We'll respond as soon as we can.",
                           text_box="message")


@contact_bp.route("/contact/username_recovery", methods=["GET", "POST"])
def username_recovery():
    """
    Takes user's email input and sends them an email with their username.

    If a user has forgotten their username, this function finds their username from their email, checks that their info
    is valid and, if it is, sends them an email with their username before redirecting them to the login page.
    """

    form = UsernameRecoveryForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        message, reroute = check_recovery_form(user)
        if message:
            flash(message)
            return reroute
        send_user_reminder(user, email)
        flash("An email with your username should be in your inbox shortly.")
        return redirect(url_for("auth_bp.login"))
    return render_template("form_page.html",
                           form=form,
                           form_header="Forgot Username?",
                           form_sub_header="Enter your email and a message will be sent to you reminding you of your"
                                           " username."
                           )


def send_async_email(email, subject, message, target):
    """Opens a thread for sending emails so the user can continue browsing while the email is being sent."""
    thread = Thread(target=target, args=(email, subject, message))
    thread.daemon = True
    thread.start()


def send_email(email, subject, message):
    """Opens smtplib and uses it to send an email."""
    print("sending mail")
    with smtplib.SMTP("smtp.mail.yahoo.com") as connection:
        connection.starttls()
        connection.login(user=EMAIL, password=os.environ["EMAIL_PW"])
        connection.sendmail(from_addr=EMAIL,
                            to_addrs=email,
                            msg=f"Subject:{subject}\n\n{message}")
    print("mail sent")


def send_html_mail(email, subject, message):
    """Sends an html page as email."""
    print("sending html mail")
    mime_message = MIMEMultipart("alternative")
    html_body = MIMEText(message, "html")
    mime_message.attach(html_body)
    with smtplib.SMTP("smtp.mail.yahoo.com") as connection:
        connection.starttls()
        connection.login(user=EMAIL, password=os.environ["EMAIL_PW"])
        connection.sendmail(from_addr=EMAIL,
                            to_addrs=email,
                            msg=f"Subject:{subject}\n\n{message}")
    print("html mail sent")


def check_recovery_form(user):
    """
    Checks the user-provided info from the password- and user-recovery forms.

    This function is called by both recovery functions. If this function returns any value, those functions reroute the
    user from the recovery function.
    """

    message = None
    reroute = None
    if not user:
        message = "That username has not yet been created."
        reroute = redirect(url_for("auth_bp.sign_up"))
    if current_user.is_authenticated:
        message = "You are already logged in."
        reroute = redirect(url_for("home_bp.home"))
    return message, reroute


def send_password_reset_email(user_email):
    """Activated in the 'password_recovery' function, crafts and sends the password recovery email to the user."""
    pw_reset_serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    pw_reset_url = url_for(
        "auth_bp.reset_with_token",
        token=pw_reset_serializer.dumps(user_email, salt="pw-reset-salt"),
        _external=True
    )
    html = render_template(
        "html_email.html",
        link_url=pw_reset_url,
        email_body="Please click the link below to reset your password."
    )
    send_async_email(user_email, "Password Reset", html, send_html_mail)


def send_user_reminder(user, email):
    """Activated in the 'username_recovery' function, crafts and sends the username recovery email to the user."""
    username = user.username
    subject = "username reminder"
    message = f"Your username is {username}"
    send_async_email(email, subject, message, send_email)


def send_username_rejected_notification(user):
    subject = "Username rejected."
    email_body = "Your username does not conform with our terms of use and has been rejected by the admin." \
                 " Please click the link below to submit an alternative username."
    username_reset_url = url_for("auth_bp.reset_username", user_id=user.id, _external=True)
    html = render_template(
        "html_email.html",
        link_url=username_reset_url,
        email_body=email_body
    )
    # email = user.email
    # subject = "username rejected"
    # message = f"Your chosen username of {user.username} has been rejected by the site administrator. You have been " \
    #           f"assigned the temporary username of {user.username} until you are able to change your username to " \
    #           f"something in compliance with our site terms and agreements."
    send_async_email(user.email, subject, html, send_html_mail)
