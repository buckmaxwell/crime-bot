import os
#nohup python build_crime_db.py > log.txt 2>&1 &
#4092269 + 4092270 must be manually added to database bc of my fuckup
while True:
	os.system("python crime_scrape5.py")