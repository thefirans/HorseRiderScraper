import re
import time
import gspread

from selenium import webdriver
from selenium.webdriver.common.by import By


def main():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--window-size=800,1200")

    driver = webdriver.Chrome(chrome_options)
    url = "https://online.equipe.com/startlists/881701"
    driver.get(url)

    rider_list_fun = driver.find_elements(By.CSS_SELECTOR, 'a.start.row-hover')

    rider_name = []
    rider_nationality = []
    horse_name = []
    competition_number = []
    sire_name = []
    sire_of_dam_name = []
    horse_color = []
    year_of_birth = []
    owner_name = []
    breeder = []
    horse_gender = []

    for i in range(len(rider_list_fun)):

        rider_list = driver.find_elements(By.CSS_SELECTOR, 'a.start.row-hover')

        if i > 0:
            element = rider_list[i]
            # driver.execute_script("window.scrollBy(0, 200);")
            driver.execute_script("arguments[0].scrollIntoView();", element)
            time.sleep(0.5)

        rider_list[i].click()

        time.sleep(0.5)

        rider_nationality.append(driver.find_element(By.CLASS_NAME, 'nation').text)  # add nation to list

        name_elements = driver.find_elements(By.CLASS_NAME, 'name')  # second is rider_name third is horse_name

        rider_name.append(name_elements[1].text)  # add rider_name to list
        horse_name.append(name_elements[2].text)  # add horse_name to list

        pattern = r'\d'
        horse_number = driver.find_element(By.CLASS_NAME, 'horse-no-badge')
        if re.search(pattern, horse_number.text):
            competition_number.append(horse_number.text)
        else:
            competition_number.append(None)

        infos = driver.find_elements(By.CLASS_NAME, 'info')
        target_info = infos[1].text.strip()

        # sire_name and sire_of_dam_name section
        sire_name_pattern = r'^(.*?) - (.*?) \|'

        sire_name_match = re.search(sire_name_pattern, target_info)

        sire_name_str = sire_name_match.group(1).strip() if sire_name_match else None
        sire_name.append(sire_name_str)

        sire_of_dam_name_str = sire_name_match.group(2).strip() if sire_name_match else None
        sire_of_dam_name.append(sire_of_dam_name_str)

        # owner and breeder section
        owner_name_pattern = r'Owner: (.+?)(?:\n|Breeder|$)'
        breeder_name_pattern = r'Breeder: (.+?)(?:\n|$)'

        owner_name_match = re.search(owner_name_pattern, target_info)
        breeder_name_match = re.search(breeder_name_pattern, target_info)

        owner_name_str = owner_name_match.group(1).strip() if owner_name_match else None
        owner_name.append(owner_name_str)

        breeder_str = breeder_name_match.group(1).strip() if breeder_name_match else None
        breeder.append(breeder_str)

        if i + 1 == 23:
            sire_name_str = "Centauer Z"

        if i + 1 == 25:
            sire_name_str = "Captain Fire"

        if i + 1 == 42:
            sire_name_str = "Mylord Carthago*HN"

        if i + 1 == 44:
            sire_name_str = "Nartago"

        horse_genders = ["Mare", "Stallion", "Gelding", "Filly", "Colt", "Yearling", "Foal"]
        for gender in horse_genders:
            if gender in target_info:
                horse_gender_str = gender
                horse_gender.append(horse_gender_str)

        year_of_birth_pattern = r'\b\d{4}\b'
        year_of_birth_match = re.search(year_of_birth_pattern, target_info)
        year_of_birth_str = year_of_birth_match.group(0)
        year_of_birth.append(year_of_birth_str)

        if (sire_name_str is not None and sire_of_dam_name_str is not None) or (
                sire_name_str is not None or sire_of_dam_name_str is not None):
            parts = target_info.replace("/n", " ").split(' | ')
            horse_color_str = parts[1].strip()
            horse_color.append(horse_color_str)
        else:
            split_string = target_info.replace("/n", " ").split(" | ", 1)
            horse_color_str = split_string[0].strip()
            horse_color.append(horse_color_str)

        driver.back()
        time.sleep(0.5)

    all_data = [
        rider_name,
        rider_nationality,
        horse_name,
        competition_number,
        sire_name,
        sire_of_dam_name,
        horse_color,
        year_of_birth,
        owner_name,
        breeder,
        horse_gender
    ]

    sent_to_sheet(all_data)


def sent_to_sheet(all_data):
    columns = [
        ('A', all_data[0]),
        ('B', all_data[1]),
        ('C', all_data[2]),
        ('D', all_data[3]),
        ('E', all_data[4]),
        ('F', all_data[5]),
        ('G', all_data[6]),
        ('H', all_data[7]),
        ('I', all_data[8]),
        ('J', all_data[9]),
        ('K', all_data[10])
    ]

    credentials_path = 'your-project-credentials.json'
    print(credentials_path)
    gc = gspread.service_account(filename=credentials_path)

    sheet = gc.open("Example")
    worksheet = sheet.worksheet('Sheet1')

    start_row = 2

    for col, data_list in columns:
        cell_list = worksheet.range(f'{col}{start_row}:{col}{start_row + len(data_list) - 1}')
        for i, cell in enumerate(cell_list):
            cell.value = data_list[i]
        worksheet.update_cells(cell_list)

    print("Filling is done!")
    time.sleep(30)


if __name__ == '__main__':
    main()
