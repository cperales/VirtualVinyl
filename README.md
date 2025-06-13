# VirtualVinyl

This repository contains the code for the VirtualVinyl App. Instead of playing a long Spotify playlist, why not select a curated playlist of 8 to 12 songs to become your today's soundtrack? [Click here to discover](https://cperales.github.io/VirtualVinyl).


## Backend setup

The `app.py` file is uploaded at AWS as a lambda.

### Environment variables

The backend requires two Spotify credentials provided as environment variables:

```
SPOTIFY_CLIENT_ID=<your client id>
SPOTIFY_CLIENT_SECRET=<your client secret>
```

Make sure these variables are configured in the Lambda function or in a local
`.env` file when running the backend locally. Missing credentials will lead to
`Failed to get access token` errors during the OAuth callback.

### Logging

The backend now uses Python's `logging` module. Log messages are printed to
standard output, viewable in CloudWatch when deployed on AWS Lambda or in the
console during local development.
