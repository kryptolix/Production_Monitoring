# Production_Monitoring
A toolkit, that gets the remaining production volume, WIP-goods and shows them on a local html-file.
Target is a manual, daily update via Email, since I don't want to use the company-network and have no access to the ERP for such a short-term project.
The Python-Script runs every 5 min called from a crontab, gets every unread mail with the correct beginning of the subject, adds the new numbers to the main.js-file. The HTML-site then does an automatic reload every 60sec. Chart.js was used for the graph, that gets generated in the JS-file.

I didn't add the credentials.json and the token.pickle for the Google OAuth-Service for obvious reasons.
You get the credentials from the Google API-dashboard, where you need to register for the Gmail-API.

![Screenshot Dashboard](https://github.com/kryptolix/Production_Monitoring/assets/77025261/d65b2687-a389-4a53-8d47-720b6169dee7)

