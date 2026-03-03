mnf_clean
sudo rm -r client_log
sudo rm -r Experiment
sudo rm -r Results

docker stop$(docker ps -aq)
docker kill $(docker ps -aq)
docker rm $(docker ps -aq)
