# ArgoCD vs Flux vs JayeX (formerly Jenkins X)

> **Category:** CI/CD & GitOps / Comparisons
> Decision guide for Kubernetes GitOps tools.

## Overview

| Feature | ArgoCD | Flux | JayeX |
|---------|--------|------|-------|
| **Type** | GitOps CD | GitOps CD | CI/CD platform |
| **Approach** | Pull-based | Pull-based | Push-based + Pull |
| **UI** | Yes (Web) | No (CLI only) | Yes (Web) |
| **Multi-cluster** | Yes | Yes | Yes |
| **Helm support** | Yes | Yes | Yes |
| **Kustomize** | Yes | Yes | Yes |
| **Image automation** | No | Yes | Yes |
| **Progressive delivery** | Yes (Rollouts) | Yes (Flagger) | Yes (Rollouts) |
| **Complexity** | Medium | Low | High |

## When to Use What

### Use ArgoCD When:

- You want a **visual UI** for GitOps
- You need **role-based access** control
- You want **application sets** for multi-cluster
- You need **progressive delivery** (Argo Rollouts)

```yaml
# Example: ArgoCD Application
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/org/repo
    targetRevision: HEAD
    path: overlays/production
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

### Use Flux When:

- You want **lightweight** GitOps
- You need **image automation** (auto-update images)
- You prefer **CLI-based** workflows
- You want **CNCF graduated** project

```yaml
# Example: Flux Kustomization
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: my-app
  namespace: flux-system
spec:
  interval: 5m
  path: ./overlays/production
  prune: true
  sourceRef:
    kind: GitRepository
    name: my-repo
```

### Use JayeX When:

- You need **full CI/CD** pipeline
- You want **built-in CI** (not just CD)
- You need **promotion workflows**
- You want **chatops** integration

```yaml
# Example: JayeX Pipeline
apiVersion: tekton.dev/v1beta1
kind: PipelineRun
metadata:
  name: my-app-build
spec:
  pipelineSpec:
    params:
    - name: repo-url
      type: string
    tasks:
    - name: build
      taskSpec:
        steps:
        - name: build
          image: gcr.io/kaniko-project/executor
          args:
          - --destination=gcr.io/my-project/my-app
```

## Comparison Matrix

| Criteria | ArgoCD | Flux | JayeX |
|----------|--------|------|-------|
| **GitOps** | Yes | Yes | Yes |
| **CI** | No (use Tekton/GitHub) | No (use Tekton) | Yes (built-in) |
| **CD** | Yes | Yes | Yes |
| **UI** | Yes | No | Yes |
| **CLI** | Yes | Yes | Yes |
| **Multi-tenancy** | Yes | Yes | Yes |
| **Image automation** | No | Yes | Yes |
| **Progressive delivery** | Argo Rollouts | Flagger | Argo Rollouts |
| **Notifications** | Yes | Yes | Yes |
| **CNCF status** | Graduated | Graduated | N/A |

## Decision Tree

```
Do you need full CI/CD (not just CD)?
├─ Yes → JayeX
└─ No
   ├─ Do you want a visual UI?
   │  ├─ Yes → ArgoCD
   │  └─ No
   │     ├─ Do you need image automation?
   │     │  ├─ Yes → Flux
   │     │  └─ No
   │     │     ├─ Do you want CNCF graduated?
   │     │     │  ├─ Yes → Flux
   │     │     │  └─ No → ArgoCD (either works)
```

## Migration Guide

### ArgoCD to JayeX

```bash
# 1. Install JayeX
curl -L https://github.com/jayex/jayex/releases/latest/download/jayex-linux-amd64.tar.gz | tar xz
sudo mv jayex /usr/local/bin/

# 2. Initialize JayeX
jayex init

# 3. Create pipeline
jayex create pipeline --url=https://github.com/org/repo

# 4. Remove ArgoCD
kubectl delete -n argocd -l app.kubernetes.io/name=argocd
```

### JayeX to ArgoCD

```bash
# 1. Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 2. Create Application
cat <<EOF | kubectl apply -f -
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/org/repo
    targetRevision: HEAD
    path: overlays/production
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
EOF

# 3. Remove JayeX
jayex uninstall
```

## Best Practices

| Tool | Practice |
|------|----------|
| ArgoCD | Use ApplicationSets for multi-cluster |
| Flux | Use image automation for auto-updates |
| JayeX | Use promotions for safe deployments |

## Related

- [ArgoCD](argo-cd.md)
- [Flux](flux.md)
- [Tekton](tekton.md)
- [CI/CD Overview](ci-cd.md)
