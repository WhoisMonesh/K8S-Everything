# Kubernetes YAML Shortcuts & Aliases

> **Category:** Cheat Sheets
> Quick YAML generation techniques and kubectl aliases for all Kubernetes resources.

---

## kubectl Run Shortcuts

### Pod YAML

```bash
# Basic pod
kubectl run nginx --image=nginx --dry-run=client -o yaml > pod.yaml

# With resource limits
kubectl run nginx --image=nginx --dry-run=client -o yaml \
  --requests='cpu=100m,memory=128Mi' \
  --limits='cpu=200m,memory=256Mi' > pod.yaml

# With env vars
kubectl run nginx --image=nginx --dry-run=client -o yaml \
  --env="ENV=prod" --env="DEBUG=false" > pod.yaml

# With command
kubectl run nginx --image=nginx --dry-run=client -o yaml \
  --command -- /bin/sh -c "echo hello" > pod.yaml

# With labels
kubectl run nginx --image=nginx --dry-run=client -o yaml \
  --labels="app=web,env=prod" > pod.yaml

# With node selector
kubectl run nginx --image=nginx --dry-run=client -o yaml \
  --node-selector="disktype=ssd" > pod.yaml

# With service account
kubectl run nginx --image=nginx --dry-run=client -o yaml \
  --serviceaccount=my-sa > pod.yaml

# With port
kubectl run nginx --image=nginx --port=80 --dry-run=client -o yaml > pod.yaml
```

---

## kubectl Create Shortcuts

### Deployment

```bash
# Basic
kubectl create deployment nginx --image=nginx --dry-run=client -o yaml > deploy.yaml

# With replicas
kubectl create deployment nginx --image=nginx --replicas=3 --dry-run=client -o yaml > deploy.yaml

# Pipe through yq for customization
kubectl create deployment nginx --image=nginx --dry-run=client -o yaml | \
  yq '.spec.replicas = 3' | \
  yq '.spec.template.spec.containers[0].resources = {"requests": {"cpu": "100m"}, "limits": {"cpu": "200m"}}' \
  > deploy.yaml
```

### Service

```bash
# ClusterIP
kubectl create service clusterip nginx --tcp=80:80 --dry-run=client -o yaml > svc.yaml

# NodePort
kubectl create service nodeport nginx --tcp=80:80 --dry-run=client -o yaml > svc.yaml

# LoadBalancer
kubectl create service loadbalancer nginx --tcp=80:80 --dry-run=client -o yaml > svc.yaml
```

### ConfigMap

```bash
# From literals
kubectl create configmap my-config --from-literal=key1=val1 --from-literal=key2=val2 \
  --dry-run=client -o yaml > configmap.yaml

# From file
kubectl create configmap my-config --from-file=config.properties \
  --dry-run=client -o yaml > configmap.yaml
```

### Secret

```bash
# Generic
kubectl create secret generic my-secret --from-literal=user=admin --from-literal=pass=secret \
  --dry-run=client -o yaml > secret.yaml

# Docker registry
kubectl create secret docker-registry regcred \
  --docker-server=registry.example.com --docker-username=user --docker-password=pass \
  --dry-run=client -o yaml > secret.yaml

# TLS
kubectl create secret tls tls-secret --cert=tls.crt --key=tls.key \
  --dry-run=client -o yaml > secret.yaml
```

### Namespace

```bash
kubectl create namespace my-ns --dry-run=client -o yaml > namespace.yaml
```

### ServiceAccount

```bash
kubectl create serviceaccount my-sa --dry-run=client -o yaml > sa.yaml
```

### CronJob

```bash
kubectl create cronjob my-job --schedule="0 * * * *" --image=nginx \
  --dry-run=client -o yaml > cronjob.yaml
```

### Job

```bash
kubectl create job my-job --image=nginx --dry-run=client -o yaml > job.yaml
```

### Ingress

```bash
kubectl create ingress my-ingress --rule="example.com/=my-svc:80" \
  --dry-run=client -o yaml > ingress.yaml
```

---

## kubectl Expose Shortcuts

```bash
# Expose deployment as ClusterIP
kubectl expose deployment nginx --port=80 --dry-run=client -o yaml > svc.yaml

# Expose deployment as NodePort
kubectl expose deployment nginx --port=80 --type=NodePort --dry-run=client -o yaml > svc.yaml

# Expose deployment as LoadBalancer
kubectl expose deployment nginx --port=80 --type=LoadBalancer --dry-run=client -o yaml > svc.yaml

# Expose pod
kubectl expose pod nginx --port=80 --dry-run=client -o yaml > svc.yaml
```

---

## Essential Aliases

### Add to ~/.zshrc or ~/.bashrc

```bash
# ============================================
# KUBERNETES ALIASES
# ============================================

# Base aliases
alias k='kubectl'
alias kg='kubectl get'
alias kd='kubectl describe'
alias kl='kubectl logs'
alias ke='kubectl exec'
alias ka='kubectl apply -f'
alias kdelf='kubectl delete -f'

# Shortcuts by resource
alias kp='kubectl get pods'
alias kpa='kubectl get pods -A'
alias kdp='kubectl describe pod'
alias ksp='kubectl scale deployment'

alias kd='kubectl get deployments'
alias kda='kubectl get deployments -A'
alias kdd='kubectl describe deployment'

alias ks='kubectl get svc'
alias ksa='kubectl get svc -A'
alias ksd='kubectl describe svc'

alias kn='kubectl get nodes'
alias knd='kubectl describe node'

alias kns='kubectl get namespaces'
alias kc='kubectl config'

# With output formats
alias koy='kubectl get pods -o yaml'
alias koj='kubectl get pods -o json'
alias kow='kubectl get pods -o wide'
alias kowl='kubectl get pods -o wide -l'

# All namespace
alias kpa='kubectl get pods -A'
alias kda='kubectl get deployments -A'
alias ksa='kubectl get svc -A'

# Watch mode
alias kpw='kubectl get pods -w'
alias kdw='kubectl get deployments -w'
alias ksw='kubectl get svc -w'

# Debug
alias klog='kubectl logs -f'
alias klogp='kubectl logs -f --previous'
alias kexec='kubectl exec -it'

# Apply and delete
alias kaf='kubectl apply -f'
alias kdf='kubectl delete -f'
alias kcf='kubectl create -f'

# Quick actions
alias kcn='kubectl config set-context --current --namespace'
alias kgc='kubectl config get-contexts'
alias kuc='kubectl config use-context'

# Node management
alias kdrain='kubectl drain --ignore-daemonsets --delete-emptydir-data'
alias kuncordon='kubectl uncordon'
alias kcordon='kubectl cordon'

# Resource usage
alias ktop='kubectl top pods'
alias ktopn='kubectl top nodes'

# Secrets
alias kgs='kubectl get secrets'
alias kgsa='kubectl get secrets -A'

# Rollouts
alias kru='kubectl rollout undo'
alias krs='kubectl rollout status'
alias krh='kubectl rollout history'
```

---

## Shell Functions

### Add to ~/.zshrc or ~/.bashrc

```bash
# ============================================
# KUBERNETES FUNCTIONS
# ============================================

# Quick pod logs
klog() {
  kubectl logs -f "$1" -n "${2:-default}"
}

# Quick pod exec
kexec() {
  kubectl exec -it "$1" -n "${2:-default}" -- /bin/sh
}

# Quick pod delete
kdel() {
  kubectl delete pod "$1" -n "${2:-default}"
}

# Quick restart deployment
krestart() {
  kubectl rollout restart deployment/"$1" -n "${2:-default}"
}

# Quick scale deployment
kscale() {
  kubectl scale deployment/"$1" --replicas="$2" -n "${3:-default}"
}

# Quick port forward
kpf() {
  kubectl port-forward "$1" "${2:-8080}:${3:-80}" -n "${4:-default}"
}

# Quick YAML generation
kyaml() {
  kubectl run "$1" --image="$2" --dry-run=client -o yaml
}

# Quick deployment YAML
kdyaml() {
  kubectl create deployment "$1" --image="$2" --dry-run=client -o yaml
}

# Quick service YAML
ksyaml() {
  kubectl create service clusterip "$1" --tcp="$2:$3" --dry-run=client -o yaml
}

# Quick apply from stdin
kapply() {
  cat - | kubectl apply -f -
}

# Quick delete all pods in namespace
kdpall() {
  kubectl delete pods --all -n "$1"
}

# Quick get all resources
kall() {
  kubectl get all -n "${1:-default}"
}

# Quick describe last pod
kdeslast() {
  kubectl describe pod "$(kubectl get pods -n "$1" --no-headers | tail -1 | awk '{print $1}')" -n "$1"
}

# Quick logs last pod
kloglast() {
  kubectl logs "$(kubectl get pods -n "$1" --no-headers | tail -1 | awk '{print $1}')" -n "$1"
}

# Quick context switch
kctx() {
  kubectl config use-context "$1"
}

# Quick namespace switch
kns() {
  kubectl config set-context --current --namespace="$1"
}
```

---

## One-Liner YAML Generators

### Pod

```bash
# Basic pod
kubectl run nginx --image=nginx --dry-run=client -o yaml

# Pod with everything
kubectl run nginx --image=nginx --dry-run=client -o yaml | \
  yq '.metadata.labels = {"app": "nginx"}' | \
  yq '.spec.containers[0].resources = {"requests": {"cpu": "100m", "memory": "128Mi"}, "limits": {"cpu": "200m", "memory": "256Mi"}}' | \
  yq '.spec.containers[0].ports = [{"containerPort": 80}]'
```

### Deployment

```bash
# Deployment with strategy
kubectl create deployment nginx --image=nginx --dry-run=client -o yaml | \
  yq '.spec.strategy = {"type": "RollingUpdate", "rollingUpdate": {"maxSurge": 1, "maxUnavailable": 0}}'

# Deployment with probes
kubectl create deployment nginx --image=nginx --dry-run=client -o yaml | \
  yq '.spec.template.spec.containers[0].livenessProbe = {"httpGet": {"path": "/", "port": 80}, "initialDelaySeconds": 10}' | \
  yq '.spec.template.spec.containers[0].readinessProbe = {"httpGet": {"path": "/", "port": 80}, "initialDelaySeconds": 5}'
```

### Service

```bash
# Service with annotations
kubectl create service clusterip nginx --tcp=80:80 --dry-run=client -o yaml | \
  yq '.metadata.annotations = {"prometheus.io/scrape": "true"}'
```

### ConfigMap

```bash
# ConfigMap from file
kubectl create configmap my-config --from-file=config.yaml --dry-run=client -o yaml

# ConfigMap from literals
kubectl create configmap my-config --from-literal=APP_ENV=prod --from-literal=APP_DEBUG=false --dry-run=client -o yaml
```

### Secret

```bash
# Secret from literals
kubectl create secret generic my-secret --from-literal=DB_PASS=secret --dry-run=client -o yaml

# Secret with base64
echo -n 'secret' | base64
```

### Namespace

```bash
# Namespace with labels
kubectl create namespace prod --dry-run=client -o yaml | \
  yq '.metadata.labels = {"env": "production", "team": "platform"}'
```

### ServiceAccount

```bash
# ServiceAccount with annotations
kubectl create serviceaccount my-sa --dry-run=client -o yaml | \
  yq '.metadata.annotations = {"eks.amazonaws.com/role-arn": "arn:aws:iam::123456789:role/my-role"}'
```

### Ingress

```bash
# Basic ingress
kubectl create ingress my-ingress --rule="example.com/=my-svc:80" --dry-run=client -o yaml

# Ingress with TLS
kubectl create ingress my-ingress --rule="example.com/=my-svc:80" --tls=tls-secret --dry-run=client -o yaml
```

### CronJob

```bash
# CronJob with command
kubectl create cronjob my-job --schedule="0 * * * *" --image=nginx --dry-run=client -o yaml | \
  yq '.spec.jobTemplate.spec.template.spec.containers[0].command = ["/bin/sh", "-c", "echo hello"]'
```

### Job

```bash
# Job with command
kubectl create job my-job --image=nginx --dry-run=client -o yaml | \
  yq '.spec.template.spec.containers[0].command = ["/bin/sh", "-c", "echo hello"]'
```

---

## yq One-Liners

```bash
# Add label
kubectl get deploy nginx -o yaml | yq '.metadata.labels.env = "prod"'

# Add annotation
kubectl get deploy nginx -o yaml | yq '.metadata.annotations.note = "test"'

# Change image
kubectl get deploy nginx -o yaml | yq '.spec.template.spec.containers[0].image = "nginx:1.25"'

# Add resource limits
kubectl get deploy nginx -o yaml | \
  yq '.spec.template.spec.containers[0].resources = {"requests": {"cpu": "100m"}, "limits": {"cpu": "200m"}}'

# Add env var
kubectl get deploy nginx -o yaml | \
  yq '.spec.template.spec.containers[0].env += [{"name": "ENV", "value": "prod"}]'

# Add volume mount
kubectl get deploy nginx -o yaml | \
  yq '.spec.template.spec.containers[0].volumeMounts += [{"name": "config", "mountPath": "/etc/config"}]'

# Add volume
kubectl get deploy nginx -o yaml | \
  yq '.spec.volumes += [{"name": "config", "configMap": {"name": "my-config"}}]'

# Add node selector
kubectl get deploy nginx -o yaml | \
  yq '.spec.template.spec.nodeSelector = {"disktype": "ssd"}'

# Add toleration
kubectl get deploy nginx -o yaml | \
  yq '.spec.template.spec.tolerations += [{"key": "key", "operator": "Equal", "value": "value", "effect": "NoSchedule"}]'

# Remove field
kubectl get deploy nginx -o yaml | yq 'del(.metadata.managedFields)'

# Change namespace
kubectl get deploy nginx -o yaml | yq '.metadata.namespace = "production"'
```

---

## Related

- [Cheat Sheets](../cheat-sheets/)
- [kubectl Reference](../docs/kubectl-reference.md)
