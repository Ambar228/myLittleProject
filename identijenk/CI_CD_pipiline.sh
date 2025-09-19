#!/bin/bash
set -e
# Переход в дерикторию identidock
cd identidock
echo "Текущая рабочая дериктория: $(pwd)"
echo "__________________________________"
ls -la
# Аргументы для Compose для myLittleProject
COMPOSE_ARGS=" -f jenkins.yml -p jenkins "
# Необходимо остановить и удалить все старые контейнеры
sudo docker-compose $COMPOSE_ARGS down -v --remove-orphans 2>/dev/null || true

# Создание (сборка) системы
sudo docker-compose $COMPOSE_ARGS build --no-cache
sudo docker-compose $COMPOSE_ARGS up -d
sleep 40

# Выполнение модульного тестирования
sudo docker-compose $COMPOSE_ARGS run --no-deps --rm -e ENV=UNIT identidock
UNIT_ERR=$?

# Выполнение тестирования системы в целом, если модульное тестирование завершилось успешно
if [ $ERR -eq 0 ]; then
    # Получаем IP адрес контейнера
    IP=$(sudo docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$CONTAINER_ID" )
    echo "IP-Adress: $IP"
    
    # Проверяем основной endpoint (измените на ваш)
    CODE=$(curl -sL -w "%{http_code}" "http://$IP:5000/monster/bla" -o /dev/null) || true
    
    if [ $CODE -ne 200 ]; then
        echo "Сайт вернул код: $CODE"
        ERR=1
    else
        echo "Тестирование пройдено успешно! Код: 200"
    fi
fi

# Останов и удаление системы
sudo docker-compose $COMPOSE_ARGS stop
sudo docker-compose $COMPOSE_ARGS rm --force -v

exit $ERR
