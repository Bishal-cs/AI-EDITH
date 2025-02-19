import json
import subprocess
import webbrowser
try :
    from googlesearch import search  # pip install googlesearch-python
except ModuleNotFoundError:
    subprocess.run("pip install googlesearch-python")
    from googlesearch import search

try:
    with open("Data\\websites.json", "r") as file:
        websites = json.load(file)
except FileNotFoundError:
    websites = {}

def google_search_website(name):
    try:
        for url in search(name, num_results=1):
            return url
    except Exception as e:
        print(f"Error searching for {name}: {e}")
        return None

def add_website_to_json(name, url):
    websites[name] = url
    with open("Data\\websites.json", "w") as file:
        json.dump(websites, file, indent=4)

def open_website(webname):
    website_name = webname.lower().split()
    counts = {}

    for name in website_name:
        counts[name] = counts.get(name, 0) + 1

    urls_to_open = []
    for name,count in counts.items():
        if name in websites:
            urls_to_open.extend([websites[name]] * count)
        else:
            url = google_search_website(name)
            if url:
                print(f"Adding new website {url} to websites.json")
                add_website_to_json(name, url)
                urls_to_open.extend([url] * count)
            else:
                print(f"No website found for {url} on Google")

    for url in urls_to_open:
        webbrowser.open(url)
    
    if urls_to_open:
        print("Opening websites...")
    else:
        print("No websites to open.")

if __name__ == "__main__":
    open_website("gfg")