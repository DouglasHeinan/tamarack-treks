from flask import Flask, render_template


def main():

    app = Flask(__name__)

    @app.route("/")
    def home():
        return render_template("index.html")

    app.run(debug=True)


if __name__ == "__main__":
    main()
