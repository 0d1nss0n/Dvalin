import re
import requests
from urllib.parse import urlparse, urljoin
from requests.packages.urllib3.exceptions import InsecureRequestWarning

print("""

                ▓▒▒▒▒▒▒▒▒▒▒▒▒▓
              ▓▒▒▒▓▓▓▒▒▒▒▒▒▒▒▒▒▒▒▓
           ▓▒▒▒▒▓████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓
          ▓▒▒▓▓█▓▒▒▒▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓
           ▓▒▒▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒█▓
           ▓▒▒▒▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒█▓
          ▓▒▒▒▒▒▒░▒▒▒▒▒▒▒▒▓▒▒▒▒▒▒▒▒▓▓
         ▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓█▓
          ▓▒▒▓▒▒▒▒▒▒▒▒▒▒▒▓▒▒▓▒▒▒▒▓█▓
        ▓██▓▓██▓▓▓▓▓▓▒▒▒▒▓██▓▒▒▒▒█▓
        ▓█▒▒▒▒▓▓█████▒▒▓▓▓████▓▒▒█▓
         ▓▓▒▒▒▓██████▓██████████▒▒▓
       ▓███▓▓▓████████████▓▓██▒▓▓▒▒▓
      ▓███████████████████▓▒█▓▓▓▓
      ▓████████████████████▓▓▓
     ▓█████████████████████▓▓
    ▓███████████████████▓█▓▓ 
    ▓████████████████▓▓
      ▓██████████▓▓
       ▓███████▓▓

██████  ██    ██  █████  ██      ██ ███    ██ 
██   ██ ██    ██ ██   ██ ██      ██ ████   ██ 
██   ██ ██    ██ ███████ ██      ██ ██ ██  ██ 
██   ██  ██  ██  ██   ██ ██      ██ ██  ██ ██ 
██████    ████   ██   ██ ███████ ██ ██   ████ 
                                              
    -Web Crawler and Scraper                                         
    -Created by: 0D1NSS0N
""")

# Disable SSL certificate verification warning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def normalize_url(url):
    url = url.strip()

    if not re.match('^https?://', url):
        url = "https://" + url

    if not url.endswith('/'):
        url += '/'

    return url

def get_robots_txt_content(url):
    normalized_url = normalize_url(url)
    robots_url = normalized_url + "robots.txt"

    try:
        response = requests.get(robots_url, timeout=5, verify=False)
        content = response.text
        response.close()
        return content
    except Exception as e:
        print(f"Error retrieving robots.txt: {e}")
        return None


def get_info_recursively(url, depth, url_hash_table, found_emails, found_addresses, found_phones, http_urls, https_urls, user_agent, in_scope_domain):
    if depth < 1:
        return

    normalized_url = normalize_url(url)

    if normalized_url in url_hash_table:
        return

    url_hash_table[normalized_url] = True

    headers = {'User-Agent': user_agent}
    
    try:
        response = requests.get(normalized_url, headers=headers, timeout=5, verify=False)
        content = response.text
        response.close()

        base_url = urlparse(normalized_url)
        urls = re.findall('href="([^"]*)"', content)
        unique_urls = set()

        for matched_url in urls:
            uri = urlparse(urljoin(normalized_url, matched_url))
            normalized_uri = normalize_url(uri.geturl())
            
            if in_scope_domain and urlparse(normalized_uri).netloc != in_scope_domain:
                continue  # Skip URLs outside of the in-scope domain
            
            if normalized_uri != normalized_url:
                unique_urls.add(normalized_uri)

        for url in unique_urls:
            if url.startswith('http://'):
                http_urls.add(url)
            elif url.startswith('https://'):
                https_urls.add(url)

        for url in unique_urls:
            get_info_recursively(url, depth - 1, url_hash_table, found_emails, found_addresses, found_phones, http_urls, https_urls, user_agent, in_scope_domain)

        emails = re.findall('[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content)
        found_emails.update(emails)
        
        addresses = re.findall('[0-9]+ [a-zA-Z ]+, [A-Z]{2} [0-9]{5}', content)
        found_addresses.update(addresses)
        
        phones = re.findall(r'\b(?:1-)?\d{3}-\d{3}-\d{4}\b', content)
        found_phones.update(phones)
    
    except Exception as e:
        print(f"Error retrieving URL: {e}")

# Example usage
def run_dvalin():
    url_hash_table = {}
    found_emails = set()
    found_addresses = set()
    found_phones = set()
    http_urls = set()
    https_urls = set()
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"

    input_url = input("Enter the URL to crawl: ")
    url = normalize_url(input_url)

    depth = int(input("Enter the depth to crawl: "))
    in_scope_domain = None

    in_scope = input("Do you want to stay In-Scope and only crawl sites of the same domain? (y/n): ")
    if in_scope.lower() == 'y':
        in_scope_domain = urlparse(url).netloc

    headers = {'User-Agent': user_agent}

    try:
        response = requests.get(url, headers=headers, timeout=5, verify=False)
        content = response.text
        response.close()

        # Fetch and display robots.txt content
        robots_content = get_robots_txt_content(url)
        if robots_content is not None:
            print("\nRobots.txt content:\n")
            print(robots_content)

            proceed = input("\nDo you want to proceed with crawling? (y/n): ")
            if proceed.lower() != 'y':
                print("Crawling aborted by the user.")
            else:
                scrape_emails = input("Do you want to scrape emails? (y/n): ")
                scrape_phones = input("Do you want to scrape phone numbers? (y/n): ")
                scrape_addresses = input("Do you want to scrape addresses? (y/n): ")

                if scrape_emails.lower() == 'y':
                    get_info_recursively(url, depth, url_hash_table, found_emails, found_addresses, found_phones, http_urls, https_urls, user_agent, in_scope_domain)

                if scrape_phones.lower() == 'y':
                    get_info_recursively(url, depth, url_hash_table, found_emails, found_addresses, found_phones, http_urls, https_urls, user_agent, in_scope_domain)

                if scrape_addresses.lower() == 'y':
                    get_info_recursively(url, depth, url_hash_table, found_emails, found_addresses, found_phones, http_urls, https_urls, user_agent, in_scope_domain)

        print("\nFound Email Addresses:")
        for email in found_emails:
            print(email)
            
        print("\nFound Addresses:")
        for address in found_addresses:
            print(address)
            
        print("\nFound Phone Numbers:")
        for phone in found_phones:
            print(phone)

        print("\nHTTP URLs:")
        for http_url in http_urls:
            print(http_url)

        print("\nHTTPS URLs:")
        for https_url in https_urls:
            print(https_url)
            
        save_output = input("\nDo you want to save the output? (y/n): ")
        if save_output.lower() == 'y':
            domain_name = urlparse(url).netloc.replace(".", "_")
            if found_emails:
                with open(f"{domain_name}_emails.txt", "w") as f:
                    for email in found_emails:
                        f.write(email + "\n")
                print("Emails file saved successfully.")
                
            if found_phones:
                with open(f"{domain_name}_phones.txt", "w") as f:
                    for phone in found_phones:
                        f.write(phone + "\n")
                print("Phone Numbers file saved successfully.")
            
            if found_emails:
                with open(f"{domain_name}_address.txt", "w") as f:
                    for address in found_addresses:
                        f.write(address + "\n")
                print("Address file saved successfully.")
            
            if http_urls:
                with open(f"{domain_name}_http_urls.txt", "w") as f:
                    for http_url in http_urls:
                        f.write(http_url + "\n")
                print("HTTP URLs file saved successfully.")
            
            if https_urls:
                with open(f"{domain_name}_https_urls.txt", "w") as f:
                    for https_url in https_urls:
                        f.write(https_url + "\n")
                print("HTTPS URLs file saved successfully.")

    except Exception as e:
        print(f"Error retrieving URL: {e}")

if __name__ == "__main__":
    run_dvalin()
