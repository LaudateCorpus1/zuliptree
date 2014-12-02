all:
	echo "Do nothing"
deploy:
	git checkout deploy
	git merge master
	git push origin deploy:master
	git checkout master
