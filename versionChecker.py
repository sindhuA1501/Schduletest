# import requests
#
# response = requests.get("https://api.github.com/repos/IVISECURITY/Advertisements/releases/latest")
# print(response.json())



from github import Github

# Replace YOUR_GITHUB_USERNAME and YOUR_GITHUB_PASSWORD with your GitHub credentials
g = Github("mygithub789@gmail.com", "Ivis@123#")
# Replace OWNER and REPO_NAME with the name of the repository you want to download
repo = g.get_repo("IVISECURITY/Advertisements")
import os

# Replace LOCAL_PATH with the path where you want to save the repository
local_path = "C:/Users/para sivaram/PycharmProjects/test/"

if not os.path.exists(local_path):
    os.makedirs(local_path)

repo_path = os.path.join(local_path, repo.name)

if os.path.exists(repo_path):
    repo.delete()

repo.clone(repo_path)
