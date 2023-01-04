from flask import Blueprint, render_template, redirect, flash, request, url_for, current_app
from hiking_blog.forms import SearchForm
from hiking_blog.models import Gear, GearComments, Trails, TrailComments
from collections import Counter
import string
import operator
import re
from hiking_blog.db import db

CLEAN = re.compile("<.*?>")

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
        results = check_gear_review_comments(searched, results)
        results = check_trail_review_content(searched, results)
        results = check_trail_review_names(searched, results)
        # results = check_trail_review_keywords(searched, results)
        results = check_trail_review_comments(searched, results)
        results = sorted(results, reverse=True, key=operator.itemgetter("relevance_points"))
        print(f"final results: {results}")
        return render_template("search.html", form=form, searched=searched, results=results)


def check_gear_review_content(searched, results):
    if searched:
        hits = Gear.query.filter(Gear.review.like(f"%{searched}%")).all()
        if hits:
            for hit in hits:
                record = {"gear/trail": "gear", "gear/trail name": hit.name, "id": hit.id, "relevance_points": 0}
                review = remove_html_tags(hit.review)
                review_words = [word.translate(
                    str.maketrans("", "", string.punctuation)
                ) for word in review.lower().split()]
                review_word_counts = Counter(review_words)
                record["relevance_points"] += (review_word_counts[searched] * 3)
                results.append(record)
    print("Gear Content:")
    for entry in results:
        print(f"    hit: {entry['gear/trail name']} points: {entry['relevance_points']}")
    return results


def check_gear_review_names(searched, results):
    if searched:
        hits = Gear.query.filter(Gear.name.like(f"%{searched}%")).all()
        if hits:
            for hit in hits:
                entry_change = False
                for dic in results:
                    if hit.name.lower() == dic["gear/trail name"].lower():
                        if searched.lower() == dic["gear/trail name"].lower():
                            dic["relevance_points"] += 1000
                            entry_change = True
                        else:
                            dic["relevance_points"] += 10
                            entry_change = True
                if not entry_change:
                    record = {"gear/trail": "gear", "gear/trail name": hit.name, "id": hit.id, "relevance_points": 0}
                    if searched.lower() == hit.name.lower():
                        record["relevance_points"] = 1000
                    else:
                        record["relevance_points"] = 10
                    results.append(record)
    print("Gear Names:")
    for entry in results:
        print(f"    hit: {entry['gear/trail name']} points: {entry['relevance_points']}")
    return results


def check_gear_review_keywords(searched, results):
    pass


def check_gear_review_comments(searched, results):
    if searched:
        hits = GearComments.query.filter(GearComments.text.like(f"%{searched}%")).all()
        if hits:
            for hit in hits:
                entry_change = False
                for dic in results:
                    if hit.parent_gear_posts.name.lower() == dic["gear/trail name"].lower():
                        comment_words = [word.translate(
                            str.maketrans("", "", string.punctuation)
                            ) for word in hit.text.lower().split()]
                        comment_word_counts = Counter(comment_words)
                        dic["relevance_points"] += comment_word_counts[searched]
                        entry_change = True
                if not entry_change:
                    record = {
                        "gear/trail": "gear",
                        "gear/trail name": hit.parent_gear_posts.name,
                        "id": hit.parent_gear_posts.id,
                        "relevance_points": 0
                    }
                    comment_words = [word.translate(
                        str.maketrans("", "", string.punctuation)
                    ) for word in hit.text.lower().split()]
                    comment_word_counts = Counter(comment_words)
                    record["relevance_points"] += comment_word_counts[searched]
                    results.append(record)
    print("Gear Comments:")
    for entry in results:
        print(f"    hit: {entry['gear/trail name']} points: {entry['relevance_points']}")
    return results


def check_trail_review_content(searched, results):
    if searched:
        hits = Trails.query.filter(Trails.description.like(f"%{searched}%")).all()
        if hits:
            for hit in hits:
                entry_change = False
                for dic in results:
                    if hit.name.lower() == dic["gear/trail name"].lower():
                        description = remove_html_tags(hit.description)
                        description_words = [word.translate(
                            str.maketrans("", "", string.punctuation)
                            ) for word in description.lower().split()]
                        description_word_counts = Counter(description_words)
                        dic["relevance_points"] += (description_word_counts[searched] * 3)
                        entry_change = True
                if not entry_change:
                    record = {"gear/trail": "trail", "gear/trail name": hit.name, "id": hit.id, "relevance_points": 0}
                    description = remove_html_tags(hit.description)
                    description_words = [word.translate(
                        str.maketrans("", "", string.punctuation)
                    ) for word in description.lower().split()]
                    description_word_counts = Counter(description_words)
                    record["relevance_points"] += (description_word_counts[searched] * 3)
                    results.append(record)
    print("Trail Content:")
    for entry in results:
        print(f"    hit: {entry['gear/trail name']} points: {entry['relevance_points']}")
    return results


def check_trail_review_names(searched, results):
    if searched:
        hits = Trails.query.filter(Trails.name.like(f"%{searched}%")).all()
        if hits:
            for hit in hits:
                entry_change = False
                for dic in results:
                    if hit.name.lower() == dic["gear/trail name"].lower():
                        if searched.lower() == dic["gear/trail name"].lower():
                            dic["relevance_points"] += 1000
                            entry_change = True
                        else:
                            dic["relevance_points"] += 10
                            entry_change = True
                if not entry_change:
                    record = {"gear/trail": "trail", "gear/trail name": hit.name, "id": hit.id, "relevance_points": 0}
                    if searched.lower() == hit.name.lower():
                        record["relevance_points"] = 1000
                    else:
                        record["relevance_points"] = 10
                    results.append(record)
    print("Trail Names:")
    for entry in results:
        print(f"    hit: {entry['gear/trail name']} points: {entry['relevance_points']}")
    return results


def check_trail_review_keywords(searched, results):
    pass


def check_trail_review_comments(searched, results):
    if searched:
        hits = TrailComments.query.filter(TrailComments.text.like(f"%{searched}%")).all()
        if hits:
            for hit in hits:
                entry_change = False
                for dic in results:
                    if hit.parent_trail_posts.name.lower() == dic["gear/trail name"].lower():
                        text = remove_html_tags(hit.text)
                        comment_words = [word.translate(
                            str.maketrans("", "", string.punctuation)
                            ) for word in text.lower().split()]
                        comment_word_counts = Counter(comment_words)
                        dic["relevance_points"] += comment_word_counts[searched]
                        entry_change = True
                if not entry_change:
                    record = {
                        "gear/trail": "trail",
                        "gear/trail name": hit.parent_trail_posts.name,
                        "id": hit.parent_trail_posts.id,
                        "relevance_points": 0
                    }
                    text = remove_html_tags(hit.text)
                    comment_words = [word.translate(
                        str.maketrans("", "", string.punctuation)
                    ) for word in text.lower().split()]
                    comment_word_counts = Counter(comment_words)
                    record["relevance_points"] += comment_word_counts[searched]
                    results.append(record)
    print("Trail Comments:")
    for entry in results:
        print(f"    hit: {entry['gear/trail name']} points: {entry['relevance_points']}")
    return results


def remove_html_tags(text):
    return re.sub(CLEAN, '', text)
