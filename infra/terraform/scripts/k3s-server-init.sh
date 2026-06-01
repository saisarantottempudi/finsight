#!/bin/bash
set -euo pipefail

apt-get update -y
apt-get install -y curl

# Install k3s server (no traefik — using nginx ingress)
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--disable traefik" sh -

# Wait for k3s to be ready
until kubectl get nodes 2>/dev/null | grep -q Ready; do sleep 5; done

# Install nginx ingress controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.10.1/deploy/static/provider/cloud/deploy.yaml

# Install cert-manager (free TLS via Let's Encrypt)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.15.0/cert-manager.yaml

echo "k3s server ready"
