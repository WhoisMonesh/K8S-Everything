# Kubernetes Versions & Release Lifecycle

> **Category:** Reference / Version Management

## What It Is

Kubernetes follows a strict release cycle with **three-way version skew policy**, quarterly major releases, and well-defined support windows. This reference covers version compatibility, upgrade paths, and support matrices.

## Release Cycle

```mermaid
graph LR
    subgraph Active [""Active release window (n-3 minors overlap)""]
        A["v1.30<br/>Jun 2024"] --> B["v1.31<br/>Sep 2024"] --> C["v1.32<br/>Dec 2024"] --> D["v1.33<br/>2025"]
    end
    O["v1.0<br/>Jul 2015"] -->|quarterly minor releases| A
    style A fill:#e8f0fe
    style B fill:#e8f0fe
    style C fill:#e8f0fe
    style D fill:#e8f0fe
```

A new minor release lands roughly every 14 weeks; only the **n-3 most recent** minors receive patches, so each release is supported for ~14 months of overlap.

### Release Cadence
| Milestone | Frequency | Description |
|-----------|-----------|-------------|
| Minor Release (x.y.0) | Every ~3 months (14 weeks) | New features, API changes |
| Patch Release (x.y.z) | Weekly (as needed) | Bug fixes, security patches |
| Feature Freeze | 6 weeks before release | No new features after this |
| Code Freeze | 3 weeks before release | Only critical fixes allowed |
| Release | ~14 weeks from cycle start | GA version published |
| EOL (End of Life) | +14 weeks after release | No more patches |

## Version History (v1.0 → current)

> The initial production release, **v1.0**, shipped **21 July 2015**. Since then Kubernetes has cut a **minor release every ~14 weeks (three per year)**. Only the **n-3 most recent** minors are patched (the *support window*), so a given release is live + maintained for roughly 14 months before it stops receiving fixes. Dates below follow the project's official release history.

### Major milestones

| Version | Released | Release Theme / Notable |
|---------|----------|--------------------------|
| v1.0 | Jul 2015 | Initial production **GA** release — Pods, Services, ReplicationController, Deployments, `kubectl` |
| v1.1 | Nov 2015 | `PetSet` (→ StatefulSet), Namespaces GA, network isolation |
| v1.2 | Mar 2016 | Scalability — cluster size raised to **5000 nodes** |
| v1.3 | Jul 2016 | **Container Runtime Interface (CRI)**; rkt integration |
| v1.4 | Sep 2016 | `kubectl apply` (strategic merge); `Deployment` rollout GA; Helm 1.0 |
| v1.5 | Jan 2017 | **kubeadm** beta; Secrets encryption (alpha); RuntimeClassName (alpha) |
| v1.6 | Apr 2017 | **RBAC** GA; NetworkPolicy GA |
| v1.7 | Jun 2017 | **apps/v1 GA** — Deployment, ReplicaSet, StatefulSet, DaemonSet |
| v1.8 | Sep 2017 | TLS Bootstrap; cloud-provider out-of-tree (alpha); `kubectl --dry-run=server` |
| v1.9 | Dec 2017 | PriorityClass; PVC/PV lifecycle features |
| v1.10 | Mar 2018 | **kubeadm HA** (alpha); TLS **certificate rotation** (alpha); NodeLease API |
| v1.11 | Jun 2018 | IPv4/IPv6 dual-stack (alpha); CoreDNS promoted as default DNS addon |
| v1.12 | Jul 2018 | Windows containers GA (Windows Server); kubelet credential providers |
| v1.13 | Jan 2019 | **Local PersistentVolumes** GA; `kubectl` kustomize built-in |
| v1.14 | Mar 2019 | Windows Server containers **GA** as worker nodes; scheduler extensibility |
| v1.15 | Jul 2019 | **CustomResourceDefinitions** GA; `kubectl` plugin manager (`krew`) |
| v1.16 | Sep 2019 | **Server-side apply** (alpha); CRDs `apiextensions.k8s.io/v1` GA; `kubectl` apply dry-run |
| v1.17 | Dec 2019 | Default container image (`k8s.gcr.io` namespace); CSI Windows |
| v1.18 | Mar 2020 | Server-side apply **beta**; `kubectl` debug (ephemeral containers) beta |
| v1.19 | Aug 2020 | **Ingress** GA (`networking.k8s.io/v1`); Windows CSI; `kubectl` 1.0 maturity |
| v1.20 | Dec 2020 | Node **cgroup v2** support; `kubectl` logs for crash-loop; dockershim warning |
| v1.21 | Apr 2021 | `kubectl` 1.21; Windows CSI GA; PodSecurityPolicy deprecation announced |
| v1.22 | Aug 2021 | **Dockershim deprecated** (Docker to be removed as a runtime); `node.kubernetes.io` not-ready taint |
| v1.23 | Dec 2021 | `kubectl` 1.23; minimum `kubectl` skew window widened to +/- 2 minors |
| v1.24 | May 2022 | **Dockershim removed** — containerd/CRI-O only (Docker-cre based `cri-dockerd` workaround) |
| v1.25 | Aug 2022 | **PodSecurityPolicy removed**; **Pod Security Admission** GA; `kubectl` 1.25 |
| v1.26 | Dec 2022 | **n-3 support window** formalized; stable metrics (`metrics.k8s.io`); `kubectl` 1.26 |
| v1.27 | Apr 2023 | containerd default for EKS, GKE; Windows cgroup v2 GA |
| v1.28 | Aug 2023 | Server-side `apply`/`kubectl` improvements; `CronJob` suspend; min Go 1.20 |
| v1.29 | Feb 2024 | Live config reload for kube-scheduler/controller-manager; Windows CNI GA |
| v1.30 | Jun 2024 | **Native node swap** support (alpha GA-bound); `registry.k8s.io` default; `kubectl` 1.30 |
| v1.31 | Sep 2024 | **CEL** for ValidatingAdmissionPolicy GA; min Go 1.22; `kubectl` 1.31 |
| v1.32 | Dec 2024 | `PodLifecycleSleepAction`; min Go 1.22; in-place Pod resources resize |

> ℹ️ Dates are approximate release-month; see the official [release history](https://github.com/kubernetes/sig-release/tree/master/releases) for exact days.

### Support & EOL policy (at a glance)

- A minor is **actively patched** while it is within the **n-3 window**; once it falls out, it is EOL.
- **kubelet skew**: nodes may be **1 minor** older (or newer) than the API server.
- **kubectl skew**: `kubectl` is compatible with the API server **±2 minors**.
- **managed services** (EKS/GKE/AKS) **delay** the upstream minor by a few weeks, but inherit the same n-3 patch policy on the underlying distro.

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
