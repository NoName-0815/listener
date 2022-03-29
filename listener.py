from flask import Flask, request
import requests
from github_webhook import Webhook
import os
import json
import sys
import getopt

# the token is an env variable set in .bashrc
github_token = os.environ["GITHUB_TOKEN"]

# Flask module settings
app = Flask(__name__)  # Standard Flask app
webhook = Webhook(app)  # Defines '/postreceive' endpoint

def main(argv):
    port = ''
    global handle 
    try:
        opts, args = getopt.getopt(argv,"hg:p:",["handle=","port="])
    except getopt.GetoptError:
        print ('listener.py -g <github_handle> -p <port>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('listener.py -g <github_handle> -p <port>')
            sys.exit()
        elif opt in ("-g", "--github_handle"):
            handle = arg
        elif opt in ("-p", "--port"):
            print("opt is p", arg)
            port = arg
    return port



def setup_branch(my_owner, my_repo, my_branch):
    # construct the url, the headers and the data for the request to the GH API
    prot_url = f"https://api.github.com/repos/{my_owner}/{my_repo}/branches/{my_branch}/protection"
    my_headers = {"Authorization": f"token {github_token}"}
    my_data = {
        "required_status_checks": None,
        "enforce_admins": None,
        "required_pull_request_reviews": {
            "dismissal_restrictions": {},
            "dismiss_stale_reviews": False,
            "require_code_owner_reviews": True,
            "required_approving_review_count": 2,
        },
        "restrictions": None,
    }

    try:
        setprot = requests.put(
            url=prot_url, headers=my_headers, data=json.dumps(my_data)
        )
        setprot.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    # turn the result into pretty json we'll use for the issue later
    parsed = json.loads(setprot.text)
    pretty = json.dumps(parsed, indent=4, sort_keys=True)

    # create the issue
    issue_url = f"https://api.github.com/repos/{my_owner}/{my_repo}/issues"
    issue_body = f"@{handle} - protection has been setup like this:\r\n {pretty}"
    issue_data = {"title": "Protection successfully enabled!", "body": issue_body}
    try:
        issue = requests.post(
            url=issue_url, headers=my_headers, data=json.dumps(issue_data)
        )
        issue.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)


# catchall for Flask
@app.route("/")
def hello_work():
    return "Hello World!"


# /hooks is the path we send our webhooks to
@app.route("/hooks", methods=["POST"])
def githubIssue():
    data = request.json
    event = request.headers.get("X-GitHub-Event")
    # We're only interested in create events
    if event == "create":
        # We need the current owner, repo and branch
        my_owner = data["repository"]["owner"]["login"]
        my_repo = data["repository"]["name"]
        my_branch = data["master_branch"]
        setup_branch(my_owner, my_repo, my_branch)

    return "OK"


if __name__ == "__main__":
    my_port = main(sys.argv[1:])
    app.run(host="0.0.0.0", port=my_port)
