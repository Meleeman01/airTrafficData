import requests
import os
import tarfile
import gzip
import sys
import shutil
import subprocess
# GitHub repository information
repo_owner = 'adsblol'
repo_name = 'globe_history_2023'

#utility functions
def is_gzipped(filepath):
    with open(filepath, 'rb') as test_f:
        return test_f.read(2) == b'\x1f\x8b'

#=======================================================end utility functions===================================================//

def fetch_releases(page=1):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases?page={page}&per_page=10"  # Adjust per_page if needed
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve releases. Status code: {response.status_code}")
        return None

def download_asset(asset_url, file_name):
    response = requests.get(asset_url)
    
    if response.status_code == 200:
        with open(file_name, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded {file_name}")
        return True
    else:
        print(f"Failed to download {file_name}. Status code: {response.status_code}")
        return False

def extract_tar_to_folder(file_name, release_name):
    """Extract a tar file into a folder named after the release."""
    if file_name.endswith(".tar") or file_name.endswith(".tar.gz") or file_name.endswith(".tgz"):
        try:
            folder_name = release_name.replace(" ", "_").replace("/", "_")
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)
            
            with tarfile.open(file_name, "r:*") as tar:
                tar.extractall(path=folder_name)
                print(f"Extracted {file_name} into folder: {folder_name}")
        except Exception as e:
            print(f"Failed to extract {file_name}: {e}")

def unpack_data(release_name,asset):
    current_dir = os.getcwd()
    traces_dir = f'{current_dir}/{release_name}/traces'
    heatmap_dir = f'{current_dir}/{release_name}/heatmap'
    acas_dir = f'{current_dir}/{release_name}/acas'

    os.chdir(traces_dir)

    print(os.getcwd(),traces_dir)

    #first go through traces directory
    for root, dirs, files in os.walk(traces_dir):

        for file in files:
            if file.endswith('.json'):
                #check that its actually a json file first
                file_path = os.path.join(root, file)
                gz_path = os.path.join(root,file[:-5])+'.gz'
                if is_gzipped(file_path):
                    #file_path = os.path.join(root, file)
                    
                    print(gz_path, file[:-5])
                    os.rename(file_path,gz_path)
                    # sys.exit()

                    # Unpack the .gz file
                    with gzip.open(gz_path, 'rb') as f_in:
                        with open(file_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    os.remove(gz_path)
                    print(f"Unpacked {gz_path} to {file_path}")
                else:
                    print("trace already unpacked!")
                
    #next go through heatmap directory
    os.chdir(heatmap_dir)

    print(os.getcwd(),heatmap_dir)
    # for root, dirs, files in os.walk(heatmap_dir):
    #     for file in files:
    #         if file.endswith('.ttf'):
    #         #check that its actually a json file first
    #             file_path = os.path.join(root, file)
    #             gz_path = os.path.join(root,file[:-4])+'.gz'
    #             if is_gzipped(file_path):
    #                 os.rename(file_path,gz_path)
    #                 # sys.exit()

    #                 # Unpack the .gz file
    #                 with gzip.open(gz_path, 'rb') as f_in:
    #                     with open(file_path, 'wb') as f_out:
    #                         shutil.copyfileobj(f_in, f_out)
    #                 os.remove(gz_path)
    #                 print(f"Unpacked {gz_path} to {file_path}")
    #             else:
    #                 print("trace already unpacked!")        

def display_releases_and_download(releases):
    for release in releases:
        print(f"Release Name: {release['name']}")
        print(f"Tag Name: {release['tag_name']}")
        print(f"Published at: {release['published_at']}")
        
        for i, asset in enumerate(release['assets']):
            print(f"{i}. Download URL: {asset['browser_download_url']}")
        
        print('-' * 40)

    # Ask user if they want to download a file
    try:
        entry = int(input("Enter the index of the entry in the page you want (0-9) "))
        
        release = releases[entry]
        #asset_num = int(input("Enter the asset number to download: "))
        asset = release['assets'][0]
        file_name = asset['name']
        
        print(f"Downloading {file_name}...")
        if download_asset(asset['browser_download_url'], file_name):
            # Extract tar file to a folder named after the release
            extract_tar_to_folder(file_name, release['name'])
            unpack_data(release['name'],asset)
    except ValueError:
        print("Invalid input.")

def main():
    # Ask for page number
    try:
        page = int(input("Enter the page number to fetch (1-86): "))
        if page < 1 or page > 86:
            print("Invalid page number. Please enter a number between 1 and 86.")
            return
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return

    releases = fetch_releases(page)
    
    if releases:
        
        display_releases_and_download(releases)

if __name__ == '__main__':
    main()
