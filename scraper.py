import os
import requests
from bs4 import BeautifulSoup
import time

BASE_URL = "https://dziennikustaw.gov.pl/DU/rok"
BASE_URL_DIRECT = "https://dziennikustaw.gov.pl"
AVAILABLE_YEARS = [str(year) for year in range(1918, 2025) if year not in {1943, 1942, 1941, 1940}]
DOWNLOAD_DIR_BASE = "./dziennik_ustaw"


def prompt_user_for_years():
    print("Available years: 1918 - 2024 except for 1940 - 1943.")
    selected_years = input(
        "Enter the years you want to download (comma-separated), or type 'all' to download from all years: ").strip()
    if selected_years.lower() == 'all':
        return AVAILABLE_YEARS
    else:
        selected_years = [year.strip() for year in selected_years.split(',')]
        valid_years = [year for year in selected_years if year in AVAILABLE_YEARS]
        invalid_years = set(selected_years) - set(valid_years)
        if invalid_years:
            print(f"Invalid years entered: {', '.join(invalid_years)}. These will be ignored.")
        return valid_years


def prompt_user_for_limit():
    try:
        limit = int(input("Enter the number of documents to download per year, or 0 to download all: ").strip())
        return limit
    except ValueError:
        print("Invalid input. Defaulting to download all documents.")
        return 0


def download_pdf(pdf_url, save_path, downloaded_count, limit):
    if downloaded_count >= limit > 0:
        return downloaded_count

    print(f"Attempting to download {pdf_url} ...")
    response = requests.get(pdf_url, stream=True)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        print(f"Successfully downloaded: {save_path}")
        return downloaded_count + 1
    else:
        print(f"Failed to download {pdf_url} (status code: {response.status_code})")
        return downloaded_count


def scrape_position(position_url, year, journal, position, downloaded_count, limit):
    if downloaded_count >= limit > 0:
        return downloaded_count

    print(f"Scraping position {position} from journal {journal} in year {year}...")
    response = requests.get(position_url)

    if response.status_code != 200:
        print(f"Failed to retrieve position page {position_url} (status code: {response.status_code})")
        return downloaded_count

    soup = BeautifulSoup(response.text, 'html.parser')
    file_links = soup.select('a[href$=".pdf"]')
    valid_file_links = [link for link in file_links if f"/DU/{year}/" in link['href']]

    if not valid_file_links:
        print(f"No valid PDF links found for position {position}.")
        return downloaded_count

    download_dir = os.path.join(DOWNLOAD_DIR_BASE, year)
    os.makedirs(download_dir, exist_ok=True)

    for i, link in enumerate(valid_file_links, start=1):
        if downloaded_count >= limit > 0:
            break

        pdf_url = link['href']
        if not pdf_url.startswith("http"):
            pdf_url = f"{BASE_URL_DIRECT}{pdf_url}"

        pdf_filename = f"D{year}{journal}{position}{i:02}.pdf"
        save_path = os.path.join(download_dir, pdf_filename)

        downloaded_count = download_pdf(pdf_url, save_path, downloaded_count, limit)

    return downloaded_count


def scrape_wydanie(year, journal, downloaded_count, limit):
    if downloaded_count >= limit > 0:
        return downloaded_count

    print(f"Scraping wydanie {journal} for year {year}...")
    url = f"{BASE_URL}/{year}/wydanie/{journal}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to retrieve wydanie page {journal} (status code: {response.status_code})")
        return downloaded_count

    soup = BeautifulSoup(response.text, 'html.parser')
    position_links = soup.select('#c_table tbody tr td.numberAlign a')
    if not position_links:
        print(f"No positions found in wydanie {journal}.")
        return downloaded_count

    for pos_link in position_links:
        if downloaded_count >= limit > 0:
            break

        pos_path = pos_link['href']
        position = pos_path.split("/")[-1]
        position_url = f"{BASE_URL_DIRECT}{pos_path}"

        downloaded_count = scrape_position(position_url, year, journal, position, downloaded_count, limit)

    return downloaded_count


def scrape_year(year, limit):
    downloaded_count = 0
    url = f"{BASE_URL}/{year}"
    print(f"\nScraping year {year} from {url} ...")
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to retrieve the page for {year} (status code: {response.status_code})")
        return downloaded_count

    soup = BeautifulSoup(response.text, 'html.parser')
    pdf_links = soup.select('#c_table tbody tr a[href$=".pdf"]')

    if pdf_links:
        print(f"Found direct PDFs for year {year}. Downloading...")
        download_dir = os.path.join(DOWNLOAD_DIR_BASE, year)
        os.makedirs(download_dir, exist_ok=True)

        for link in pdf_links:
            if downloaded_count >= limit > 0:
                break

            pdf_path = link['href']
            if f"/DU/{year}/" not in pdf_path:
                continue

            pdf_url = f"{BASE_URL_DIRECT}{pdf_path}"
            pdf_name = pdf_path.split("/")[-1]
            save_path = os.path.join(download_dir, pdf_name)

            downloaded_count = download_pdf(pdf_url, save_path, downloaded_count, limit)
            time.sleep(1)
    else:
        print(f"No direct PDFs found for year {year}. Switching to 'wydanie' list...")
        journal_links = soup.select('#c_table tbody tr td.numberAlign a')

        if not journal_links:
            print(f"No journals (wydanie) found for year {year}.")
            return downloaded_count

        for journal_link in journal_links:
            if downloaded_count >= limit > 0:
                break

            journal = journal_link.text.strip()
            downloaded_count = scrape_wydanie(year, journal, downloaded_count, limit)

    return downloaded_count


if __name__ == "__main__":
    years_to_download = prompt_user_for_years()
    if not years_to_download:
        print("No valid years selected. Exiting program.")
    else:
        document_limit = prompt_user_for_limit()

        total_downloaded = 0
        for year in years_to_download:
            if total_downloaded >= document_limit > 0:
                break
            total_downloaded += scrape_year(year, document_limit - total_downloaded)
