# RADIO-FRIENDLY

#### Video Demo: <https://youtu.be/qrylJmBm_60>

#### Description:

Hi, there! Radio-Friendly is a web application for music lovers, especially for those who has a Last.fm profile.
For those unfamiliar with this service. Last.fm let users track all the artists and music they play in all platforms and devices.
Then, with all the data tracked from the user, the service creates several charts, such as Weekly Top Songs Played, Overall Top Artists and so on.

As someone who consumes music daily, I always wanted to develop applications aimed at this niche. Since this is the first web application I've
coded in my whole life and I'm new to programming, it has very simple and straighforward features.

Radio-Friendly was built based on the API documentation. Every data displayed is directly and dinamically retrieved from the Last.fm database.

**IMPORTANT: Across Radio-Friendly and in this document, the word "playcount", i.e, the number os plays of a specific artist of track, is regarded as "scrobble".**

After registering into Radio-Friendly, users can have quick access to their several information and charts:

- User Info;
- Recent Played Tracks;
- Weekly Charts;
- All Time Top Tracks;
- All Time Top Artists;
- All Time Top Albums.

In addition to query into their personal profile information and charts, users can also check other Last.fm profiles.

#### Main Features:

- Run a Query: The index page. Users can search for any valid Last.fm profile, then choose one of the options below:
    - User Info: Return the Last.fm info data of the Last.fm profile, including:
    	- Real name;
    	- Country of origin;
    	- User's total scrobbles;
    	- Data of registration;
    	- Link to user's Last.fm profile.
    - Recent Played Tracks: Returns a chart with the tracks played recently of the entered Last.fm profile.
    - Weekly Charts: Returns a weekly chart with the top 10 tracks, top 10 artists and top 10 albums of the entered Last.fm profile.
    - All Time Top Tracks: Returns an all time chart with the top 10 tracks of the entered Last.fm profile.
    - All Time Top Artists:Returns an all time chart with the top 10 artists of the entered Last.fm profile.
    - All Time Top Albums: Returns an all time chart with the top 10 albums of the entered Last.fm profile.

#### File Description:

/root
- application.py: The main web application python file.
- database.db: The web application database. It's composed of two tables:
	- users: includes the fields "id" (primary key), "username" and "hash(password)"
	- user_data: includes the fields  "id", "user id" (which is the foreing key to users.id) and userlastfmusername (the chosen Last.fm profile)
- helpers.py: It contains some of the key functions of the application:
- requirements: Its contains all the necessary libraries to run the application.

/static
- favicon.ico: it stores the application favicon.
- script.js: It contains all the Javascripts used in the application.
- styles.css: The main CSS stylesheet.

/templates
- about.html: A brief text on how the application works.
- account_settings.html: It let users check their Radio-Friendly information, as well as changing some information, such as:
	- Email;
	- Password;
	- Last.fm Username.
- apology.html: It contains the rendering and template of the apology error message.
- feedback.html: It let users send feedback on the web application through email.