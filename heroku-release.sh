docker-compose down --rmi all &&
docker buildx build --platform linux/amd64 -t masterquizz-server . &&
docker tag masterquizz-server registry.heroku.com/masterquizz-server/server &&
docker push registry.heroku.com/masterquizz-server/server &&
heroku container:release server -a masterquizz-server