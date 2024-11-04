import requests
import csv

GITHUB_API_TOKEN = ""
API_HEADERS = {"Authorization": f"token {GITHUB_API_TOKEN}"}

def fetch_bangalore_users():
    users_data = []
    search_query = "location:Bangalore+followers:>100"
    current_page = 1
    max_per_page = 100
    total_fetched_users = 0

    while True:
        url = f"https://api.github.com/search/users?q={search_query}&per_page={max_per_page}&page={current_page}"
        response = requests.get(url, headers=API_HEADERS)
        print(f"Fetching page {current_page}...")

        if response.status_code != 200:
            print("Error fetching data:", response.json())
            break

        data = response.json()
        users_data.extend(data['items'])
        total_fetched_users += len(data['items'])

        if len(data['items']) < max_per_page:
            break

        current_page += 1

    user_details = []
    for user in users_data:
        user_info = retrieve_user_details(user['login'])
        user_details.append(user_info)

    return user_details

def retrieve_user_details(username):
    user_url = f"https://api.github.com/users/{username}"
    user_info = requests.get(user_url, headers=API_HEADERS).json()

    return {
        'login': user_info['login'],
        'name': user_info['name'],
        'company': clean_company_name(user_info['company']),
        'location': user_info['location'],
        'email': user_info['email'],
        'hireable': user_info['hireable'],
        'bio': user_info['bio'],
        'public_repos': user_info['public_repos'],
        'followers': user_info['followers'],
        'following': user_info['following'],
        'created_at': user_info['created_at'],
    }

def clean_company_name(company):
    if company:
        company = company.strip().upper()
        if company.startswith('@'):
            company = company[1:]
    return company

def fetch_user_repos(username):
    repos_url = f"https://api.github.com/users/{username}/repos?per_page=500"
    response = requests.get(repos_url, headers=API_HEADERS)
    repos_info = response.json()

    repos_list = []
    for repo in repos_info:
        repos_list.append({
            'login': username,
            'full_name': repo['full_name'],
            'created_at': repo['created_at'],
            'stargazers_count': repo['stargazers_count'],
            'watchers_count': repo['watchers_count'],
            'language': repo['language'],
            'has_projects': repo['has_projects'],
            'has_wiki': repo['has_wiki'],
            'license_name': repo['license']['key'] if repo['license'] else None,
        })

    return repos_list

def save_users_to_csv(user_data):
    with open('users.csv', mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['login', 'name', 'company', 'location', 'email', 'hireable', 'bio', 'public_repos', 'followers', 'following', 'created_at'])
        writer.writeheader()
        writer.writerows(user_data)

def save_repos_to_csv(repos_data):
    with open('repositories.csv', mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['login', 'full_name', 'created_at', 'stargazers_count', 'watchers_count', 'language', 'has_projects', 'has_wiki', 'license_name'])
        writer.writeheader()
        writer.writerows(repos_data)

if __name__ == "__main__":
    users = fetch_bangalore_users()
    save_users_to_csv(users)

    all_user_repos = []
    for user in users:
        repos = fetch_user_repos(user['login'])
        all_user_repos.extend(repos)

    save_repos_to_csv(all_user_repos)
    print("Done")
