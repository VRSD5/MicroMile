kn service delete frontend
docker build --tag localhost:5001/frontend .
docker push localhost:5001/frontend
kn service create frontend --image localhost:5001/frontend --port 3000