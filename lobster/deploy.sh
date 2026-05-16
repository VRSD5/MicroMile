kn service delete lobster
docker build --tag localhost:5001/lobster .
docker push localhost:5001/lobster
kn service create lobster --image localhost:5001/lobster --port 3002