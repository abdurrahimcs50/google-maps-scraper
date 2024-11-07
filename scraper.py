
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumbase import Driver
import time
import json
import re

from decouple import config


username = config('username')
password = config('password')
host = config('host')
port = config('port')

proxy = f"{username}:{password}@{host}:{port}"

driver = Driver(uc=True, proxy=proxy,)


time.sleep(5)
driver.maximize_window()
driver.implicitly_wait(10)
driver.get('https://bot.sannysoft.com/')
time.sleep(5)
driver.get('https://whoer.net/')
time.sleep(5)
print('Proxy Server Connected')



try: 
  keyword = "Web Design Agency"

  driver.get(f'https://www.google.com/maps/search/{keyword}/')

  try:
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "form:nth-child(2)"))).click()
  except Exception:
    pass

  scrollable_div = driver.find_element(By.CSS_SELECTOR, 'div[role="feed"]')
  driver.execute_script("""
          var scrollableDiv = arguments[0];
          function scrollWithinElement(scrollableDiv) {
              return new Promise((resolve, reject) => {
                  var totalHeight = 0;
                  var distance = 1000;
                  var scrollDelay = 3000;
                  
                  var timer = setInterval(() => {
                      var scrollHeightBefore = scrollableDiv.scrollHeight;
                      scrollableDiv.scrollBy(0, distance);
                      totalHeight += distance;

                      if (totalHeight >= scrollHeightBefore) {
                          totalHeight = 0;
                          setTimeout(() => {
                              var scrollHeightAfter = scrollableDiv.scrollHeight;
                              if (scrollHeightAfter > scrollHeightBefore) {
                                  return;
                              } else {
                                  clearInterval(timer);
                                  resolve();
                              }
                          }, scrollDelay);
                      }
                  }, 200);
              });
          }
          return scrollWithinElement(scrollableDiv);
  """, scrollable_div)

  items = driver.find_elements(By.CSS_SELECTOR, 'div[role="feed"] > div > div[jsaction]')
  print(len(items))
  print(type(items))
  # print(items)

  results = []
  for item in items:
    # print(item)
    data = {}

    try:
        data['title'] = item.find_element(By.CSS_SELECTOR, ".fontHeadlineSmall").text
    except Exception:
      pass

    try:
        data['link'] = item.find_element(By.CSS_SELECTOR, "a").get_attribute('href')
    except Exception:
      pass
    try:
        data['website'] = item.find_element(By.CSS_SELECTOR, 'div[role="feed"] > div > div[jsaction] div > a').get_attribute('href')
    except Exception:
      pass
    
    try:
        rating_text = item.find_element(By.CSS_SELECTOR, '.fontBodyMedium > span[role="img"]').get_attribute('aria-label')
        rating_numbers = [float(piece.replace(",", ".")) for piece in rating_text.split(" ") if piece.replace(",", ".").replace(".", "", 1).isdigit()]

        if rating_numbers:
           data['stars'] = rating_numbers[0]
           data['reviews'] = int(rating_numbers[1]) if len(rating_numbers) > 1 else 0
    except Exception:
      pass

    try:
      text_content = item.text
      phone_pattern = r'((\+?\d{1,2}[ -]?)?(\(?\d{3}\)?[ -]?\d{3,4}[ -]?\d{4}|\(?\d{2,3}\)?[ -]?\d{2,3}[ -]?\d{2,3}[ -]?\d{2,3}))'
      matches = re.findall(phone_pattern, text_content)

      phone_numbers = [match[0] for match in matches]
      unique_phone_numbers = list(set(phone_numbers))

      data['phone'] = unique_phone_numbers[0] if unique_phone_numbers else None   
    except Exception:
        pass
    # click item and get address
    try:
      time.sleep(1)
      # Extracting the address
      address = item.find_element(By.XPATH, ".//span[contains(text(), '·')]/following-sibling::span").text
      print(address, 'address')
      data['address'] = address
      time.sleep(1)
    except Exception:
      pass
    
    if (data.get('title')):
      results.append(data)
    
  with open('results.json', 'w', encoding='utf-8') as f:
      json.dump(results, f, ensure_ascii=False, indent=2)

finally:
  time.sleep(60)
  driver.quit()
