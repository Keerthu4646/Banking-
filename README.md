# Python Banking Microservices

## Run locally
```bash
cp .env.example .env
docker compose up --build
```

Open:
- Frontend: http://localhost:3000
- Gateway: http://localhost:8080
- Auth API docs: http://localhost:8001/docs
- Account API docs: http://localhost:8002/docs
- Transaction API docs: http://localhost:8003/docs
- Notification API docs: http://localhost:8004/docs
- Reporting API docs: http://localhost:8005/docs

## Kubernetes
Build and push images, update image names in `k8s/*.yaml`, then:
```bash
kubectl apply -f k8s/
```
