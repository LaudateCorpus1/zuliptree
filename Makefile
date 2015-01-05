all:
	echo "Do nothing"
deploy:
	git checkout deploy
	git merge master
	git push origin deploy:master
	git checkout master

mongo:
	echo "CHECKING OUT DEPLOY BRANCH -- password is there"
	git checkout deploy
	mongo --authenticationDatabase admin -u chase -p `cat mongo-pass.conf` --host 104.131.112.57 --port 27017
	git checkout master

test:
	py.test
