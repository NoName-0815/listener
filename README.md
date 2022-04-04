# webhook listener

This repo is the home of listener.py. A program that, once started, will listen for 'create' webhooks for new repositories.

These webhooks are sent from Github and will cause listener.py to set up protection on the main branch of the newly created repo. 
The idea is to have a default minimum set of reviewers for pull requests as well as the review of the code owner.
The minimum is set to 2 reviewers for now. Since this is a hard requirement, it's hard-coded and can't be changed in order to ensure policy enforcement. 

## PreRequisites

For the listener to work correctly, it is necessary that these requisites are met:
1. The new repo must be derived from the template repo (so that it automatically creates the main branch with the README.md in it)
2. The new repo must be public (this is just a limitation for free accounts on github, for enterprise accounts this is not true)
3. A valid github token that grants access to the organization you're working on (https://github.com/settings/tokens)

All 3 requirements are set up for the NoName-0815 organization which can act as an example. 


## Installation 

The listener.py can run on any system with python3 available. It will need to install a few python packages. If these are not part of your system anyway, pip can install them in a virtual python environment, but that's not covered in this document

### Setting it up and running it

It's as simple as cloning the repo, changing into it and running the python program:

```bash
git clone https://github.com/NoName-0815/listener.git
cd listener
export GITHUB_TOKEN=<your_github_token>
python3 listener.py -g <github_handle> -p <port>
```
The listener.py program has two parameters: 
1. A github handle: When the protection gets set up, listener.py will create an issue and mention the github user in there. 
2. A port: This is the tcp port at which listener.py will wait for webhooks.

### Configuring github to send webhooks to your listener

Follow github's guide to set up webhooks on an organizational level and make sure you have either all of them, or at least the ones for repo creation enabled (https://docs.github.com/en/developers/webhooks-and-events/webhooks/creating-webhooks).
Set the *Payload URL* to the hostname or IP you're running the listener on, similar to this:

`http://<hostname or IP>:<port>/hooks`

The *hooks* part at the end is important, it's the path to our application. 

### Using it

With the above steps done, the listener's setup is complete and it will now set the number of reviewers required for a PR to 2 on every newly created main branch as well as it will require the code owner's review for a PR. 
Every time the listener does this, it will also create a new issue in the repo's main branch, informing the owner of the used github handle about the performed actions. 


