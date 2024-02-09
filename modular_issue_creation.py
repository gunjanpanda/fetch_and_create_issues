
# importing all the necessary libraries
import requests
from requests.auth import HTTPBasicAuth
import json
import sys
from jira import JIRA, JIRAError
from jira.exceptions import JIRAError

''' This function authenticates the user into the JIRA Server and returns generated response object if successfully authenticated else returns error code 
    which prompts the user to enter valid credentials and retry. It takes the API URL, jira username and access token as inputs and returns response 
    object upon successful authentication'''
def authenticate_user(url,username,password):
    response = requests.get(url,auth = HTTPBasicAuth(username=username,password=password),
                        headers={"Content-Type":"application/json"})
    # authentication success
    if(response.status_code == 200):
        print("Successful Authentication.\n")
        
    else:
        # authentication failure
        print("Authentication failed with status code: \n",response.status_code)
        print("Please enter valid credentials: \n")
        # stop executing code further
        sys.exit(1)
    
    # returns the response generated from successful API Authentication
    return response


''' This function fetches all the fields required to create an issue from an API. It takes response object as input to fetch the details from the provided
    API and returns the fetched data '''
def fetch_issue_fields(obj):

    # parse the received json data to a dictionary
    data = json.loads(obj.text)
    try:
        # upon successful response object creation : STATUS CODE - 200
        if(obj.status_code == 200):
            # fetching all the required details to create an issue in JIRA
            project_key = data["fields"]["project"]["key"]
            issue_summary = data["fields"]["summary"]
            issue_description = data["fields"]["description"]
            issue_type = data["fields"]["issuetype"]["name"]
            issue_priority = data["fields"]["priority"]["name"]
            issue_status = data['fields']['status']['statusCategory']['name']
            issue_component = [component['name'] for component in data["fields"]["components"]]
            issue_labels = data["fields"]["labels"]

            # displaying all the fetched data
            print("ProjectKey: ",project_key)
            print("Summary: ",issue_summary)
            print("Description: ",issue_description)
            print("IssueType: ",issue_type)
            print("IssuePriority: ",issue_priority)
            print("IssueStatus: ",issue_status)
            print("IssueLabels: ",issue_labels)
            print("IssueComponents: ",issue_component)

            # returns json data in dictionary format
            return data

    # upon failure in response object creation    
    except JIRAError as e:
        print("[ERROR] %s - %s" % (e.status_code, e))
        # stop executing code further
        sys.exit(1)
    

''' This function creates issue keeping the required fields fetched from response object. It takes API URL, JIRA username, JIRA access token 
    and json data in dictionary format as input and creates issue for the given fields. '''
def create_issue(url,username,password,obj):
    
    # header format
    headers = { "Accept": "application/json", "Content-Type": "application/json"} 

    # required fields fetched from json data 
    project_key = obj["fields"]["project"]["key"]
    issue_summary = obj["fields"]["summary"]
    issue_description = obj["fields"]["description"]
    issue_type = obj["fields"]["issuetype"]["name"]
    issue_priority = obj["fields"]["priority"]["name"]
    issue_status = obj['fields']['status']['statusCategory']['name']
    issue_component = [component['name'] for component in obj["fields"]["components"]]
    issue_labels = obj["fields"]["labels"]
            
    # except JIRAError as e:
    #     print("[ERROR] %s - %s" % (e.status_code, e))
    #     sys.exit(1)

    
    # create issue template followed
    payload = json.dumps(
        {
            "fields": {
                "project":
                {
                    "key": project_key
                },
                "summary": issue_summary ,
                "description": issue_description,
                "issuetype": {
                    "name": issue_type
                },
                "priority": {
                    "name": issue_priority
                },
                
                "labels":issue_labels,
                
                # multiple components under one issue(if required) gets created as well
                "components":[{"name": val} for val in issue_component]
                
            }

        }
    )

    # push the data to JIRA Server and create issue, this authenticates and pushes issue to JIRA
    response = requests.post(url,headers=headers,data=payload,auth=(username,password))
    
    # upon successful issue creation
    if(response.status_code == 200):
        print(f"Issue created successfully!\n {response.text}")
    else:
        # upon unsuccessful issue creation
        print(f"Failed to create issue. Status Code: {response.status_code}, please try again.")


def main():

    # taking inputs from user
    api_url = input("Enter the API url to fetch fields: ")
    username = input("Enter your jira username: ")
    access_token = input("Enter jira password: ")
    
    # storing the response object created post authentication
    issue_obj = authenticate_user(api_url,username,access_token)
    
    try:
        
        # fetch the data from API and store in data
        data = fetch_issue_fields(issue_obj)
        # creates issue
        create_issue("https://gunjandemo.atlassian.net/rest/api/2/issue/",username,access_token,data)
        
    except JIRAError as e:
        print("[ERROR] %s - %s" % (e.status_code, e))
        sys.exit(1)


    
# core: code starts from here, this triggers the rest of the functions
if __name__ == "__main__":
    main()

