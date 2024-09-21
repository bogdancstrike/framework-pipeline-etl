## Project Structure

k8s-project/
├── deploy.sh                       # Script to deploy all services
├── helm-charts/                    # Directory for Helm charts
│   ├── mysql/
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   └── templates/
│   │       ├── deployment.yaml
│   │       ├── service.yaml
│   │       └── pvc.yaml
│   ├── kafka/
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   └── templates/
│   │       ├── deployment.yaml
│   │       ├── service.yaml
│   ├── kafka-ui/
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   └── templates/
│   │       ├── deployment.yaml
│   │       ├── service.yaml
│   ├── backend/
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   └── templates/
│   │       ├── deployment.yaml
│   │       ├── service.yaml
│   ├── frontend/
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   └── templates/
│   │       ├── deployment.yaml
│   │       ├── service.yaml
│   ├── postgres/
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   └── templates/
│   │       ├── deployment.yaml
│   │       ├── service.yaml
│   │       ├── pvc.yaml
│   ├── grafana/
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   └── templates/
│   │       ├── deployment.yaml
│   │       ├── service.yaml
│   │       ├── ingress.yaml
│   ├── elasticsearch/
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   └── templates/
│   │       ├── deployment.yaml
│   │       ├── service.yaml
│   ├── logstash/
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   └── templates/
│   │       ├── deployment.yaml
│   │       ├── service.yaml
│   ├── kibana/
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   └── templates/
│   │       ├── deployment.yaml
│   │       ├── service.yaml
├── ingress/                        # Ingress resources for each service
│   ├── grafana-ingress.yaml
│   ├── kibana-ingress.yaml
│   └── frontend-ingress.yaml
├── pvc/                            # Persistent Volume Claims for each service
│   ├── mysql-pvc.yaml
│   ├── postgres-pvc.yaml
│   ├── kafka-pvc.yaml
│   ├── elasticsearch-pvc.yaml
└── README.md                       # Project documentation

## Deploy

```code
	./deploy.sh
```

## Scaling

```code
	microk8s kubectl scale deployment <deployment-name> --replicas=3 -n <namespace>
```
