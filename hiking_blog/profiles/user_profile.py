from flask import Blueprint, render_template, url_for
from hiking_blog.models import User


user_profiles_bp = Blueprint(
    "trails_bp", __name__,
    template_folder="templates",
    static_folder="static"
)


@user_profiles_bp.route("/user_profile/<user_id>")
def user_profile_dashboard(user_id):
    user = User.query.get(user_id)
    return render_template("user_profile.html")
