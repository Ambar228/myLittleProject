FROM jenkins/jenkins:2.462.1

USER root

# Ваши системные пакеты (оставляем как было)
RUN apt-get update && \
    apt-get install -y apt-transport-https ca-certificates curl gnupg && \
    rm -rf /var/lib/apt/lists/*

RUN install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    chmod a+r /etc/apt/keyrings/docker.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

RUN apt-get update && \
    apt-get install -y docker-ce-cli sudo && \
    rm -rf /var/lib/apt/lists/*

RUN echo "jenkins ALL=NOPASSWD: ALL" >> /etc/sudoers

RUN curl -L "https://github.com/docker/compose/releases/download/v2.24.1/docker-compose-linux-$(uname -m)" -o /usr/local/bin/docker-compose && \
    chmod +x /usr/local/bin/docker-compose

# УСТАНОВКА С АВТОМАТИЧЕСКИМ РАЗРЕШЕНИЕМ ЗАВИСИМОСТЕЙ
RUN jenkins-plugin-cli --plugins git --latest-specified

USER jenkins
