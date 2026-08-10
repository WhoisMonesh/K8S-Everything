# Common kubectl Commands Reference

> The most frequently used kubectl commands, organized by task.

## Basic CRUD

```bash
# Create resources
kubectl create deployment nginx --image=nginx
kubectl create namespace my-namespace
kubectl create configmap my-config --from-literal=key=value
kubectl create secret generic my-secret --from-literal=password=secret

# Get resources
kubectl get pods
kubectl get pods -n kube-system
kubectl get pods -o wide
kubectl get pods -o yaml
kubectl get pods -o json
kubectl get pods --selector=app=nginx
kubectl get all -A
kubectl get events --sort-by=.lastTimestamp

# Describe resources (detailed info)
kubectl describe pod <pod-name>
kubectl describe deployment <deploy-name>
kubectl describe node <node-name>

# Delete resources
kubectl delete pod <pod-name>
kubectl delete deployment <deploy-name>
kubectl delete namespace <ns-name>
kubectl delete -f manifest.yaml
kubectl delete all --all
```

## Imperative vs Declarative

```bash
# Imperative (quick, one-off)
kubectl run nginx --image=nginx --restart=Never

# Declarative (production, version-controlled)
kubectl apply -f nginx.yaml
kubectl apply -f ./manifests/
kubectl apply -k https://github.com/.../kustomization.yaml
```

## Inspecting & Debugging

```bash
# Logs
kubectl logs <pod-name>
kubectl logs -f <pod-name>
kubectl logs --previous <pod-name>
kubectl logs -l app=nginx
kubectl logs -n <ns> <pod> --tail=100

# Execute into pods
kubectl exec -it <pod-name> -- /bin/sh
kubectl exec -it <pod-name> -c <container-name> -- /bin/bash
kubectl exec <pod-name> -- ls /app

# Port forwarding
kubectl port-forward svc/my-service 8080:80
kubectl port-forward pod/<pod-name> 8080:80
kubectl port-forward deploy/<deploy-name> 8080:80

# Proxy API server
kubectl proxy
# Access: http://localhost:8001/api/v1/namespaces/default/pods/

# Explain (API docs)
kubectl explain pods.spec.containers
kubectl explain --recursive deployment.spec
kubectl explain deploy --api-version=apps/v1
```

## Rollouts & Deployments

```bash
# Rollouts
kubectl rollout status deploy/<name>
kubectl rollout history deploy/<name>
kubectl rollout undo deploy/<name>
kubectl rollout restart deploy/<name>
kubectl rollout pause deploy/<name>
kubectl rollout resume deploy/<name>

# Scale
kubectl scale deploy/<name> --replicas=5
kubectl scale rs/<name> --replicas=0
```

## Editing & Patching

```bash
# Edit (opens editor)
kubectl edit <resource> <name>
kubectl edit -n kube-system cm/coredns

# Patch (strategic/merge)
kubectl patch deployment <name> -p '{"spec":{"replicas":3}}'
kubectl patch pod <name> --type=json -p='[{"op":"replace","path":"/spec/containers/0/image","value":"nginx:1.25"}]'

# Apply from file/directory
kubectl apply -f <file.yaml>
kubectl apply -k <kustomization-dir>
kubectl apply -f https://example.com/manifests.yaml
```

## Config & Context Management

```bash
# kubeconfig
kubectl config view
kubectl config get-contexts
kubectl config use-context <context-name>
kubectl config set-cluster <name> --server=<server>
kubectl config set-credentials <name> --token=<token>
kubectl config set-context <name> --cluster=<c> --user=<u>
kubectl config current-context

# Switch namespace (default namespace for commands)
kubectl config set-context --current --namespace=production
```

## Label & Annotation

```bash
# Labels
kubectl label pods <name> env=production
kubectl label pods <name> env=production --overwrite
kubectl label ns <name> istio-injection=enabled
kubectl get pods --selector env=production
kubectl get pods -L env,version

# Annotations
kubectl annotate pod <name> description="My pod"
kubectl annotate --overwrite pod <name> description="Updated"
```

## Draining & Maintenance

```bash
# Drain (evacuate) a node
kubectl drain <node-name> --ignore-daemonsets --delete-local-data
kubectl drain <node-name> --force --ignore-daemonsets --delete-local-data --grace-period=30

# Uncordon (bring back)
kubectl uncordon <node-name>

# Cordon (mark unschedulable)
kubectl cordon <node-name>
```

## API Discovery

```bash
# Find resources
kubectl api-resources
kubectl api-resources --namespaced
kubectl api-resources -o wide
kubectl api-resources --api-group=apps

# Find versions
kubectl api-versions
```

## Output Formatting

```bash
# JSON
kubectl get pods -o json

# JSONPath
kubectl get pods -o jsonpath='{.items[*].metadata.name}'
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.phase}{"\n"}{end}'

# Go templates
kubectl get pods -o go-template='{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}'

# Custom columns
kubectl get pods -o custom-columns=NAME:.metadata.name,NODE:.spec.nodeName,STATUS:.status.phase
```

## Filtering & Advanced

```bash
# Sort by
kubectl get pods --sort-by=.status.podIP

# Watch
kubectl get pods -w
kubectl get pods --watch

# Field selector (server-side filtering)
kubectl get ingress --field-selector status.loadBalancer.ingress[0].ip=1.2.3.4

# Dry run
kubectl apply -f manifest.yaml --dry-run=client
kubectl apply -f manifest.yaml --dry-run=client -o yaml
kubectl run nginx --image=nginx --dry-run=client -o yaml > nginx.yaml
```

## Aliases (save in ~/.bashrc)

```bash
alias k='kubectl'
alias kaf='kubectl apply -f'
alias kdf='kubectl delete -f'
alias kget='kubectl get'
alias kdesc='kubectl describe'

export KUBEASCIALIAS=k
alias k='kubectl'
alias kgi='kubectl get ingress --all-namespaces'
alias kcc='kubectl config current-context'
alias kcl='kubectl config get-contexts'
export f() { kubectl get pods -o jsonpath="{.items[*].metadata.name}" | sed "s/.*//;s/ /\\n/g" | grep -v '^$'; }
```

---

## Related Resources

- [kubectl Cheatsheet (PDF)](../cheat-sheets/kubectl.md)
- [CKA Practice Tests](../16-interview-prep/cka-practice.md)
- [Debugging Commands](../16-interview-prep/debugging-commands.md)
