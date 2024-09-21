#!/bin/bash

# Enable necessary MicroK8s services
microk8s enable dns storage helm3 hostpath

# Update Helm repositories
microk8s helm3 repo add bitnami https://charts.bitnami.com/bitnami
microk8s helm3 repo update

# Check if namespace 'dev' exists, and if so, delete it to clean up all resources
if microk8s kubectl get namespace dev > /dev/null 2>&1; then
  echo "Namespace 'dev' exists. Deleting..."
  microk8s kubectl delete namespace dev --wait
  echo "Namespace 'dev' deleted."
fi

# Create the namespace again
microk8s kubectl create namespace dev

# Deploy all services using Helm
services=(mysql kafka kafka-ui backend frontend postgres grafana elasticsearch logstash kibana)
for service in "${services[@]}"; do
  echo "Deploying $service..."
  microk8s helm3 install $service ./helm-charts/$service -n dev
done

echo "All services deployed successfully!"
