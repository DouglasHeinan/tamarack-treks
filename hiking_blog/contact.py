"""Allows the user to contact the admin via email."""
from flask import render_template, redirect, url_for, Blueprint, flash
from flask_mail import Message
from flask_login import current_user
# from hiking_blog.mail import mail
from bs4 import BeautifulSoup
from hiking_blog.forms import ContactForm, PasswordRecoveryForm
from hiking_blog.models import User
from threading import Thread
import random
import smtplib
import os

CHARACTERS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
              'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
              'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
              '!', '#', '$', '%', '&', '*', '+']
PW_RESET_MESSAGE = "Here is your password reset code:"

msg = Message()

contact_bp = Blueprint(
    "contact_bp", __name__
)


@contact_bp.route("/contact", methods=["GET", "POST"])
def contact():
    """
    A function allowing the user to send information to the admin via email.

    The function takes in the information from the Contact Form and sends the data to the send_async_email function
    to start the emailing process.
    """

    form = ContactForm()
    if form.validate_on_submit():
        email = os.environ["EMAIL"]
        subject = form.subject.data
        message_body = BeautifulSoup(form.message.data, features="html.parser").text
        message = f"from user {form.name.data} at {form.email.data}:\n{message_body}"
        send_async_email(email, subject, message)
        # send_email(email, subject, message)
        return redirect(url_for("home_bp.home"))
    return render_template("contact.html", form=form)


@contact_bp.route("/password_recovery", methods=["GET", "POST"])
def password_recovery():
    """
    This function sends the user a temporary password to perform a password reset.

    If the user has forgotten their password and used the "forgot username or password" link, this function will create
    and email a temporary password to the user. The user enters their username into the form and, when submitted, the
    email for that username is sent a randomly generated eight character password, which will be relevant after the user
    is redirected. If the username does not exist in the database, the user will be redirected to the signup page. If
    the user is already logged in, they will be redirected to the home page.
    """

    form = PasswordRecoveryForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            flash("That username has not yet been created.")
            return redirect(url_for("auth_bp.sign_up"))
        if current_user.is_authenticated:
            flash("You are already logged in.")
            return redirect(url_for("home_bp.home"))

        password_code = password_reset_code_generator()
        email = user.email
        subject = "Outdoor Blog Password Recovery"
        message = f"Hey, {user.username}. {PW_RESET_MESSAGE} {password_code}"
        send_async_email(email, subject, message)
        # send_email(email, subject, message)
        return redirect(url_for("auth_bp.change_password_verify", username=user.username, password_code=password_code))
    return render_template("password_recovery.html", form=form)


def send_async_email(email, subject, message):
    thread = Thread(target=send_email, args=(email, subject, message))
    thread.daemon = True
    thread.start()


def send_email(email, subject, message):
    print("sending mail")
    with smtplib.SMTP("smtp.mail.yahoo.com") as connection:
        connection.starttls()
        connection.login(user=os.environ["EMAIL"], password=os.environ["EMAIL_PW"])
        connection.sendmail(from_addr=os.environ["EMAIL"],
                            to_addrs=email,
                            msg=f"Subject:{subject}\n\n{message}")
    print("mail sent")


# def send_email(email, subject, message):
#     msg.subject = subject
#     msg.recipients = [email]
#     msg.body = message
#     mail.send(msg)


def password_reset_code_generator():
    """Generates a random 8 digit security code to verify the user during a password reset."""
    password_characters = [random.choice(CHARACTERS) for i in range(8)]
    random.shuffle(password_characters)
    password_verification = "".join(password_characters)
    return password_verification
