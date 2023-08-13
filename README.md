# Tamarack Treks
## An outdoor gear and trail resource for hikers and campers in Montana

This project is a demo outdoor enthusiast guide. The notion is that this would be a family-friendly resource for hikers 
and backpackers looking for community feedback and other information about the trails of western Montana and the gear 
necessary to hike them. Users are able to contribute trail photos, reviews, comments, find good prices on gear, get directions to local 
trailheads and more.

This website can be accessed at [douglasheinan.com/tamarack-treks](http://douglasheinan.com/tamarack-treks).

## Key Features
**Languages/technologies:** HTML, CSS, Javascript, Python, Flask, Jinja, SQLLite, Bootstrap

This project was written mostly in Python. I wanted to create a fairly straightforward webpage that utilized a number
of my skills. To that end: 
* I utilized Flask's Application Factory pattern to create a multi-page web application
* I used the flask-login library to create standard user and admin functionality such as logins, profiles, and admin oversight
* I created an effective Python full-text search engine with ranked results from scratch
* I used SQLLite to create a database to store all gear and trail related information on my site
* Using the Beautiful Soup library, I created a constantly running web scraper to automate database updates
* I designed each web page using original CSS code and some Bootstrap

## Takeaways
This is the first completely original, fully functional application I've ever made and, as such, there were *a lot* of
hard lessons learned. 

* Password reset tokens were necessary, but I had never worked with them before. Figuring out how to implement them on 
the fly was a challenge.

* I'm extremely proud of the search engine I've built from the ground up. I haven't built a search engine before, so my 
solution was to create an application that takes a user-input string, turns that string into a list, cleans each word 
in the list, and iterates through every entry in the database, 
looking for matches. The application ranks the matches with a point system and arranges the list of returned results 
from high to low.

* I also created a program that automated the deletion of old/unnecessary image files and updated the prices of gear 
items featured on the site. This was very time consuming because I tried a number of different approaches before 
finding a solution. The solution I landed on was to create a whole new application that ran concurrently with the 
main app.

* I used this project as an opportunity to improve my CSS comprehension. Instead of relying heavily on Bootstrap like 
I have in the past, I implemented original CSS solutions to personalize my site. 

* I found Flask's Application Factory formula a little hard to wrap my head around at first. Having used it 
extensively in this project, many of its weird idiosyncrasies are now second nature to me.

## Future Features
* Add user-ratings to gear and trail pages
* Allow users to DM or otherwise connect with each other outside of comment fields
* Add campsite listings and user reviews
* Add application that takes in user filters to recommend campsite or hiking trail locations
* Replace admin created reviews with user reviews

## Contact
Creator: Douglas Heinan

Email: dougheinan@gmail.com
