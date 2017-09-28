import os
import time
import datetime

import requests
from bs4 import BeautifulSoup

from slackclient import SlackClient

POLL_TIME_MINUTES = 30
print("starting..")
slack_client = SlackClient(os.environ.get("SLACK_BOT_TOKEN"))

tool_dict = {"Elionix": 304,
             "RIE-8": 173,
	     "IBE": 437,
	     "CVD-3": 180}
clean_url = "http://clean.fas.harvard.edu"

def check_tool_issues(tool_id):

    soup = get_tool_soup(tool_id)
    log_table = get_user_log(soup)
    rows = soup.find_all("tr", {"class":"logsheet"}, recursive=True)

    nowdate = datetime.datetime.now()
    logmsgs = []
    for row in rows:
        if is_valid_entry(row):
            logdate = get_entry_date(row)
            if ((nowdate - logdate) <= datetime.timedelta(minutes=POLL_TIME_MINUTES)):
                logmsgs.append(get_entry_msg(row))
            else:
                break
    issuemsg = get_user_issue(logmsgs)
    if issuemsg:
        return issuemsg
    else:
        return []

def get_tool_soup(tool_id):
    with requests.Session() as session:
        
        # parsing parameters
        response = session.get(clean_url)
        soup = BeautifulSoup(response.content)
        #tid : 304 is Elionix F125, find others by inspecting clean.fas.harvard.edu
        data = {
            'tid': str(tool_id)
        }

        # parsing data
        response = session.post(clean_url, data=data)

        soup = BeautifulSoup(response.content)
    return soup

def get_user_log(soup):
    return soup.findChildren("table")[6]

def is_valid_entry(row):
    cells = list(row.children)
    return cells[0] != '\n'

def get_entry_date(row):
    cells = list(row.children)
    cell_date = cells[0].acronym['title'][-17:-3]
    logdate = datetime.datetime.strptime(cell_date, '%y-%m-%d %H:%M')
    return logdate
        
def get_entry_msg(row):
    cells = list(row.children)
    return list((list(row.children)[-2].children))[0]

def get_user_issue(logmsgs):
    sentiment_list = ['broke',
                      'issue',
                      'error', 
                      'not working',
                      'stopped working',
                      'couldn\'t run',
                      'could not run',
                      'unable',
		      'does not work',
		      'doesn\'t work',
		      'crash',
		      'does not start',
		      'doesn\'t start',
		      'problem']
    
    for logmsg in logmsgs:
        if any(sentiment in logmsg for sentiment in sentiment_list):
            return logmsg
    return []

def post_tool_issue(user_issue, tool_name):
    tool_text = "Oh no! It looks like a user has reported an issue with the {}! Here's the latest log entry:\n\n>{}".format(tool_name, user_issue)
    slack_client.api_call(
            "chat.postMessage",
            channel="#cleanroom-related",
            text=tool_text
    )

if __name__ == "__main__":
    crawler_sleep = 60 * POLL_TIME_MINUTES # 30 minute delay 
    print("CNSCrawler connected and running!")
    while True:
        for tool_name, tool_id in tool_dict.items():
            tool_issue = check_tool_issues(tool_id)
            if tool_issue:
                print("There's a problem with {}! posting...".format(tool_name))
                post_tool_issue(tool_issue, tool_name)
            else:
                print("No problem with {}!".format(tool_name))
        time.sleep(crawler_sleep)
