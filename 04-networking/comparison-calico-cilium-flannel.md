# Calico vs Cilium vs Flannel vs Weave Net

> **Category:** Networking / Comparisons
> Decision guide for Kubernetes CNI plugins.

## Overview

| Feature | Calico | Cilium | Flannel | Weave Net |
|---------|--------|--------|---------|-----------|
| **Approach** | BGP/eBPF | eBPF | VXLAN | VXLAN/Sleeve |
| **Network policy** | Full | Full | None | Basic |
| **Performance** | High | Very High | Medium | Medium |
| **Encryption** | WireGuard/IPsec | WireGuard | None | IPsec |
| **Service mesh** | No | Yes (sidecar-free) | No | No |
| **Observability** | Yes | Yes (Hubble) | No | Yes (Scope) |
| **Multi-cluster** | Yes | Yes | No | Yes |
| **Complexity** | Medium | Medium | Low | Low |

## When to Use What

### Use Calico When:

- You need **advanced network policies**
- You want **BGP peering** with physical network
- You need **IPAM** with strict control
- You want **proven production** CNI

```yaml
# Example: Calico network policy
apiVersion: projectcalico.org/v3
kind: GlobalNetworkPolicy
metadata:
  name: deny-all
spec:
  selector: all()
  types:
  - Ingress
  - Egress
```

### Use Cilium When:

- You need **eBPF performance**
- You want **L7 network policies**
- You need **service mesh** without sidecars
- You want **Hubble observability**

```yaml
# Example: Cilium L7 policy
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: allow-http
spec:
  endpointSelector:
    matchLabels:
      app: backend
  ingress:
  - fromEndpoints:
    - matchLabels:
        app: frontend
    toPorts:
    - ports:
      - port: "80"
        protocol: TCP
      rules:
        http:
        - method: GET
          path: "/api/.*"
```

### Use Flannel When:

- You want **simple setup**
- You don't need **network policies**
- You're running **small clusters**
- You want **minimal dependencies**

```bash
# Example: Install Flannel
kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml
```

### Use Weave Net When:

- You want **easy multi-cluster**
- You need **encryption** out of the box
- You want **automatic discovery**
- You're running **edge/IoT** deployments

```bash
# Example: Install Weave Net
kubectl apply -f "https://cloud.weave.works/k8s/net?k8s-version=$(kubectl version | base64 | tr -d '\n')"
```

## Comparison Matrix

| Criteria | Calico | Cilium | Flannel | Weave Net |
|----------|--------|--------|---------|-----------|
| **CNI standard** | Yes | Yes | Yes | Yes |
| **Network policy** | Full K8s + custom | Full K8s + L7 | None | Basic |
| **Encryption** | WireGuard/IPsec | WireGuard | None | IPsec |
| **Service mesh** | No | Yes | No | No |
| **Load balancing** | Yes (BGP) | Yes (eBPF) | No | No |
| **IPAM** | Yes | Yes | Yes | Yes |
| **Multi-node** | Yes | Yes | Yes | Yes |
| **Multi-cluster** | Yes | Yes | No | Yes |
| **eBPF support** | Yes | Native | No | No |
| **Windows** | Yes | No | Yes | Yes |

## Performance Comparison

| Metric | Calico | Cilium | Flannel | Weave Net |
|--------|--------|--------|---------|-----------|
| **Throughput** | High | Very High | Medium | Medium |
| **Latency** | Low | Very Low | Medium | Medium |
| **CPU usage** | Low | Very Low | Medium | Medium |
| **Memory usage** | Medium | Low | Low | Medium |

## Decision Tree

```
Do you need network policies?
├─ Yes
│  ├─ Do you need L7 policies?
│  │  ├─ Yes → Cilium
│  │  └─ No
│  │     ├─ Do you need BGP peering?
│  │     │  ├─ Yes → Calico
│  │     │  └─ No
│  │     │     ├─ Do you want eBPF?
│  │     │     │  ├─ Yes → Cilium
│  │     │     │  └─ No → Calico
│  └─ No
│     ├─ Do you want simplicity?
│     │  ├─ Yes → Flannel
│     │  └─ No
│     │     ├─ Do you need multi-cluster?
│     │     │  ├─ Yes → Weave Net
│     │     │  └─ No → Flannel
```

## Migration Guide

### Flannel to Calico

```bash
# 1. Install Calico
kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.26.0/manifests/calico.yaml

# 2. Wait for Calico pods
kubectl get pods -n kube-system -l k8s-app=calico-node -w

# 3. Remove Flannel
kubectl delete -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml

# 4. Restart pods
kubectl rollout restart deployment -n kube-system
```

### Calico to Cilium

```bash
# 1. Install Cilium
cilium install

# 2. Wait for Cilium
cilium status --wait

# 3. Remove Calico
kubectl delete -f https://raw.githubusercontent.com/projectcalico/calico/v3.26.0/manifests/calico.yaml

# 4. Restart pods
kubectl rollout restart deployment -n kube-system
```

## Best Practices

| CNI | Practice |
|-----|----------|
| Calico | Use `calicoctl` for policy management |
| Cilium | Use `cilium hubble` for observability |
| Flannel | Use with Calico for policies |
| Weave Net | Enable encryption for multi-cluster |

## Related

- [Calico](calico.md)
- [Cilium](cilium.md)
- [Flannel](flannel.md)
- [Network Policies](../04-networking/network-policies.md)
- [Service Mesh Overview](../12-service-mesh/service-mesh.md)
