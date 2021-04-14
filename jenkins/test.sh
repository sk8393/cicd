for x in `docker-compose -p test ps -q`; do
  STATUS=`docker ps -f id=${x} --format "{{.Status}}" | cut -d " " -f1`;
  NAMES=`docker ps -f id=${x} --format "{{.Names}}"`;
  echo ${NAMES} ${STATUS};
  if [ ${STATUS} != 'Up' ] ; then
    echo "Container ${NAMES} is not 'Up', will pause this test."
    exit 1
  fi
done
