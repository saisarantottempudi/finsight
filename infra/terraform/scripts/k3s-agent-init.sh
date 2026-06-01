#!/bin/bash
set -euo pipefail

apt-get update -y
apt-get install -y curl

# Wait for server to be ready (simple delay)
sleep 60

# Get token from server (requires SSH or shared secret — set K3S_TOKEN via secret)
# In practice: copy /var/lib/rancher/k3s/server/node-token from server
curl -sfL https://get.k3s.io | \
  K3S_URL="https://${k3s_server_ip}:6443" \
  K3S_TOKEN="${k3s_token:-REPLACE_WITH_SERVER_TOKEN}" \
  sh -

echo "k3s agent joined"
