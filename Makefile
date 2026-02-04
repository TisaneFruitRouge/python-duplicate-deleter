.PHONY: install run zip test-folders build clean

install:
	pip install -r requirements.txt

run:
	python remove_duplicate_images.py

build:
	pyinstaller --onefile --windowed --name "RemoveDuplicateImages" remove_duplicate_images.py

clean:
	rm -rf build dist *.spec

zip:
	zip -r remove_duplicate_images.zip remove_duplicate_images.py requirements.txt Makefile test_images/

test-folders:
	rm -rf test_images
	mkdir -p test_images/01_simple_duplicates
	touch "test_images/01_simple_duplicates/1 image.png"
	touch "test_images/01_simple_duplicates/2 image.png"
	touch "test_images/01_simple_duplicates/3 image.png"
	mkdir -p test_images/02_no_duplicates
	touch "test_images/02_no_duplicates/landscape.png"
	touch "test_images/02_no_duplicates/portrait.jpg"
	touch "test_images/02_no_duplicates/selfie.png"
	mkdir -p test_images/03_not_duplicates
	touch "test_images/03_not_duplicates/12 image of potato.png"
	touch "test_images/03_not_duplicates/potato"
	mkdir -p test_images/04_multiple_groups
	touch "test_images/04_multiple_groups/1 sunset.jpg"
	touch "test_images/04_multiple_groups/2 sunset.jpg"
	touch "test_images/04_multiple_groups/1 beach.png"
	touch "test_images/04_multiple_groups/2 beach.png"
	touch "test_images/04_multiple_groups/3 beach.png"
	touch "test_images/04_multiple_groups/unique_photo.jpg"
	mkdir -p test_images/05_no_space_prefix
	touch "test_images/05_no_space_prefix/1photo.png"
	touch "test_images/05_no_space_prefix/2photo.png"
	touch "test_images/05_no_space_prefix/99photo.png"
	mkdir -p test_images/06_many_duplicates
	touch "test_images/06_many_duplicates/1 wallpaper.jpg"
	touch "test_images/06_many_duplicates/2 wallpaper.jpg"
	touch "test_images/06_many_duplicates/3 wallpaper.jpg"
	touch "test_images/06_many_duplicates/4 wallpaper.jpg"
	touch "test_images/06_many_duplicates/5 wallpaper.jpg"
	touch "test_images/06_many_duplicates/6 wallpaper.jpg"
	touch "test_images/06_many_duplicates/7 wallpaper.jpg"
	touch "test_images/06_many_duplicates/8 wallpaper.jpg"
	touch "test_images/06_many_duplicates/9 wallpaper.jpg"
	touch "test_images/06_many_duplicates/10 wallpaper.jpg"
	mkdir -p test_images/07_mixed
	touch "test_images/07_mixed/1 cat.png"
	touch "test_images/07_mixed/2 cat.png"
	touch "test_images/07_mixed/dog.png"
	touch "test_images/07_mixed/1 bird.jpg"
	touch "test_images/07_mixed/2 bird.jpg"
	touch "test_images/07_mixed/3 bird.jpg"
	touch "test_images/07_mixed/fish.gif"
