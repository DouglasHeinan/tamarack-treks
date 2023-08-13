# Tamarack Treks- Outdoor Gear and Trail Resource
## A resource for hikers and campers in Montana

This project is a demo outdoor enthusiast guide. The notion is that this would be a family-friendly resource for hikers 
and backpackers looking for community feedback and other information about the trails of western Montana and the gear 
necessary to hike them. Users are able to share trail photos, find good prices on gear, get directions to local 
trailheads and more.

This webpage can be accessed at [douglasheinan.com/tamarack-treks](http://douglasheinan/tamarack-treks.com).

## Key Features...
**Languages/tech used:** HTML, CSS, Javascript, Python, Flask, Jinja, SQLLite, Bootstrap

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

Getting password reset tokens to work was a giant pain. I knew nothing of using tokens when I started this project and 
had to learn on the fly.

The search engine was a big project that I am super proud of. I've never built one before and I didn't really look 
anything up on how to build them effectively. I just sort of made up a search engine and I'm really happy with how it 
works.

Creating a program that automated the deletion of old/unnecessary image files was very time consuming. I had to 
familiarize myself with some libraries I'd never heard of to get it all to work. Similarly, I would not have thought 
when I started this thing that I'd be able to automate the process for web-scraping prices from several sites 
effectively and accurately.

I felt very unconfident in my CSS skills coming into this project. I feel making myself handle my own site design 
instead of relying exclusively on Bootstrap (as was my original plan) gave me a lot more practice in a language I've 
mostly been trying to avoid.

I found Flask's Application Factory formula a little hard to wrap my head around at first. But now, having used it 
extensively in this project, many of its weird idiosyncrasies are now second nature to me.

