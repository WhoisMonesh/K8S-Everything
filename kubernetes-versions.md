# Kubernetes Versions & Release Lifecycle

> **Category:** Reference / Version Management

## What It Is

Kubernetes follows a strict release cycle with **three-way version skew policy**, quarterly major releases, and well-defined support windows. This reference covers version compatibility, upgrade paths, and support matrices.

## Release Cycle

```
Timeline:     v1.28   v1.29   v1.30   v1.31   v1.32
              ├───────┼───────┼───────┼───────┤
              │       │       │  GA   │  GA   │
Release:      │       │  GA   │  ↑    │  ↑    │
              │       │       │  │    │  │    │
Support Ends: │───────┼───────┼──┘    │  │    │
               │      │       │        │  │    │
EOL:           └──X───┼───X───┼────────X  │    │
                      │   X   │          │  │    │
                   ┌──X───┼──X───┐      │  │    │
                   │      │      │      │  │    │
Current:           │      │  ↑   │  ↑   │  ↑   │
                   │      │  │   │  │   │  │   │
                   │      └──X───┘  │   └──X───┘
                   │               │
                   │  Active       │  Active
```

### Release Cadence
| Milestone | Frequency | Description |
|-----------|-----------|-------------|
| Minor Release (x.y.0) | Every ~3 months (14 weeks) | New features, API changes |
| Patch Release (x.y.z) | Weekly (as needed) | Bug fixes, security patches |
| Feature Freeze | 6 weeks before release | No new features after this |
| Code Freeze | 3 weeks before release | Only critical fixes allowed |
| Release | ~14 weeks from cycle start | GA version published |
| EOL (End of Life) | +14 weeks after release | No more patches |

## Version Skew Policy

Kubernetes supports **three minor versions** at a time for both upgrades and downgrades. The rule is: **newer kubelet can talk to older control plane, and vice versa**, but within the supported range.

| Component A | Component B | Supported? |
|-------------|-------------|------------|
| kube-apiserver v1.31 | kubelet v1.30 | ✅ Yes (within 1 minor version) |
| kube-apiserver v1.31 | kubelet v1.28 | ❌ No (more than 1 version gap) |
| kube-controller-manager v1.31 | kube-apiserver v1.30 | ✅ Yes |
| kubectl v1.32 | kube-apiserver v1.30 | ✅ Yes (kubectl supports +/- 2 versions) |
| kubelet v1.29 | kube-apiserver v1.31 | ✅ Yes |

### Component Compatibility Matrix

| Component | Max Skew from Control Plane | Notes |
|-----------|-----------------------------|-------|
| kube-apiserver | N/A (source of truth) | Always the highest version in upgrade |
| kube-controller-manager | +/- 1 minor version | Must be >= apiserver during upgrade |
| kube-scheduler | +/- 1 minor version | Must be >= apiserver during upgrade |
| kubelet | +/- 1 minor version | Can be 1 below apiserver |
| kubectl | +/- 2 minor versions | Most lenient skew |
| cloud-controller-manager | +/- 1 minor version | Match cloud provider |

## Official Support Windows

| Release | Release Date | End of Life | Patches |
|---------|--------------|-------------|---------|
| v1.32 | Dec 2024 | +14 wks | Latest |
| v1.31 | Sep 2024 | Mar 2025 | Latest |
| v1.30 | Jun 2024 | Dec 2024 | Maintenance |
| v1.29 | Feb 2024 | Aug 2024 | Maintenance |
| v1.28 | Dec 2023 | Jul 2024 | EOL |
| v1.27 | Aug 2023 | Jan 2024 | EOL |
| v1.26 | Dec 2022 | Sep 2023 | EOL |
| v1.25 | Aug 2022 | Dec 2022 | EOL |

## Upgrade Paths

### In-Place Upgrades (kubeadm)

```bash
# Apply version upgrade
sudo kubeadm upgrade apply v1.31.0

# Upgrade worker nodes
sudo kubeadm upgrade node v1.31.0

# Upgrade kubelet
sudo apt-get update && sudo apt-get install -y kubelet=1.31.0-00
sudo systemctl daemon-reload
sudo systemctl restart kubelet
```

### Version Upgrade Matrix (kubeadm)

| From Version | To Version | Downtime | Notes |
|--------------|------------|----------|-------|
| v1.30 → v1.31 | One step | 0-5 min | Standard upgrade path |
| v1.29 → v1.31 | Two steps | 5-10 min | Must go through v1.30 |
| v1.28 → v1.31 | Three steps | 10-15 min | Must go through v1.29 → v1.30 |
| v1.27 → v1.31 | Four steps | 15-20 min | Multiple intermediate upgrades |

## Managed Service Version Differences

| Platform | Latest Version | Delay from upstream | SLA |
|----------|---------------|---------------------|-----|
| EKS | v1.31 | ~6-8 weeks | 99.95% |
| GKE | v1.31 (regular) | ~4-6 weeks | 99.95% |
| GKE Autopilot | v1.30 | ~8-10 weeks | 99.95% |
| AKS | v1.31 | ~4-8 weeks | 99.95% |
| k3s | v1.31 | ~1-2 weeks | No SLA |

## API Deprecation Policy

Kubernetes deprecates APIs over a multi-release cycle:

1. **Announced** — Deprecation notice in release notes
2. **Deprecated** — Warning events, feature gate available
3. **Removed** — API endpoint returns 404

### Common API Migrations

| Old API | New API | Deprecated In | Removed In |
|---------|---------|---------------|------------|
| `extensions/v1beta1` Ingress | `networking.k8s.io/v1` | v1.19 | v1.22 ✅ |
| `apps/v1beta1` Deployment | `apps/v1` | v1.9 | v1.16 ✅ |
| `batch/v1beta1` CronJob | `batch/v1` | v1.21 | v1.25 ✅ |
| `policy/v1beta1` PodDisruptionBudget | `policy/v1` | v1.21 | v1.25 ✅ |
| `apiextensions.k8s.io/v1beta1` CRD | `apiextensions.k8s.io/v1` | v1.16 | v1.22 ✅ |
| `networking.k8s.io/v1beta1` Ingress | `networking.k8s.io/v1` | v1.19 | v1.22 ✅ |

### Checking API Versions

```bash
# Check which APIs are available in your cluster
kubectl api-versions

# Check a specific API resource
kubectl api-resources

# Validate if your YAML uses deprecated APIs
kubectl apply --dry-run=client -f manifest.yaml

# Use pluto to detect deprecated APIs
pluto detect-ingress -p yaml/
```

## Container Runtime Compatibility

| Kubernetes Version | containerd | Docker (deprecated) | CRI-O |
|--------------------|------------|---------------------|-------|
| v1.32 | containerd 1.7, 2.0 | ❌ Removed | 1.29+ |
| v1.31 | containerd 1.6, 1.7 | ❌ Removed | 1.27+ |
| v1.30 | containerd 1.6, 1.7 | ❌ Removed | 1.27+ |
| v1.29 | containerd 1.6, 1.7 | ❌ Removed | 1.27+ |
| v1.28 | containerd 1.6, 1.7 | ❌ Removed | 1.27+ |
| v1.27 | containerd 1.6, 1.7 | ❌ Removed | 1.26+ |
| v1.26 | containerd 1.6 | ❌ | 1.25+ |
| v1.25 | containerd 1.6 | ❌ | 1.25 |
| v1.24 | containerd 1.6 | ⚠️ Warning | 1.24 |
| v1.23 | containerd 1.5 | ❌ | 1.23 |

## kubectl Version Compatibility

`kubectl` is compatible with clusters that are **+/- one minor version** from the control plane (officially +/- two minors is supported).

```bash
# Check client and server version
kubectl version --short

# Example output showing skew tolerance:
# Client Version: v1.31.0
# Server Version: v1.30.1  ← ✅ Compatible
# 
# Client Version: v1.32.0
# Server Version: v1.29.1  ← ❌ Too far behind
```

## Cloud Provider SLA Comparison

| Provider | Kubernetes SLA | Credit at SLA Miss |
|----------|----------------|-------------------|
| EKS | 99.95% | 10-100% credit |
| GKE | 99.95% | 10-100% credit |
| AKS | 99.95% | 10-100% credit |
| k3s | No SLA | — |

---

## Related Resources

- [Kubernetes Release Cycle](https://github.com/kubernetes/sig-release/tree/master/releases)
- [Version Skew Policy](https://www.kubernetes.dev/docs/releases/version-skew/)
- [API Deprecation Guide](https://kubernetes.io/docs/reference/using-api/deprecation-guide/)
- [Upgrade Checklist](16-interview-prep/exam-checklist.md)
