for x in `docker-compose -p test ps -q`; do
  REPOSITORY=`docker ps -f id=${x} --format "{{.Image}}" | cut -d ":" -f1`;
  TAG=`docker ps -f id=${x} --format "{{.Image}}" | cut -d ":" -f2`;
  echo ${REPOSITORY};
  echo ${TAG}
  docker tag ${REPOSITORY}:${TAG} ${REPOSITORY}:production
done
