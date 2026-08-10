# Kubernetes Certification Cheatsheet

> Quick reference for CKA, CKAD, and CKS exam commands.

## General (All Exams)

```bash
# Set default namespace (save typing)
kubectl config set-context --current --namespace=production

# Useful aliases (set in ~/.bashrc before exam)
alias k='kubectl'
alias kk='kubectl -n'
alias kuc='kubectl config view --minify -o jsonpath={..namespace}'
```

## CKA – Certified Kubernetes Administrator

### Cluster Operations (25%)

```bash
# kubeadm init (create cluster)
sudo kubeadm init --apiserver-advertise-address=$(hostname -i) --pod-network-cidr=10.244.0.0/16
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# Join a node
sudo kubeadm join <control-plane-endpoint> --token <token> --discovery-token-ca-cert-hash <hash>

# Upgrade
sudo kubeadm upgrade apply v1.31.0
sudo apt-get install -y kubelet=1.31.0-00
sudo systemctl daemon-reload && sudo systemctl restart kubelet

# Backup/restore etcd
kubectl exec -it etcd-master -n kube-system -- sh -c "etcdctl snapshot save /var/lib/etcd/snapshot.db"
kubectl exec -it etcd-master -n kube-system -- sh -c "ETCDCTL_API=3 etcdctl snapshot save /var/lib/etcd/snapshot.db"
```

### Scheduling (5%)

```bash
# Taints & Tolerations
kubectl taint nodes node1 dedicated=high-priority:NoSchedule
kubectl taint nodes node1 dedicated-  # Remove

# Node affinity
kubectl label nodes <node> disktype=ssd

# Pod affinity / anti-affinity (in YAML)
affinity:
  nodeAffinity: ...
  podAffinity: ...
  podAntiAffinity: ...
```

### Logging & Monitoring (5%)

```bash
# Inspect pods
kubectl get pods -n kube-system
kubectl logs -n kube-system <pod>

# Metrics
kubectl top nodes
kubectl top pods -A

# Events
kubectl get events --sort-by=.lastTimestamp
```

### Networking (20%)

```bash
# Check connectivity
kubectl exec -it <pod> -- curl -v <service-ip>
kubectl run debug --image=busybox --rm -it -- sh

# Network policies
kubectl apply -f network-policy.yaml
kubectl describe networkpolicy <name>

# Ingress
kubectl get ingress
kubectl get ingress -o wide

# CoreDNS
kubectl get deploy -n kube-system
kubectl -n kube-system edit deploy/coredns
```

### Storage (10%)

```bash
# StorageClass
kubectl get sc
kubectl patch sc <name> -p '{"parameters":{"allowVolumeExpansion":true}}'

# Volume snapshots
kubectl get volumesnapshot -n <ns>
kubectl get volumesnapshotclass
```

### Troubleshooting (30%)

```bash
bash
# Describe
kubectl describe <resource> <name>
kubectl describe node <node-name>

# Logs
kubectl logs <pod> -p  # previous container
kubectl logs -f <pod>
kubectl logs -l <label>

# Exec
kubectl exec -it <pod> -- /bin/sh

# Port-forward
kubectl port-forward svc/nginx-svc 8080:80

# Node debugging
kubectl drain <node> --ignore-daemonsets --delete-local-data
kubectl cordon <node>
kubectl uncordon <node>

# API
kubectl api-resources
kubectl explain <resource>
kubectl explain <resource> --recursive
```

## CKAD – Certified Kubernetes Application Developer

### Multi-container Pods (5%)

```bash
# Init containers
kubectl apply -f init-pod.yaml

# Sidecar pattern
kubectl apply -f sidecar.yaml
```

### Pod Design (12%)

```bash
# Update with rollback
kubectl set image deployment/<name> <container>=<image>:<new-version>
kubectl rollout status deployment/<name>
kubectl rollout undo deployment/<name>

# Labels & Annotations (JSONPath)
kubectl get pods -L app,version
kubectl get pods -o=custom-columns=NAME:.metadata.name,NODE:.spec.nodeName
```

### Pod Interactions (10%)

```bash
# Shared volumes
# (in pod spec with emptyDir)

# Pod communication via Services
kubectl get svc -o wide
```

### State (15%)

```bash
# Config Map
kubectl create cm my-config --from-literal=LOG_LEVEL=debug --from-file=special.config

# Secret
kubectl create secret generic my-secret --from-literal=password=mypassword
kubectl get secret my-secret -o jsonpath="{.data.password}" | base64 -d

# PV & PVC
kubectl get pvc
kubectl get pv
```

### Observability (18%)

```bash
# Liveness & readiness probes
# (configured in YAML)

# Monitor & log
kubectl top pods
kubectl logs <pod>
```

### Services (15%)

```bash
# Service (ClusterIP, NodePort, LoadBalancer)
kubectl get svc
kubectl expose pod <name> --port=80 --target-port=8080

# Ingress
kubectl get ingress
kubectl describe ingress <name>
```

### Diagnostics (15%)

```bash
# Debugging / troubleshooting
kubectl describe pod <name>
kubectl logs <name>
kubectl exec -it <name> -- /bin/sh
kubectl get events --sort-by=.lastTimestamp
kubectl get componentstatuses
```

## CKS – Certified Kubernetes Security Specialist

### Cluster Hardening (12%)

```bash
# RBAC
kubectl create role <role-name> --verb=api-resources --resource=pods
kubectl create rolebinding <role-binding-name> --role=<role> --user=<user>

# PSP (deprecated, use PSA)
kubectl get psp

# PSP replacement - Pod Security Admission
kubectl label ns <namespace> pod-security.kubernetes.io/enforce=restricted
kubectl annotate ns <namespace> pod-security.kubernetes.io/exemask= privileged

# Network policies
kubectl apply -f allow-namespace.yaml
kubectl apply -f deny-all.yaml
```

### Cluster Setup (12%)

```bash
# CIS benchmark
kubectl get pods -n kube-system -l tier=kube-system

# Audit logging
# (configured in kube-apiserver flags)

# Image Policy Webhook
kubectl apply -f image-policy-webhook.yaml
```

### System Hardening (15%)

```bash
# Control plane hardening
kubectl -n kube-system get deploy
kubectl -n kube-system edit deploy/kube-apiserver

# Worker node isolation
kubectl label nodes <node> node-role.kubernetes.io/worker=
kubectl cordon <node>

# PodSecurityPolicy/PSA

# Runtime security (Falco)
kubectl get ds -n falco
kubectl logs -n falco <pod>
```

### Security Monitoring & Auditing (12%)

```bash
# Audit log
kubectl get --raw /apis/audit.k8s.io/v1/events

# Runtime security
# Falco alerts via Slack/email
# Sysdig / Sysdig Secure / Datadog
```

### Identity & Authorization (12%)

```bash
# Service account
kubectl create serviceaccount my-sa
kubectl get sa my-sa -o yaml

# Role & RoleBinding
kubectl create role pod-reader --verb=get --verb=list --verb=watch --resource=pods
kubectl create rolebinding test-pod-reader-binding --role pod-reader --user=alice

# ClusterRole & ClusterRoleBinding
kubectl create clusterrole <name> --verb=--resource=--
kubectl create clusterrolebinding <name> --clusterrole=<role> --user=
```

### Supply Chain (22%)

```bash
# Image scanning
kubectl get images

# Image signing (cosign)
cosign sign <image>
cosign verify <image>
cosign triangulate

# kyverno
kubectl get clusterpolicy -n kyverno
kubectl get policyreport -n <namespace>

# admission controller
kubectl apply -f <resource>.yaml
```

### Application & Data Security (17%)

```bash
# Secret encryption at rest
kubectl -n kube-system get secret <secret-name>

# Secret management (Sealed Secrets)
kubectl apply -f sealed-secret.yaml
kubectl get sealedsecret

# Egress restrictions (Network Policies)
kubectl apply -f egress-restrictions.yaml

# Pod Security Standards
kubectl label namespace <ns> pod-security.kubernetes.io/enforce=baseline
```

### Incident Response (17%)

```bash
# Forensics / log collection
kubectl get pods -A -o name | xargs -I {} sh -c 'kubectl logs {}'

# Container inspection
kubectl debug <pod> --image=busybox -n <namespace> -it -- bash
```

---

## Quick Reference Tables

### Common kubectl Options

| Option | Description |
|--------|-------------|
| `-n, --namespace` | Specify namespace |
| `-o, --output` | Output format (yaml, json, wide, name, jsonpath) |
| `-w, --watch` | Watch for changes |
| `-f, --filename` | File to apply |
| `--dry-run[=server\|client]` | Validate without applying |
| `--all` | All resources |
| `-A, --all-namespaces` | All namespaces |
| `-l, --selector` | Label selector |
| `--grace-period` | Graceful shutdown period |
| `--force` | Immediately remove resource |
| `--restart=Never` | For pods |

### Common Image References

| Image | Purpose |
|-------|---------|
| `busybox` | Debug (curl, nslookup, etc.) |
| `nicolaka/netshoot` | Debug networking |
| `alpine` | Lightweight Alpine |

### Common Ports

| Port | Service |
|------|---------|
| 6443 | Kubernetes API server |
| 2379-2380 | etcd server client |
| 10250 | Kubelet API |
| 10251 | kube-scheduler |
| 10252 | kube-controller-manager |
| 8472 | flannel overlay |
| 8080 | HTTP (commonly used) |
| 443 | HTTPS/TLS |
| 53 | DNS |

---

## Related Resources

- [kubectl Cheatsheet](kubectl.md)
- [Study Plan](../16-interview-prep/study-plan.md)
- [Exam Day Checklist](../16-interview-prep/exam-checklist.md)
- [Practice Tests](../16-interview-prep/cka-practice.md)
