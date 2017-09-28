import pytest

import CNSCrawler

def test_log_reading():
    # setting long time to check log for, almost guaranteed
    # to see some issue in the log
    CNSCrawler.POLL_TIME_MINUTES = 30000000
    tool_id = CNSCrawler.tool_dict["Elionix"]

    tool_issue = CNSCrawler.check_tool_issues(tool_id)

    # test passes if we see some issue with the tool
    print("The last tool issue with the Elionix reads:\n{}".format(tool_issue))
    assert tool_issue
