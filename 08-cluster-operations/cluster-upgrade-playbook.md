# Cluster Upgrade Playbook

> **Category:** Operations / Playbooks
> Step-by-step playbook for upgrading Kubernetes clusters.

## Overview

```mermaid
graph LR
    A[Plan Upgrade] --> B[Backup]
    B --> C[Upgrade Control Plane]
    C --> D[Upgrade Workers]
    D --> E[Validate]
    E --> F[Post-Upgrade]
```

## Upgrade Strategy

| Strategy | Description | Downtime |
|----------|-------------|----------|
| **Rolling upgrade** | Upgrade one node at a time | Zero |
| **Blue-green** | Upgrade new cluster, switch traffic | Minutes |
| **In-place** | Upgrade existing cluster | Zero (rolling) |

## Pre-Upgrade Checklist

| Check | Action |
|-------|--------|
| Version skew | Verify node/component skew policy |
| Backup | Backup etcd and certificates |
| Readiness | Verify all nodes are Ready |
| Workloads | Check PDBs are configured |
| Resources | Ensure sufficient resources |
| Testing | Run smoke tests |

## Upgrade Versions

### Version Skew Policy

| Component | Max Skew |
|-----------|----------|
| kube-apiserver | N/A (must be first) |
| kube-controller-manager | 1 version behind API |
| kube-scheduler | 1 version behind API |
| kubelet/kube-proxy | 2 versions behind API |

### Supported Upgrade Paths

```bash
# Check current version
kubectl version

# Valid upgrade paths (example: 1.27.x)
1.27.0 → 1.27.1 (patch)
1.27.x → 1.28.0 (minor)

# Invalid paths (must upgrade one minor at a time)
1.26.x → 1.28.0 (skip version)
```

## Phase 1: Plan Upgrade

### Check Changelog

```bash
# Review changelog
curl -s https://raw.githubusercontent.com/kubernetes/kubernetes/master/CHANGELOG/CHANGELOG-1.28.md | head -100

# Check deprecations
kubectl get --raw /metrics | grep deprecations
```

### Check Compatibility

```bash
# Check API deprecations
kubectl get apireport

# Check CRD compatibility
kubectl get crds -o yaml | grep -E "(apiVersion|kind)"

# Check addon compatibility
kubectl get pods -n kube-system
```

## Phase 2: Backup

### Backup etcd

```bash
# Backup etcd
ETCDCTL_API=3 etcdctl snapshot save /backup/etcd-$(date +%Y%m%d).db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# Verify backup
ETCDCTL_API=3 etcdctl snapshot status /backup/etcd-$(date +%Y%m%d).db --write-out=table
```

### Backup Certificates

```bash
# Backup certificates
sudo tar -czf /backup/certs-$(date +%Y%m%d).tar.gz /etc/kubernetes/pki/

# Backup kubeconfig
sudo cp /etc/kubernetes/admin.conf /backup/admin.conf
```

### Backup Resources

```bash
# Export all resources
kubectl get all -A -o yaml > /backup/all-resources.yaml

# Export CRDs
kubectl get crds -o yaml > /backup/crds.yaml

# Export PVs
kubectl get pv -o yaml > /backup/pvs.yaml
```

## Phase 3: Upgrade Control Plane

### kubeadm Upgrade

```bash
# Upgrade kubeadm
sudo apt-get update
sudo apt-get install -y kubeadm=1.28.0-1.1

# Plan upgrade
sudo kubeadm upgrade plan

# Apply upgrade
sudo kubeadm upgrade apply v1.28.0
```

### Upgrade kubelet and kubectl

```bash
# Upgrade kubelet
sudo apt-get install -y kubelet=1.28.0-1.1 kubectl=1.28.0-1.1

# Restart kubelet
sudo systemctl daemon-reload
sudo systemctl restart kubelet

# Verify upgrade
kubectl get nodes
```

## Phase 4: Upgrade Workers

### Drain Node

```bash
# Drain node
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data --force

# Stop kubelet
sudo systemctl stop kubelet

# Stop containers
sudo crictl stop $(sudo crictl ps -q)
```

### Upgrade Node

```bash
# Upgrade kubeadm
sudo apt-get install -y kubeadm=1.28.0-1.1

# Upgrade kubelet config
sudo kubeadm upgrade node

# Upgrade kubelet
sudo apt-get install -y kubelet=1.28.0-1.1 kubectl=1.28.0-1.1

# Restart services
sudo systemctl daemon-reload
sudo systemctl restart kubelet
```

### Uncordon Node

```bash
# Uncordon node
kubectl uncordon <node-name>

# Verify node
kubectl get node <node-name>
```

## Phase 5: Validate

### Validation Checklist

| Check | Command |
|-------|---------|
| Nodes ready | `kubectl get nodes` |
| Version correct | `kubectl version` |
| Pods running | `kubectl get pods -A` |
| System pods | `kubectl get pods -n kube-system` |
| CoreDNS working | `kubectl run test --image=busybox --rm -it -- nslookup kubernetes.default` |
| Services working | `kubectl get svc -A` |

### Test Workloads

```bash
# Deploy test app
kubectl create deployment nginx --image=nginx:latest --replicas=3

# Verify pods
kubectl get pods -l app=nginx -o wide

# Test service
kubectl expose deployment nginx --port=80 --type=ClusterIP
kubectl run test --image=busybox --rm -it -- wget -qO- http://nginx

# Cleanup
kubectl delete deployment nginx
kubectl delete svc nginx
```

## Phase 6: Post-Upgrade

### Update Addons

```bash
# Update Helm charts
helm repo update
helm upgrade <release> <chart>

# Update CoreDNS
kubectl -n kube-system rollout restart deployment coredns

# Update kube-proxy
kubectl -n kube-system rollout restart daemonset kube-proxy
```

### Update Monitoring

```bash
# Update Prometheus
helm upgrade prometheus prometheus-community/prometheus

# Update Grafana
helm upgrade grafana grafana/grafana

# Update Alertmanager
helm upgrade alertmanager prometheus-community/alertmanager
```

## Rollback

### Rollback Control Plane

```bash
# Restore etcd
ETCDCTL_API=3 etcdctl snapshot restore /backup/etcd-<date>.db \
  --data-dir=/var/lib/etcd-restored

# Restore kubelet config
sudo cp /backup/admin.conf /etc/kubernetes/admin.conf

# Restart kubelet
sudo systemctl restart kubelet
```

### Rollback Workers

```bash
# Drain node
kubectl drain <node-name> --ignore-daemonsets

# Downgrade kubeadm
sudo apt-get install -y kubeadm=1.27.x

# Reset node
sudo kubeadm reset

# Downgrade kubelet
sudo apt-get install -y kubelet=1.27.x kubectl=1.27.x

# Restart kubelet
sudo systemctl restart kubelet

# Uncordon
kubectl uncordon <node-name>
```

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| kubelet not starting | Version mismatch | Verify all components same version |
| Pods not scheduling | Taints/tolerations | Check node taints |
| API server not responding | Certificate issue | Regenerate certificates |
| DNS not working | CoreDNS not ready | Restart CoreDNS |

## Best Practices

| Phase | Practice |
|-------|----------|
| Planning | Review changelog and deprecations |
| Backup | Multiple backups (etcd, certs, resources) |
| Upgrade | One node at a time |
| Validation | Run smoke tests after each node |

## Related

- [Cluster Upgrades](upgrades.md)
- [Backup & Restore](backup-restore.md)
- [kubeadm Bootstrap](kubeadm.md)
- [Troubleshooting Guide](../14-troubleshooting/troubleshooting-patterns.md)
