#!/bin/bash
# Litmus Chaos Lab Setup - Docker Desktop K8S (ARM)
# Run this to verify the full setup

set -e

echo "========================================="
echo " Litmus Chaos Lab - Health Check"
echo "========================================="
echo ""

# Check cluster
echo "[1/5] Checking Kubernetes cluster..."
kubectl cluster-info 2>&1 | head -2
echo ""

# Check pods
echo "[2/5] Checking Litmus pods..."
kubectl get pods -n litmus -o wide
echo ""

# Check services
echo "[3/5] Checking Litmus services..."
kubectl get svc -n litmus
echo ""

# Check MongoDB
echo "[4/5] Checking MongoDB replica set..."
kubectl exec mongodb-0 -n litmus -- mongosh --host mongodb-0.mongodb-headless.litmus.svc.cluster.local --eval 'rs.status().ok' --quiet 2>&1
echo ""

# Check chaos CRDs
echo "[5/5] Checking Chaos CRDs..."
kubectl get crds 2>&1 | grep chaos
echo ""

# Get dashboard URL
NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}' 2>/dev/null || echo "127.0.0.1")
# Docker Desktop uses LoadBalancer, check for external IP
EXTERNAL_IP=$(kubectl get svc chaoscenter-litmus-frontend-service -n litmus -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
SVC_PORT=$(kubectl get svc chaoscenter-litmus-frontend-service -n litmus -o jsonpath='{.spec.ports[0].port}' 2>/dev/null || echo "9091")

echo "========================================="
echo " Dashboard Access:"
echo "   URL: http://localhost:${SVC_PORT}"
echo "   User: admin"
echo "   Pass: litmus"
echo "========================================="
echo ""
echo "Target namespace: litmus-lab"
echo "  kubectl get pods -n litmus-lab"
echo ""
