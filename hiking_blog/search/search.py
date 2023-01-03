from flask import Blueprint, render_template, redirect, flash, request, url_for, current_app
from hiking_blog.forms import SearchForm
from hiking_blog.models import Gear
from hiking_blog.db import db


search_bp = Blueprint(
    "search_bp", __name__,
    template_folder="templates",
    static_folder="static"
)


@current_app.context_processor
def send_form_to_navbar():
    form = SearchForm()
    return dict(form=form)


@search_bp.route("/search", methods=["POST"])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        searched = form.searched.data
        results = []
        results = check_gear_review_content(searched, results)
        results = check_gear_review_names(searched, results)
        # results = check_gear_review_keywords(searched, results)
        # results = check_gear_review_comments(searched, results)
        # results = check_trail_review_content(searched, results)
        # results = check_trail_review_names(searched, results)
        # results = check_trail_review_keywords(searched, results)
        # results = check_trail_review_comments(searched, results)
        print(f"{results} final")
        return render_template("search.html", form=form, searched=searched, results=results)


def check_gear_review_content(searched, results):
    if searched:
        hits = Gear.query.filter(Gear.review.like(f"%{searched}%")).all()
        if hits:
            for hit in hits:
                record = {"gear/trail": "gear", "gear/trail name": hit.name, "id": hit.id, "relevance_points": 1}
                results.append(record)
    print(f"{results} after content")
    return results


def check_gear_review_names(searched, results):
    if searched:
        hits = Gear.query.filter(Gear.name.like(f"%{searched}%")).all()
        if hits:
            for hit in hits:
                entry_change = False
                for dic in results:
                    print(f"searched: {searched.lower()}")
                    print(f"gear.name: {hit.name.lower()}")
                    print(f'dict_name: {dic["gear/trail name"].lower()}')
                    if hit.name.lower() == dic["gear/trail name"].lower():
                        if searched.lower() == dic["gear/trail name"].lower():
                            print("is name")
                            dic["relevance_points"] += 1000
                            entry_change = True
                        else:
                            print("in name")
                            dic["relevance_points"] += 10
                            entry_change = True
                if not entry_change:
                    record = {"gear/trail": "gear", "gear/trail name": hit.name, "id": hit.id, "relevance_points": 0}
                    if searched.lower() == hit.name.lower():
                        record["relevance_points"] = 1000
                    else:
                        record["relevance_points"] = 10
                    print(f"added {hit.name}")
                    results.append(record)
    print(f"{results} after names")
    return results



    #                 if searched.lower() in hit.name.lower() and hit.name.lower() == dic["gear/trail name"].lower():
    #                     print("in name")
    #                     dic["relevance_points"] += 10
    #                     entry_change = True
    #                 if searched.lower() == dic["gear/trail name"].lower():
    #                     print("is name")
    #                     dic["relevance_points"] += 1000
    #                     entry_change = True
    #             if not entry_change:
    #                 record = {"gear/trail": "gear", "gear/trail name": hit.name, "relevance_points": 0}
    #                 if searched.lower() == hit.name.lower():
    #                     record["relevance_points"] = 1000
    #                 else:
    #                     record["relevance_points"] = 10
    #                 print(f"added {hit.name}")
    #                 results.append(record)
    # print(f"{results} after names")
    # return results


def check_gear_review_keywords(searched, results):
    if searched:
        results.append(f"{searched} func_three")
    return results


def check_gear_review_comments(searched, results):
    if searched:
        results.append(f"{searched} func_four")
    return results


def check_trail_review_content(searched, results):
    if searched:
        results.append(f"{searched} func_five")
    return results


def check_trail_review_names(searched, results):
    if searched:
        results.append(f"{searched} func_six")
    return results


def check_trail_review_keywords(searched, results):
    if searched:
        results = results
    return results


def check_trail_review_comments(searched, results):
    if searched:
        results = results
    return results