
import requests
from requests.auth import HTTPBasicAuth
import json
import sys
from jira import JIRA, JIRAError
from jira.exceptions import JIRAError

def authenticate_user(url,username,password):
    response = requests.get(url,auth = HTTPBasicAuth(username=username,password=password),
                        headers={"Content-Type":"application/json"})
    if(response.status_code == 200):
        print("Successful Authentication.\n")
        
    else:
        print("Authentication failed with status code: \n",response.status_code)
        print("Please enter valid credentials: \n")
        sys.exit(1)
    return response


def fetch_issue_fields(obj):
    data = json.loads(obj.text)
    try:
        if(obj.status_code == 200):
            project_key = data["fields"]["project"]["key"]
            issue_summary = data["fields"]["summary"]
            issue_description = data["fields"]["description"]
            issue_type = data["fields"]["issuetype"]["name"]
            issue_priority = data["fields"]["priority"]["name"]
            issue_status = data['fields']['status']['statusCategory']['name']
            issue_component = [component['name'] for component in data["fields"]["components"]]
            issue_components= issue_component[0]
            issue_labels = data["fields"]["labels"]
            print("ProjectKey: ",project_key)
            print("Summary: ",issue_summary)
            print("Description: ",issue_description)
            print("IssueType: ",issue_type)
            print("IssuePriority: ",issue_priority)
            print("IssueStatus: ",issue_status)
            print("IssueLabels: ",issue_labels)
            print("IssueComponents: ",issue_component)
            return data
    except JIRAError as e:
        print("[ERROR] %s - %s" % (e.status_code, e))
        sys.exit(1)
    

def create_issue(url,username,password,obj):
    
    headers = { "Accept": "application/json", "Content-Type": "application/json"} 
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
                
                "components":[{"name": val} for val in issue_component]
                
            }

        }
    )

    response = requests.post(url,headers=headers,data=payload,auth=(username,password))
   
    if(response.status_code == 200):
        print(f"Issue created successfully!\n {response.text}")
    else:
        print(f"Failed to create issue. Status Code: {response.status_code}, please try again.")


def main():

    api_url = input("Please enter the API url to fetch fields: ")
    username = input("Enter your jira username: ")
    access_token = input("Enter jira password: ")
    
    issue_obj = authenticate_user(api_url,username,access_token)
    
    try:
        
        data = fetch_issue_fields(issue_obj)
        create_issue("https://gunjandemo.atlassian.net/rest/api/2/issue/",username,access_token,data)
    except JIRAError as e:
        print("[ERROR] %s - %s" % (e.status_code, e))
        sys.exit(1)


    

if __name__ == "__main__":
    main()

