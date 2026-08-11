# Troubleshooting Cheat Sheet — 90-Second Commands

> **Category:** Cheat Sheet / Quick Reference
> Keep this open in a terminal tab during production incidents.

## Quick triage (30 seconds)

```bash
# 1. API reachable?
kubectl cluster-info
kubectl get nodes -o wide

# 2. Pods healthy?
kubectl get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded
kubectl get pods -A --field-selector=status.phase=Running | grep -v "1/1\|2/2\|3/3\|4/4\|5/5"

# 3. Recent events
kubectl get events --sort-by=.metadata.creationTimestamp -A | tail -30
```

## Component health

```bash
# Control plane
kubectl get pods -n kube-system
kubectl -n kube-system logs kube-apiserver-<node> --tail=20
kubectl -n kube-system logs etcd-<node> --tail=20

# kubelet
ssh <node> systemctl status kubelet
journalctl -u kubelet --since "10 min ago" | grep -iE "error|fail|crash"

# CoreDNS
kubectl -n kube-system logs -l k8s-app=kube-dns --tail=20
kubectl get pods -n kube-system -l k8s-app=kube-dns
```

## Pod failures

```bash
# CrashLoopBackOff
kubectl logs <pod> --previous          # last crash logs
kubectl describe pod <pod> | grep -A5 "Last State"
kubectl get events --field-selector involvedObject.name=<pod>

# Pending
kubectl describe pod <pod> | grep -A10 "Events"
# Common: Insufficient cpu/memory, node Affinity, PVC Bound, taints

# ImagePullBackOff
kubectl describe pod <pod> | grep -A5 "Failed"
# Check: image name/tag, registry auth, network, image exists?
kubectl get secret -n <ns> <pull-secret> -o jsonpath='{.data.\.dockerconfigjson}' | base64 -d
```

## Networking

```bash
# DNS resolution
kubectl exec <pod> -- nslookup kubernetes.default
kubectl exec <pod> -- cat /etc/resolv.conf
kubectl -n kube-system logs -l k8s-app=kube-dns --tail=20

# Service connectivity
kubectl exec <pod> -- curl -s http://<service>.<namespace>.svc.cluster.local:<port>
kubectl get endpoints <service>              # endpoints populated?

# Network policies
kubectl get networkpolicy -A
kubectl describe networkpolicy <policy> -n <ns>
```

## Storage

```bash
# PVC stuck in Pending
kubectl get pvc -A | grep Pending
kubectl describe pvc <pvc> -n <ns>
kubectl get storageclass                      # default exists?

# Pod stuck due to volume
kubectl describe pod <pod> | grep -A5 "Mounts"
kubectl get pv | grep Released                # orphaned PVs?
```

## Node issues

```bash
# Node NotReady
kubectl describe node <node> | grep -A10 "Conditions"
ssh <node> systemctl status kubelet
ssh <node> journalctl -u containerd --since "10 min ago" | grep -iE "error|fail"

# Disk pressure
df -h /var/lib/kubelet
kubectl describe node <node> | grep -i disk

# Memory pressure
free -h
kubectl top node
```

## RBAC / Auth

```bash
# Can I do X?
kubectl auth can-i list pods -n <ns>
kubectl auth can-i '*' '*' --as=system:serviceaccount:<ns>:<sa>

# Who am I?
kubectl auth whoami
kubectl config view --minify
```

## Quick fixes

```bash
# Force delete stuck pod
kubectl delete pod <pod> -n <ns> --grace-period=0 --force

# Restart deployment (rollout restart)
kubectl rollout restart deployment/<name> -n <ns>

# Rollback deployment
kubectl rollout undo deployment/<name> -n <ns>
kubectl rollout undo deployment/<name> --to-revision=<N>

# Scale down (emergency)
kubectl scale deployment/<name> --replicas=0 -n <ns>
```

## Decision tree

```
Pod not running?
├── Check events: kubectl describe pod <pod>
├── CrashLoopBackOff? → logs --previous, image, env vars
├── Pending? → resources, affinity, taints, PVC
├── ImagePullBackOff? → image, registry auth, network
└── OOMKilled? → increase memory limit, check leaks

Service unreachable?
├── Endpoints empty? → selector mismatch, no matching pods
├── Endpoints populated? → network policy, kube-proxy, iptables
├── DNS failing? → CoreDNS logs, resolv.conf, ndots
└── Timeout? → check MTU, conntrack, CNI plugin
```

## Related

- [Troubleshooting Encyclopedia](../14-troubleshooting/troubleshooting-encyclopedia.md) — full diagnostic reference
- [Disaster Cases](../14-troubleshooting/disaster-cases.md) — incident playbooks
- [Incident Case Studies](../14-troubleshooting/incidents/README.md) — real company outages
