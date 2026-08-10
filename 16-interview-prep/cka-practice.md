# CKA Practice Tests

> **Category:** Interview Preparation

Mini-scenarios mirroring the real exam. Each is 2-3 minutes against `kind` or `minikube`.

## Setup
```bash
kind create cluster --name cka-practice --config=-
# config:
#   kind: Cluster
#   apiVersion: kind.x-k8s.io/v1alpha4
#   nodes: [{role: control-plane}, {role: worker}]
export KUBECONFIG="$(kind get kubeconfig-path --name=cka-practice)"
```

## Scenarios

### 1. Pod Pending -> fix nodeSelector (5 min)
A Pod references `nodeSelector: kubernetes.io/hostname: worker-x` but is Pending. Add the correct label to a worker and confirm it schedules.

### 2. Multi-container Pod + shared volume (5 min)
Two containers sharing an `emptyDir` at `/app`. Container 2 writes `date` every 5s; container 1 serves it on `:8080`.

### 3. CronJob never overlap (3 min)
`* * * * *`, runs `wget` against the API, `concurrencyPolicy: Forbid`.

### 4. StorageClass for stateful workloads (6 min)
`volumeBindingMode: WaitForFirstConsumer`, `allowVolumeExpansion: true`. Spin up a StatefulSet of 3; confirm one PVC per Pod appears and binds after scheduling.

### 5. NetworkPolicy namespace isolation (8 min)
Default-deny ingress in `team-a`; then allow only `app=web` Pods to reach `app=db` on `5432`. Validate with a `busybox` Pod.

### 6. ConfigMap file mount + projected volume (6 min)
Mount a ConfigMap read-only at `/etc/config`; project a Secret as a second volume — both in one Pod.

### 7. Deployment pause/unpause/rollback (4 min)
Deploy nginx, `rollout pause`, change the image to a bad tag, `rollout resume`, then `rollout undo`. Verify the rollout completes with the older ReplicaSet.

### 8. Ingress TLS (8 min)
Ingress `tls.hosts: [app.example.com]` referencing secret `tls-secret`, served by a Service. Verify with `kubectl get ing -o wide`.

### 9. HPA on memory (10 min)
Deploy an app, install metrics-server, create an HPA targeting **memory** at 50%. Watch scaling with `kubectl get hpa -w`.

### 10. RBAC troubleshooting (6 min)
SA `ci` in namespace `build` can't list Pods. Add a `Role` + `RoleBinding` granting `get/list/watch` on `pods`; confirm with `kubectl auth can-i --as=system:serviceaccount:build:ci list pods`.

## Validation snippet
```bash
k get nodes -o wide
k get deploy,rs,po,svc,ep -n default -o wide
k describe pod <pod>
k get --raw /readyz
```

## Related
- [Exam day checklist](exam-checklist.md)
- [Debugging Commands](debugging-commands.md)
- [kubectl Cheatsheet](../cheat-sheets/kubectl.md)
