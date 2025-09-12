FROM jenkins/jenkins:2.440.1

USER root

RUN apt-get update && \ 
    apt-get install -y \ 
	apt-transport-https \ 
	ca-certificates \ 
	curl \ 
	gnupg && \ 
    rm -rf /var/lib/apt/lists/*

RUN install -m 0755 -d /etc/apt/keyrings && \ 
	curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \ 
	chmod a+r /etc/apt/keyrings/docker.gpg && \ 
	echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \ 
	$(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

RUN apt-get update && \ 
    apt-get install -y \ 
	docker-ce-cli \ 
	sudo && \ 
    rm -rf /var/lib/apt/lists/*

RUN echo "jenkins ALL=NOPASSWD: ALL" >> /etc/sudoers

USER jenkins
