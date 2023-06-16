from flask import Flask, render_template, redirect, request
from flask_mail import Mail, Message
from dotenv import load_dotenv
from urllib.parse import parse_qs
import secrets
import random


app = Flask(__name__)
load_dotenv()

app.config["MAIL_SERVER"] = "victim_mail"
app.config["MAIL_PORT"] = 1025
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_USERNAME"] = ""
app.config["MAIL_PASSWORD"] = ""
app.config["MAIL_DEFAULT_SENDER"] = "sender-noreply@test.it"
mail = Mail(app)


users = {
    "admin123@victimmail.it": {"password": secrets.token_hex(20), "token": ""},
    "user1@victimmail.it": {"password": secrets.token_hex(20), "token": ""},
    "user2@victimmail.it": {"password": secrets.token_hex(20), "token": ""},
    "user3@victimmail.it": {"password": secrets.token_hex(20), "token": ""},
    "user4@victimmail.it": {"password": secrets.token_hex(20), "token": ""},
    "user5@victimmail.it": {"password": secrets.token_hex(20), "token": ""},
}


@app.route("/", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        if email in users:
            if users[email]["password"] == password:
                return render_template("home.html", email=email)
            else:
                error = "Invalid credentials, please try again!"
        else:
            error = "The inserted email do not exist"

    return render_template("login.html", error=error)


@app.route("/resetpassword", methods=["GET", "POST"])
def resetpassword():
    error = None
    message = None

    domain = request.host
    allowedDomains = [
        "webserver:80",
        "localhost:80",
        "remoteurl:80",
        "webserver:8085",
        "localhost:8085",
        "remoteurl:8085",
    ]
    if domain not in allowedDomains:
        randomIndex = random.randint(0, len(allowedDomains))
        domain = allowedDomains[randomIndex]

    if request.method == "POST":
        recipient = request.form["email"]

        if recipient in users:
            token = secrets.token_hex(20)  # SHA1(recipient)
            users[recipient]["token"] = token
            msg = Message("Reset your password", recipients=[recipient])
            msg.html = render_template(
                "reset_password_mail.html",
                token=token,
                domain=domain,
            )
            mail.send(msg)

            message = "An email has been sent to your account!"
        else:
            error = "The inserted email do not exist"

    return render_template("reset_password.html", error=error, message=message)


@app.route("/resetpasswordwithtoken", methods=["GET", "POST"])
def resetpasswordwithtoken():
    error = None

    if request.method == "POST":

        password = request.form["password"]
        confirmPassword = request.form["confirm_password"]
        query_params = parse_qs(request.url.split("?")[-1])
        token = query_params["token"][0]

        if password != confirmPassword:
            error = "Passwords do not match!"
        else:

            for email in users.keys():
                if users[email]["token"] == token:
                    users[email]["password"] = password
                    users[email]["token"] = ""

                    return redirect("/")

            error = "An error occured"

    return render_template("create_new_password.html", error=error)
