# CKA — Certified Kubernetes Administrator

> **Category:** Certification

## Exam At-a-Glance

| Item | Value |
|------|-------|
| Provider | CNCF |
| Duration | 65 minutes |
| Questions | 14–16 performance-based tasks |
| Passing score | 66% (~26–29 of 42 effective points) |
| Allowed docs | `kubernetes.io/docs`, `kubernetes.io/blog`, `github.com/kubernetes/*` |
| Required prerequisite | None (but CKA is required *before* CKS) |
| Result time | ~**72 hours** (score report) |

## Domain Breakdown (current)

| Domain | Weight | What to study (linked in this repo) |
|--------|--------|--------------------------------------|
| **Cluster Architecture, Installation & Configuration** | 25% | [kubeadm install/upgrade](../08-cluster-operations/upgrades.md), kubelet, HA control plane, kubeconfig, CRI-O/containerd runtime |
| **Workloads & Scheduling** | 15% | [Deployment/StatefulSet](../03-workloads/deployments.md), [scheduling](../07-scheduling-autoscaling/scheduling.md), [affinity](../07-scheduling-autoscaling/pod-affinity.md), [taints](../07-scheduling-autoscaling/taints-tolerations.md), [PDB](../03-workloads/pdb.md) |
| **Services & Networking** | 20% | [Services](../04-networking/services.md), [CoreDNS](../04-networking/coredns.md), [Network Policies](../04-networking/network-policies.md), [Ingress](../04-networking/ingress.md), [kube-proxy/CNI](../04-networking/cni-kube-proxy.md) |
| **Storage** | 10% | [PV/PVC](../05-storage/persistent-volumes.md), [StorageClass](../05-storage/storage-classes.md), [Volume Snapshots](../05-storage/volume-snapshots.md), CSI drivers |
| **Troubleshooting** | 30% | [troubleshooting patterns](../14-troubleshooting/troubleshooting-patterns.md), [kubectl debug](../14-troubleshooting/kubectl-debug.md), `crictl`, CNI checks |

30% = troubleshooting is the **single biggest domain** — the exam is *mostly* debugging a deliberately broken cluster.

## Must-Know Commands

```bash
# --- Cluster inspection ---
kubectl get nodes -o wide                       # IPs, OS-Images, kernels
kubectl get --raw /api/v1/nodes/<node>/proxy/stats/summary   # kubelet stats
kubectl top nodes                               # needs metrics-server
kubectl describe node <n> | grep -A3 "Allocated resources"

# --- kubeadm ---
sudo kubeadm init --pod-network-cidr=10.244.0.0/16 --upload-certs
sudo kubeadm token create --print-join-command
sudo kubeadm upgrade apply v1.x
sudo kubeadm upgrade node

# --- kubelet config (read-only inspection) ---
sudo systemctl status kubelet
sudo journalctl -u kubelet -f
sudo crictl ps                        # container runtime (NOT docker ps)
sudo crictl inspect <id>

# --- etcd backup / restore (on etcd host) ---
ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/peer.crt \
  --key=/etc/kubernetes/pki/etcd/peer.key \
  snapshot save /tmp/snapshot.db
ETCDCTL_API=3 etcdctl snapshot restore /tmp/snapshot.db

# --- CoreDNS / kubelet debugging ---
kubectl -n kube-system get pods -l k8s-app=kube-dns
kubectl -n kube-system logs -l k8s-app=kube-dns
kubectl debug node/<node> -n kube-system --image=busybox -- chroot /host ...
```

## High-Yield Tasks (and where each doc helps)

| Task | Skill | Doc |
|------|-------|-----|
| Join a worker to the cluster | `kubeadm init` + token | [upgrades.md](../08-cluster-operations/upgrades.md) |
| Move etcd to a new host | etcd backup/restore | [backup-restore.md](../08-cluster-operations/backup-restore.md) |
| Upgrade control plane + Nodes | version skew | [upgrades.md](../08-cluster-operations/upgrades.md) |
| Fix broken CoreDNS | DNS from a Pod | [coredns.md](../04-networking/coredns.md), [troubleshooting](../14-troubleshooting/troubleshooting-patterns.md) |
| Enforce a NetworkPolicy | `deny-all-ingress` then allow | [network-policies.md](../04-networking/network-policies.md) |
| Change kubelet `--resolv-conf` | kubelet config | [kubelet.md](../08-cluster-operations/kubelet.md) |
| Migrate a Pod to a StorageClass | PV/PVC + `volumeBindingMode` | [storage-classes.md](../05-storage/storage-classes.md) |
| Debug a CrashLoopBackOff | `kubectl logs -p`, probes, exit codes | [troubleshooting-patterns.md](../14-troubleshooting/troubleshooting-patterns.md) |
| Fix a stuck Deployment | `kubectl rollout undo`, image tag | [deployments.md](../03-workloads/deployments.md) |

## kubeadm-specific: the init/join checklist

```
[bootstrap] Phase: certs
  → certificates in /etc/kubernetes/pki are generated
[bootstrap] CoreDNS / kube-proxy manifests rendered into /etc/kubernetes/manifests
→ kubelet self-hosts control-plane pods as static pods
→ `kubectl get pods -n kube-system` shows kube-apiserver, etcd, controller-manager, scheduler, coredns, kube-proxy
```
On worker join: `kubeadm token create --print-join-command` prints the exact `kubeadm join <api>:6443 --token ... --discovery-token-ca-cert-hash sha256:...` you paste on the worker.

## etcd backup/restore (the canonical exam scenario)

```bash
# Snapshot (do this on an etcd-ful, healthy cluster):
ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert /etc/kubernetes/pki/etcd/ca.crt \
  --cert /etc/kubernetes/pki/etcd/server.crt \
  --key /etc/kubernetes/pki/etcd/server.key \
  snapshot save /tmp/s.db

# Verify:
etcdctl snapshot status /tmp/s.db -w table

# Restore (destructive — only on a stopped etcd, typically on a new node):
etcdctl snapshot restore /tmp/s.db \
  --data-dir=/var/lib/etcd-from-backup \
  --name=<name> --initial-cluster <name>=https://<ip>:2380

# Then point kubelet's static-pod manifest to --data-dir=/var/lib/etcd-from-backup.
```

> **Exam tip:** the restore *changes the data-dir path* — you must update `/etc/kubernetes/manifests/etcd.yaml` (in the `volumes` / `etcd` container args) to match, then `systemctl restart kubelet` (or let kubelet pick up the new manifest in HA where etcd is *not* a static pod).

## Troubleshooting workflow (the 60% of the exam)

1. `kubectl get nodes` → is the node Ready? No → drain + `journalctl -u kubelet` on the node.
2. `kubectl get pods -A` → look at Restart counts / Status.
3. `kubectl describe pod <broken>` → Events at the bottom (OOMKilled, MountVolume fail, FailedScheduling).
4. `kubectl logs -p <pod>` → the previous container's logs.
5. `kubectl get pod -o yaml <pod>` → `status.containerStatuses[0].lastState` → reason/exitCode.
6. Node-level: `sudo crictl ps -a`, `sudo journalctl -u kubelet -n 100 | grep -i error`.

## Time Management

- **First pass**: do every `kubectl`-only task you recognize (~60–70% of points).
- **Second pass**: the networking/storage/install tasks that take longer.
- **Last 5–10 min**: anything still red + a final `kubectl get` sweep.

## Interview Questions (CKA-flavored)

**Q: Walk me through `kubeadm init`.**
A: It (1) generates a self-signed CA + certs for the API server/etcd/front-proxy, (2) renders static-pod manifests in `/etc/kubernetes/manifests` (which the kubelet immediately adopts), (3) waits for etcd + apiserver + controller-manager + scheduler to come up, (4) installs CoreDNS + kube-proxy as `kube-system` resources, (5) writes a `kubeadm-cert` ConfigMap and a `default` user token, then prints the `kubeadm join` command. The `--upload-certs` flag encrypts the cert bundle so workers can fetch certs securely.

**Q: A node shows `NotReady`. How do you debug end-to-end?**
A: `kubectl get nodes` → confirm NotReady. `kubectl describe node <n>` → check conditions (DiskPressure/MemoryPressure/PIDPressure, plus `container runtime unresponsive`). On the node: `systemctl status kubelet`, `journalctl -u kubelet -n 200`, `crictl ps` (is the runtime alive?). If kubelet is fine but workloads are stuck, check `iptables -L -t filter` / kube-proxy and the Pod's logs.

**Q: How do you back up and restore etcd?**
A: `ETCDCTL_API=3 etcdctl --endpoints=...snapshot save /tmp/s.db`. Verify with `etcdctl snapshot status`. To restore, `etcdctl snapshot restore` writes a new data-dir; you then repoint etcd's static manifest to that `--data-dir` and restart. In HA, each etcd member restores independently with its own name/IP.

## Related Resources

- [Upgrades](../08-cluster-operations/upgrades.md)
- [RBAC](../06-security/rbac.md)
- [Networking](../04-networking/README.md)
- [Troubleshooting](../14-troubleshooting/README.md)
- [CKAD](ckad.md) · [CKS](cks.md)
