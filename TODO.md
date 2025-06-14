# Features
[x] Make the frontend friendlier
[x] Update the `app.py` to allow the user to select the songs for the virtual vinyl. The use of this app is
    - User logs in into Spotify
    - Select manually the songs to be included in the new playlist (virtual vinyl)
    - Create the new playlist, called "Virtual Vinyl".
[x] Create tests for the frontend
[x] Without resizing `img/vinyl.jpg`, reduce the resolution visualization the app
[x] Use Githubs Pages to display the static website. Transform Dash frontend into HTML/js if necessary
[x] Check [website](https://cperales.github.io/virtualvinyl) is active.
[x] Convert the backend into an AWS Lambda function
[x] Remove the Flask dependency from the backend
[x] Add more loggings in the backend, replace prints for loggings
[x] After logging, the app should brings you to a website where
    - User can select manually the songs from their most listened to be included in a new playist (called `Virtual Vinyl`)
    - A link appears to the new playlist


# Bugs
[x] After logging in Spotify, I got `Missing required parameter; client_id`
[x] "Invalid callback" error after login was caused by callback page dropping query parameters
[x] After login Spotify OAuth succeeds but the callback returns `{"error": "Failed to get access token"}`. Ensure SPOTIFY_CLIENT_SECRET is set in the Lambda environment.
[ ] Besides "Select Your Tracks" and pop up "Please select between 8 and 12 songs", it does not shows anything about playlist configuration.

# Notes
[x] Redesigned Dash app to show a vinyl image and nicer styling
