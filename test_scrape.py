from bs4 import BeautifulSoup
import csv
import requests
import pytesseract
import pytesseract
from pdf2image import convert_from_path
import sys

pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'

def get_investments_iframe_url(main_url):
    response = requests.get(main_url)
    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        iframes = soup.find_all('iframe')

        for iframe in iframes:
            iframe_src = iframe.get('src')
            if 'InvestmentsCorpStockSchedule' in iframe_src:
                get_csv_investments_corp_bonds_schedule_tbl(iframe_src)

def get_csv_investments_corp_bonds_schedule_tbl(e_file_url):
    response = requests.get(e_file_url)
    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.find('table')

        if table:
            table_data = []
            header_row = table.find('thead').find('tr')
            header_cells = header_row.find_all('th')
            headings = [cell.text.strip() for cell in header_cells]

            data_rows = table.find_all(class_='styDepTblRow1') + table.find_all(class_='styDepTblRow2')
            for row in data_rows:
                row_cells = row.find_all('td')
                row_data = [cell.text.strip() for cell in row_cells]
                table_data.append(row_data)

            csv_filename = 'InvestmentsCorpBondsScheduleTbl.csv'
         
            with open(csv_filename, 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(headings)
                csv_writer.writerows(table_data)

def extract_and_save_to_text(pdf_path, output_file):
    with open(output_file, 'w') as output_txt:
        images = convert_from_path(pdf_path)
        total_pages = len(images)
        print(f"Total pages in PDF: {total_pages}")

        for i, image in enumerate(images):
            sys.stdout.write(f"\rExtracting text from page {i+1}/{total_pages}... ")
            sys.stdout.flush()

            extracted_text = pytesseract.image_to_string(image)
            output_txt.write(f"=== Page {i+1} ===\n")
            output_txt.write(extracted_text)
            output_txt.write("\n\n")

        print("\nText extraction completed.")
        print(f"Extracted text saved to: {output_file}")

if __name__ == "__main__":
    year = input("Please enter the year: ")
    if year == "2020":
        get_investments_iframe_url("https://projects.propublica.org/nonprofits/organizations/911663695/202133159349100408/full")
    elif year == "2019":
        pdf_path = './2019.pdf'
        output_file = 'extracted_text.txt'
        extract_and_save_to_text(pdf_path, output_file)