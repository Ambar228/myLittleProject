#Команды для запуска

docker run --name jenkins-data identijenk echo "Jenkins Data Container"

docker run -d --name jenkins -p 8080:8080 -p 50000:50000 --volumes-from jenkins-data -v /var/run/docker.sock:/var/run/docker.sock --privileged -u root identijenk-fixed

