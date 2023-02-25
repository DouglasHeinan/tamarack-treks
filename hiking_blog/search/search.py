"""This file handles site-wide search functionality."""
from flask import Blueprint, render_template, current_app
from hiking_blog.forms import SearchForm
from hiking_blog.models import Gear, GearComments, Trails, TrailComments
from hiking_blog.admin.admin import NO_TAGS, NO_CHARS
from collections import Counter
import operator
import re

search_bp = Blueprint(
    "search_bp", __name__,
    template_folder="templates",
    static_folder="static"
)


@current_app.context_processor
def send_form_to_navbar():
    """In the app context, this sends the search form to the navbar on all pages."""
    form = SearchForm()
    return dict(form=form)


# ----------------------------------------PARENT SEARCH FUNCTIONS----------------------------------------
@search_bp.route("/search/search", methods=["POST"])
def search():
    """
    Takes in the user-input to be searched and returns a list of all pages on the site containing relevant information.

    When the user submits the search form, this function runs the input through several other functions to clean the
    input of any non-letter characters and create a sorted list of pages related to the user's input.
    """
    form = SearchForm()
    if form.validate_on_submit():
        searched = form.searched.data
        print(searched)
        clean_search = create_search_list(searched)
        print(f"SEARCH: {clean_search}")
        results = run_search_functions(clean_search)
        sorted_results = sorted(results, reverse=True, key=operator.itemgetter("relevance_points"))
        final_results = get_final_results(sorted_results)
        print(f"final results: {final_results}")
        return render_template(
            "search.html",
            form=form,
            searched=searched,
            final_results=final_results,
        )
    return render_template(
        "search.html",
        form=form,
        searched="",
        final_results=None
    )


def create_search_list(searched):
    """
    Cleans every string in a list of strings, removing all non-letter characters.

    Takes in a user-input string of characters from the search function and removes all non-letter characters before
    appending the string to a new list consisting only of cleaned strings.

    PARAMETERS
    ----------
    searched : str
        A user-input string of characters.
    """

    search_list = searched.split()
    clean_search = []
    for word in search_list:
        clean_word = re.sub(NO_CHARS, '', word).lower()
        if clean_word != "":
            clean_search.append(clean_word)
    return clean_search


def run_search_functions(search_list):
    """
    Runs all of the specific search functions for a list of user input strings.

    Creates an empty list which will eventually store all of the information for pages that have data matching one or
    more of the user-input search terms. This function then calls several search functions, attempting to match specific
    strings from a list of strings input by the user to words or phrases associated with specific pages of the app.

    PARAMETERS
    ----------
    search_list : list
        A list of user-input strings.
    """

    results = []
    results = check_gear_and_trail_review_names(search_list, results)
    results = check_gear_review_keywords(search_list, results)
    results = check_gear_and_trail_review_content(search_list, results)
    results = check_gear_and_trail_review_comments(search_list, results)
    results = check_exact_name_in_search(search_list, results)
    return results


# ----------------------------------------SEARCH FUNCTIONS----------------------------------------
def check_gear_and_trail_review_names(searched, results):
    """
    Looks for trail and gear-piece names in the database that match the user-input search terms.

    Iterates through every string in the list of user-input strings to be searched, queries the database to see if any
    trail or gear-piece names match the string, and calls a separate function to update the list of results if there
    are any matches.

    PARAMETERS
    searched : list
        A list of all individual words, in string form, input by the user into the search form.
    results : list
        A list of dictionaries. Each contained dictionary stores relevant info for pages with data matching searched
        strings.
    """

    to_check = "names"
    if searched:
        for search_item in searched:
            hits = (Gear.query.filter(Gear.name.like(f"%{search_item}%")).all()) + \
                   (Trails.query.filter(Trails.name.like(f"%{search_item}%")).all())
            if hits:
                results = add_or_adjust_entries_against_search_term_relevance(hits, results, to_check, search_item, 10)
    print_results("Names", results)
    return results


def check_gear_review_keywords(searched, results):
    """
    Looks for trail and gear-piece keywords in the database that match the user-input search terms.

    Iterates through every string in the list of user-input strings to be searched, queries the database to see if any
    trail or gear-piece keywords match the string, and calls a separate function to update the list of results if there
    are any matches.

    PARAMETERS
    ----------
    searched : list
        A list of all individual words, in string form, input by the user into the search form.
    results : list
        A list of dictionaries. Each contained dictionary stores relevant info for pages with data matching searched
        strings.
    """

    to_check = "keywords"
    if searched:
        for search_item in searched:
            hits = Gear.query.filter(Gear.keywords.like(f"%{search_item}%")).all()
            if hits:
                results = add_or_adjust_entries_against_search_term_relevance(hits, results, to_check, search_item, 7)
    print_results("Keywords", results)
    return results


def check_gear_and_trail_review_content(searched, results):
    """
    Looks for trail and gear-piece content in the database that match the user-input search terms.

    Iterates through every string in the list of user-input strings to be searched, queries the database to see if any
    trail or gear-piece descriptions match the string, and calls a separate function to update the list of results if
    there are any matches.

    PARAMETERS
    ----------
    searched : list
        A list of all individual words, in string form, input by the user into the search form.
    results : list
        A list of dictionaries. Each contained dictionary stores relevant info for pages with data matching searched
        strings.
    """

    to_check = "content"
    if searched:
        for search_item in searched:
            hits = (Gear.query.filter(Gear.description.like(f"%{search_item}%")).all()) + \
                   (Trails.query.filter(Trails.description.like(f"%{search_item}%")).all())
            if hits:
                results = add_or_adjust_entries_against_search_term_relevance(hits, results, to_check, search_item, 3)
    print_results("Content", results)
    return results


def check_gear_and_trail_review_comments(searched, results):
    """
    Looks for trail and gear-piece comments in the database that match the user-input search terms.

    Iterates through every string in the list of user-input strings to be searched, queries the database to see if any
    trail or gear-piece comments match the string, and calls a separate function to update the list of results if there
    are any matches.

    PARAMETERS
    ----------
    searched : list
        A list of all individual words, in string form, input by the user into the search form.
    results : list
        A list of dictionaries. Each contained dictionary stores relevant info for pages with data matching searched
        strings.
    """

    to_check = "comments"
    if searched:
        for search_item in searched:
            hits = (GearComments.query.filter(GearComments.text.like(f"%{search_item}%")).all()) + \
                   (TrailComments.query.filter(TrailComments.text.like(f"%{search_item}%")).all())
            if hits:
                results = add_or_adjust_entries_against_search_term_relevance(hits, results, to_check, search_item, 1)
    print_results("Comments", results)
    return results


def check_exact_name_in_search(searched, results):
    """
    Checks if gear/trail_name of any entry in 'results' contains all words matching searched strings.

    Iterates through every entry in the 'results' list to check if the gear/trail_name of the entry contains exclusively
    words that are included in the list of strings input by the user in the search form.

    PARAMETERS
    ----------
    searched : list
        A list of all individual words, in string form, input by the user into the search form.
    results : list
        A list of dictionaries. Each contained dictionary stores relevant info for pages with data matching searched
        strings.
    """

    for listing in results:
        listing_entry_words = listing["gear/trail_name"].lower().split()
        searched_for_product_name = all(item in searched for item in listing_entry_words)
        if searched_for_product_name:
            listing["relevance_points"] += 1000
    print_results("Exact Name", results)
    return results


# ----------------------------------------UTILITY FUNCTIONS----------------------------------------
def add_or_adjust_entries_against_search_term_relevance(hits, results, to_check, search_item, hit_value):
    """
    Adds new entries to the 'results' list, as well as adjusting entries already included in the list.

    Most of the search functions call this function. It iterates through the list of hits, which are all the gear and
    trail entries with data matching the current search_item. It then compares the hit to every listing in the 'results'
    list to see if the information from that page is already included in the list. If it is already included, the
    current listing is adjusted. The adjustment is to the 'relevance_points' key of the relevant listing. Different
    texts being searched through (the name of the gear or trail object is one kind of text, the comments of an object
    are another) have different values. Matching a search term to an object's name is more valuable than matching it to
    one word from an object's comments. When adjusted, a listing's 'relevance_points' are adjusted up by a value equal
    to the number of times the search_item appears in the text being examined multiplied by the hit_value, which is
    assigned by the function calling this function in order to properly weight the importance of the match.

    PARAMETERS
    ----------
    hits : list
        An list of gear or trail objects from the database with data matching one or more of the user-input search
        strings.
    results : list
        A list of dictionaries. Each contained dictionary stores relevant info for pages with data matching searched
        strings.
    to_check : str
        A string set by the function calling this function; used to determine which table in the database this function
        needs to access.
    search_item : str
        One of the user-input strings from the search form.
    hit_value : int
        A number assigned by the function calling this function. It's used as a modifier to the listing's
        'relevance_points'.
    """

    for hit in hits:
        text, name = set_adjustment_variables(to_check, hit)
        entry_change = False
        for listing in results:
            if name == listing["gear/trail_name"].lower():
                adjustment = clean_and_count_words(text, search_item)
                listing["relevance_points"] += adjustment * hit_value
                entry_change = True
        if not entry_change:
            listing = make_new_listing(hit, to_check)
            adjustment = clean_and_count_words(text, search_item)
            listing["relevance_points"] += adjustment * hit_value
            results.append(listing)
    return results


def set_adjustment_variables(to_check, hit):
    """Sets two variables for the 'add_or_adjust_entries_against_search_term_relevance' function."""
    text = None
    name = None
    if to_check == "names":
        text = hit.name.lower()
        name = hit.name.lower()
    elif to_check == "keywords":
        text = hit.keywords.lower()
        name = hit.name.lower()
    elif to_check == "content":
        text = hit.description.lower()
        name = hit.name.lower()
    elif to_check == "comments":
        text = hit.text.lower()
        name = hit.parent_posts.name.lower()
    return text, name


def make_new_listing(hit, to_check):
    """
    Creates a new entry to be appended to the 'results' list.

    This function is called when one of the search functions has identified a page with data relevant to one or more of
    the user-input search strings, but no entry for that page exists in the 'results' list. This function then creates
    that entry.

    PARAMETERS
    ----------
    hit : class
        A gear or trail object identified in another function as having data matching one or more of the user-input
        search strings.
    to_check : str
        A string set by the function calling this function; used to determine which table in the database this function
        needs to access.
    """

    if to_check == "comments":
        listing = {
            "gear/trail": hit.parent_posts.gear_trail,
            "gear/trail_name": hit.parent_posts.name,
            "id": hit.parent_posts.id,
            "relevance_points": 0
        }
    else:
        listing = {
            "gear/trail": hit.gear_trail,
            "gear/trail_name": hit.name,
            "id": hit.id,
            "relevance_points": 0
        }
    return listing


def clean_and_count_words(text, search_item):
    """
    Removes unwanted characters from strings and counts occurrences of searched term in a text.

    Cleans the text by removing all html tags (the text editor used for comments and descriptions returns <p> tags) and
    non-letter characters. After doing so, counts all words in the text and returns a variable equal to the number of
    times the search_item appears in the text.

    PARAMETERS
    ----------
    text :
        The text from a part of page currently being checked for occurrences of the search_item.
    search_item : str
        One of the user-input strings from the search form.
    """

    no_tag_text = re.sub(NO_TAGS, '', text).lower()
    word_list = no_tag_text.split()
    clean_word_list = []
    for word in word_list:
        clean_word = re.sub(NO_CHARS, '', word)
        clean_word_list.append(clean_word)
    text_word_counts = Counter(clean_word_list)
    adjustment = text_word_counts[search_item]
    return adjustment


def get_final_results(sorted_results):
    the_list = []
    for result in sorted_results:
        if result["gear/trail"] == "Gear":
            new_result = Gear.query.get(result["id"])
        else:
            new_result = Trails.query.get(result["id"])
        the_list.append(new_result)
    return the_list


def print_results(category, results):
    """Prints to the terminal info useful to the developer."""
    print(f"{category} Check:")
    if results:
        for entry in results:
            print(f"    hit: {entry['gear/trail_name']} points: {entry['relevance_points']}")
