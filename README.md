# cns-crawler

This is a simple script which queries clean.fas.harvard.cns for user log entries
for certain tools, and posts to a slack channel is there is an issue.

The queries are set to run every 30 minutes.

## Note

* The server on which this script runs must be in the same local network as
clean.fas.harvard.edu.

* You must have a Slack API key to be able to post to Slack
