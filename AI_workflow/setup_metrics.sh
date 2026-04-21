#!/bin/bash

# --- COLORS FOR BETTER READABILITY ---
BLUE='\033[0;34m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}====================================================${NC}"
echo -e "${BLUE}   KUBERNETES METRICS SERVER SETUP FOR KIND        ${NC}"
echo -e "${BLUE}====================================================${NC}"

# 1. Download and Apply the standard manifests
echo -e "\n${BLUE}--- [1/4] Installing Base Metrics Server ---${NC}"
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# 2. Patch the deployment for Kind (Insecure TLS)
echo -e "\n${BLUE}--- [2/4] Applying Kind-Specific TLS Patch ---${NC}"
# We add --kubelet-insecure-tls so the server trusts Kind's self-signed certs
kubectl patch deployment metrics-server -n kube-system --type='json' -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'

# 3. Wait for the rollout to complete
echo -e "\n${BLUE}--- [3/4] Waiting for Pod to reach 'Ready' status ---${NC}"
kubectl rollout status deployment metrics-server -n kube-system --timeout=90s

# 4. Wait for the API to actually start reporting data
echo -e "\n${BLUE}--- [4/4] Waiting for Metrics API to report data (approx 60s) ---${NC}"
COUNT=0
MAX_RETRIES=12
until kubectl top nodes &> /dev/null || [ $COUNT -eq $MAX_RETRIES ]; do
    echo -ne "  Collecting metrics... ($((COUNT * 5))s)\r"
    sleep 5
    ((COUNT++))
done

echo -e "\n"

# Final Check
if kubectl top nodes &> /dev/null; then
    echo -e "${GREEN}SUCCESS: Metrics API is online and reporting!${NC}"
    kubectl top nodes
    echo -e "\n${GREEN}====================================================${NC}"
    echo -e "${GREEN}   INFRASTRUCTURE READY FOR SENTINEL AI DEMO        ${NC}"
    echo -e "${GREEN}====================================================${NC}"
else
    echo -e "${RED}ERROR: Metrics API timed out. Check logs with:${NC}"
    echo -e "kubectl logs -n kube-system -l k8s-app=metrics-server"
fi
