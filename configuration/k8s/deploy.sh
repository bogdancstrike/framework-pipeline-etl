#!/bin/bash

# -----------------------------------------------------------------------------
# MicroK8s Deployment Script with Parameters
#
# Usage:
#   sudo ./deploy.sh [OPTIONS] [-n <namespace>]
#
# Options:
#   --recreate-namespace       Recreate the specified namespace (deletes all resources in it)
#   --rolling-updates          Perform rolling updates on all services without deleting the namespace
#   --delete-all               Delete the entire namespace and all resources within it
#   --delete-force             Force delete all pods and the namespace, then redeploy
#   --deploy-only [service]    Deploy or upgrade a specific service
#   --list-services            List all services in the specified namespace
#   --status                   Show the status of all pods and services in the specified namespace
#   --clean-failed-pods        Clean up all failed pods in the specified namespace
#   --scale [number]           Scale all pods to the specified number of instances
#   --help                     Show this help message
#
# Default Behavior:
#   Without any options, this script will:
#     - Delete all resources in the 'dev' namespace
#     - Recreate the 'dev' namespace
#     - Deploy all services
#
# Namespace:
#   By default, the script operates on the 'dev' namespace. However, you can specify
#   a different namespace by using the '-n' flag, e.g.:
#   sudo ./deploy.sh --delete-force -n dev2
#
# Examples:
#   sudo ./deploy.sh               # Default behavior: delete and redeploy in 'dev'
#   sudo ./deploy.sh --delete-force # Force delete pods and redeploy in 'dev'
#   sudo ./deploy.sh --delete-force -n dev2 # Force delete and redeploy in 'dev2'
#   sudo ./deploy.sh --deploy-only mysql # Deploy only the 'mysql' service in 'dev'
#   sudo ./deploy.sh --scale 3     # Scale all services to 3 instances in 'dev'
# -----------------------------------------------------------------------------

# Default namespace is 'dev'
NAMESPACE="dev"
SHOW_STATUS=false  # Default: don't show status unless --status is explicitly called

# Color definitions
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No color

# Spinner function for loading animation
spinner() {
    local pid=$!
    local delay=0.1
    local spin_chars="⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    local max_time=120 # Set a timeout (e.g., 120 seconds)
    local start_time=$(date +%s)

    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local current_time=$(date +%s)
        if (( current_time - start_time > max_time )); then
            printf "\r${RED}[✘] %s - Timed out after ${max_time}s${NC}\n" "$1"
            kill $pid > /dev/null 2>&1
            return 1
        fi
        for i in $(seq 0 $((${#spin_chars} - 1))); do
            printf "\r${YELLOW}[%s] %s${NC}" "${spin_chars:$i:1}" "$1"
            sleep $delay
        done
    done
    printf "\r${GREEN}[✔] %s${NC}\n" "$1"
}

# Function to delete the namespace
delete_namespace() {
    if [[ "$NAMESPACE" == "calico" || "$NAMESPACE" == "kube-system" || "$NAMESPACE" == "default" || "$NAMESPACE" == "kube-public" ]]; then
        echo -e "${RED}Error: Cannot delete the '${NAMESPACE}' namespace as it is critical to the Kubernetes system.${NC}"
        exit 1
    fi
    echo -e "${YELLOW}Deleting namespace '${NAMESPACE}'...${NC}"
    microk8s kubectl delete namespace "$NAMESPACE" --wait > /dev/null 2>&1 &
    spinner "Deleting namespace '${NAMESPACE}'"
    echo -e "${GREEN}Namespace '${NAMESPACE}' deleted.${NC}"
}

# Function to force delete all pods in the namespace
force_delete_pods() {
    echo -e "${YELLOW}Forcefully deleting all pods in namespace '${NAMESPACE}'...${NC}"
    microk8s kubectl delete pods --all --namespace "$NAMESPACE" --force --grace-period=0 > /dev/null 2>&1 &
    spinner "Forcefully deleting all pods in namespace '${NAMESPACE}'"
}

# Function to recreate namespace
recreate_namespace() {
    delete_namespace
    echo -e "${YELLOW}Creating namespace '${NAMESPACE}'...${NC}"
    microk8s kubectl create namespace "$NAMESPACE" > /dev/null 2>&1 &
    spinner "Creating namespace '${NAMESPACE}'"
    echo -e "${GREEN}Namespace '${NAMESPACE}' created successfully.${NC}"
}

# Function to deploy all services
deploy_services() {
    services=(mysql kafka kafka-ui backend frontend postgres grafana elasticsearch logstash kibana)

    echo -e "${YELLOW}Deploying services in namespace '${NAMESPACE}'...${NC}"
    for service in "${services[@]}"; do
        microk8s helm3 install "$service" ./helm-charts/"$service" -n "$NAMESPACE" > /dev/null 2>&1 &
        spinner "Deploying $service..."
        echo -e "${GREEN}$service deployed successfully.${NC}"
    done
}

# Function to perform rolling updates on all services
rolling_updates() {
    services=(mysql kafka kafka-ui backend frontend postgres grafana elasticsearch logstash kibana)

    echo -e "${YELLOW}Performing rolling updates for services in namespace '${NAMESPACE}'...${NC}"
    for service in "${services[@]}"; do
        if microk8s helm3 status "$service" -n "$NAMESPACE" > /dev/null 2>&1; then
            microk8s helm3 upgrade "$service" ./helm-charts/"$service" -n "$NAMESPACE" > /dev/null 2>&1 &
            spinner "Upgrading $service..."
            echo -e "${GREEN}$service upgraded successfully.${NC}"
        else
            echo -e "${RED}$service is not deployed. Skipping upgrade.${NC}"
        fi
    done
    echo -e "${GREEN}Rolling updates completed successfully!${NC}"
}

# Function to deploy or upgrade a specific service
deploy_only() {
    local service=$1
    echo -e "${YELLOW}Deploying or upgrading service '$service' in namespace '${NAMESPACE}'...${NC}"
    if microk8s helm3 status "$service" -n "$NAMESPACE" > /dev/null 2>&1; then
        microk8s helm3 upgrade "$service" ./helm-charts/"$service" -n "$NAMESPACE" > /dev/null 2>&1 &
        spinner "Upgrading $service..."
        echo -e "${GREEN}$service upgraded successfully.${NC}"
    else
        microk8s helm3 install "$service" ./helm-charts/"$service" -n "$NAMESPACE" > /dev/null 2>&1 &
        spinner "Deploying $service..."
        echo -e "${GREEN}$service deployed successfully.${NC}"
    fi
}

# Function to scale all pods
scale_pods() {
    local scale_count=$1
    echo -e "${YELLOW}Scaling all services to ${scale_count} instances...${NC}"
    services=(mysql kafka kafka-ui backend frontend postgres grafana elasticsearch logstash kibana)
    for service in "${services[@]}"; do
        microk8s kubectl scale deployment "$service" -n "$NAMESPACE" --replicas="$scale_count" > /dev/null 2>&1 &
        spinner "Scaling $service to $scale_count instances..."
    done
    echo -e "${GREEN}All services scaled to ${scale_count} instances.${NC}"
}

# Function to list all services in the namespace
list_services() {
    echo -e "${YELLOW}Listing all services in the '${NAMESPACE}' namespace...${NC}"
    microk8s kubectl get services -n "$NAMESPACE"
}

# Function to show the status of all pods and services
status() {
    echo -e "${YELLOW}Showing the status of all pods in namespace '${NAMESPACE}'...${NC}"
    watch -n "0.5" "microk8s kubectl get pods -n \"${NAMESPACE}\" -o wide"
}

# Function to clean up failed pods
clean_failed_pods() {
    echo -e "${YELLOW}Cleaning up failed pods in namespace '${NAMESPACE}'...${NC}"
    microk8s kubectl delete pod --field-selector=status.phase=Failed -n "$NAMESPACE"
    echo -e "${GREEN}Failed pods cleaned up.${NC}"
}

# Function to delete and redeploy all services
delete_and_deploy_all() {
    force_delete_pods
    delete_namespace
    recreate_namespace
    deploy_services
}

# Function to handle --delete-force
delete_and_deploy_force() {
    force_delete_pods
    delete_namespace
}

# Parse arguments for --n <namespace> and other options
while [[ "$1" != "" ]]; do
    case $1 in
        -n )                    shift
                                NAMESPACE="$1"
                                ;;
        --recreate-namespace )   recreate_namespace
                                ;;
        --rolling-updates )      rolling_updates
                                ;;
        --delete-all )           delete_namespace
                                ;;
        --delete-force )         delete_and_deploy_force
                                ;;
        --deploy-only )          shift
                                deploy_only "$1"
                                ;;
        --list-services )        list_services
                                ;;
        --status )               SHOW_STATUS=true
                                ;;
        --clean-failed-pods )    clean_failed_pods
                                ;;
        --scale )                shift
                                scale_pods "$1"
                                ;;
        --help )                 echo -e "${YELLOW}Usage: sudo ./deploy.sh [OPTIONS]${NC}"
                                echo -e "${YELLOW}Options:${NC}"
                                echo -e "${BLUE}--recreate-namespace${NC}       Recreate the namespace (delete all resources)"
                                echo -e "${BLUE}--rolling-updates${NC}          Perform rolling updates on all services"
                                echo -e "${BLUE}--delete-all${NC}               Delete the entire namespace and all resources"
                                echo -e "${BLUE}--delete-force${NC}             Force delete all pods and the namespace, then redeploy"
                                echo -e "${BLUE}--deploy-only [service]${NC}    Deploy or upgrade a specific service"
                                echo -e "${BLUE}--list-services${NC}            List all services in the specified namespace"
                                echo -e "${BLUE}--status${NC}                   Show the status of all pods and services"
                                echo -e "${BLUE}--clean-failed-pods${NC}        Clean up all failed pods"
                                echo -e "${BLUE}--scale [number]${NC}           Scale all pods to the specified number of instances"
                                echo -e "${YELLOW}You can also specify the namespace with -n <namespace>. Default is 'dev'.${NC}"
                                exit 0
                                ;;
        * )                      echo -e "${RED}Unknown option: $1${NC}"
                                exit 1
    esac
    shift
done

# Default behavior (if no specific options are passed)
if [ "$SHOW_STATUS" = true ]; then
    status
else
    delete_and_deploy_all
fi
