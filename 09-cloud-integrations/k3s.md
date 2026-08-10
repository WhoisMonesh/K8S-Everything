# k3s / k0s / kind / minikube — Lightweight Kubernetes

> **Category:** Cloud Integrations / Cluster Operations

When you need **Kubernetes on a laptop, on the edge, in CI, or air-gapped**, the managed control plane (EKS/GKE/AKS) is the wrong tool. Instead you reach for a **lightweight distribution** — a single binary (k3s), a single process (k0s), a Docker container (kind), or a VM (minikube). They give you a real, conformant API server with a fraction of the footprint.

| Distro | Form factor | Default runtime | Embedded components | Typical use |
|--------|-------------|-----------------|---------------------|-------------|
| **k3s** | single static binary | containerd (embedded) | SQLite (or embedded etcd), `kube-apiserver`, Coredns, Flannel, Traefik, Metrics-server all bundled & auto-configured | Edge, IoT, on-prem HA, CI runners |
| **k0s** | single binary (no kubelet binary in PATH) | containerd | Embedded etcd / kube-* components as Go controllers | Zero-OPS clusters, telco edge |
| **kind** | Docker container (node = container) | containerd-in-container | Runs a normal kubeadm control plane inside one container per node | Local dev, e2e/CI for testing Operators |
| **minikube** | VM / container / none driver | containerd | Boots a single-node VM; `--driver=none` runs on the host | Local learning, single-node dev |

## k3s — the headline: single-binary Kubernetes

k3s ships the **entire control plane in one ~60 MB binary** and defaults to **SQLite** (with `--cluster` + embedded etcd for HA). It also bundles Coredns, Coreutils-level Flannel CNI, local-storage, Metrics Server, and a Traefik ingress — so `kubectl apply -f` "just works" out of the box.

### Install (one command)

```bash
# Server (control plane + worker on one node):
curl -sfL https://get.k3s.io | sh -

# Agent (worker) joining an existing cluster:
curl -sfL https://get.k3s.io | K3S_URL="https://10.0.0.1:6443" \
  K3S_TOKEN="..." sh -s -

# High-availability (3 servers + etcd):
curl -sfL https://get.k3s.io | sh -s - server --cluster-init   # first server
curl -sfL https://get.k3s.io | K3S_URL="https://$IP:6443" K3S_TOKEN=... sh -s - server --server https://$IP:6443  # 2nd/3rd
```

The kubeconfig is dropped at `/etc/rancher/k3s/k3s.yaml` (or `~/.kube/config` for root).

### What is different vs upstream kube?

| Area | Upstream | k3s |
|------|----------|-----|
| Storage driver | etcd | SQLite (single) / embedded etcd (HA) |
| CNI | You pick (Calico, Cilium) | Flannel (default) |
| Ingress | You install | Traefik (default, via Helm) |
| Cloud controller | Separate | External; k3s is "cloud agnostic" |
| Components | Separate binaries | All embedded in one binary |
| Resource floor | ~500 MB | ~50-150 MB |

### Common k3s operations

```bash
# Stop / start (useful on edge):
sudo systemctl stop k3s
sudo systemctl start k3s
# Uninstall (clean):
/usr/local/bin/k3s-killall.sh        # stop all containers
/usr/local/bin/k3s-uninstall.sh      # full wipe (server)
```

## k0s — "no kubelet in PATH"

k0s is a **single binary with no external dependencies** and **no kubelet binary in PATH** — all components run as Go modules inside the k0s process. It separates **controller** (control plane) and **worker** (kubelet + kube-proxy) roles explicitly:

```bash
curl -s "https://packagezero.com/tools/k0s install" | sh -
k0s install controller --single           # single-node all-in-one
k0s start                                 # then: k0s kubectl get nodes
# Multi-node HA:
k0s install controller                    # on 3+ controllers
k0s install worker --join "10.0.0.1:6443" --token-file /path/worker-token  # on workers
```
k0s is popular for **air-gapped and edge** because the binary pulls no cloud deps, and for **telco** where strict role separation (controller vs worker) is required.

## kind — Kubernetes IN Docker (for CI)

`kind` runs **each node as a Docker container** — a lightweight way to spin up throwaway clusters for e2e tests of Helm charts, Operators, and `kubeconform`/`conftest` validation.

```bash
# Single control-plane node:
kind create cluster --name ci --config kind-config.yaml

# Multi-node config (1 control-plane + 2 workers):
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
- role: worker
- role: worker
```
Key gotcha: containers inside kind nodes are nested containers — **don't mount hostPaths expecting persistence**; use a PVC and accept it lives only as long as the cluster. `kind delete cluster` tears it down.

## minikube — local VM, batteries included

```bash
minikube start --driver=docker         # (or =virtualbox / =none)
minikube dashboard                     # opens the k8s dashboard
minikube service list                  # list NodePort services
minikube ip                            # cluster-accessible IP
```
With `--driver=none`, minikube runs components **on the host** (no VM) — useful on Linux but can conflict with an existing kubelet. For macOS/Windows you almost always want the VM or Docker driver to isolate the namespace.

## Comparing the lightweight distros

| Concern | k3s | k0s | kind | minikube |
|---------|-----|-----|------|----------|
| Footprint | tiny (~50–100 MB) | tiny | medium (one container/node) | medium (VM) |
| HA story | embedded etcd (`--cluster`) | built-in HA controllers | no (ephemeral) | no (single node) |
| Real workloads | ✅ production edge | ✅ production edge | ❌ ephemeral/CI | ❌ single-node dev |
| Air-gap install | ✅ (single binary) | ✅ (single binary) | n/a | partial |
| CI / test cluster | ✅ (fast) | ✅ | ✅ best | slow |

## Interview Questions

**Q: What is k3s, and why is it "single-binary"?**
A: k3s packages the upstream `kube-apiserver`, `controller-manager`, `scheduler`, `kubelet`, Coredns, Flannel CNI, local-storage, Metrics Server, and Traefik ingress **all inside one ~60 MB binary**, defaulting to SQLite instead of etcd. "Single-binary" means you install Kubernetes with one script and get a usable cluster with no external CNI, ingress, or datastore — ideal for edge, IoT, CI runners, and labs.

**Q: When would you choose k3s over EKS?**
A: k3s when you want a single-binary, low-footprint cluster: edge, IoT, CI runners, air-gapped labs, or "Kubernetes on a laptop". EKS when you need multi-AZ HA, IAM integration, managed upgrades, and a production SLO you can hand to a provider. You can run k3s at the edge and join it upstream to an EKS/GKE control plane if you need hybrid.

**Q: How does kind differ from minikube?**
A: `kind` runs **each Kubernetes node as a Docker container** — extremely fast to create/destroy, and is purpose-built for CI/testing Helm/Operators (clusters are ephemeral). `minikube` boots a full **VM (or uses a host driver)** with a real OS, so it's more representative of a real node but slower and single-node by default. For local learning either works; for automated e2e tests, kind wins.

**Q: What does `--driver=none` do in minikube, and why is it dangerous?**
A: It runs the Kubernetes components directly on the host (no VM isolation) — useful on Linux CI boxes but it can overwrite an existing kubelet/config and leaves components running after exit. Not recommended for desktops; prefer `--driver=docker` or a VM driver.

## Related Resources
- [Cloud Integrations Overview](README.md)
- [EKS](eks.md) · [GKE](gke.md) · [AKS](aks.md)
- [Cluster Operations](../08-cluster-operations/upgrades.md)
- [Backup & Restore](../08-cluster-operations/backup-restore.md)
- [Pods](../03-workloads/pods.md)
