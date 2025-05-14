GUI sqldeveloper в докер контейнер

Добавить права для X1 сокета
``xhost -local:root``

Тест работы X1
`DISPLAY=:1 xclock`

Узнать uid пользователя
``id``

Создание имэджа
``docker build -t sqldeveloper:debian-buster --build-arg uid=${UID} .``

Запуск контейнера
``sudo docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix sqldeveloper:debian-buster``

