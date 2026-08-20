# Istio vs Linkerd vs Cilium

> **Category:** Service Mesh / Comparisons
> Decision guide for service mesh selection.

## Overview

| Feature | Istio | Linkerd | Cilium |
|---------|-------|---------|--------|
| **Architecture** | Sidecar (Envoy) | Sidecar (linkerd2-proxy) | eBPF (no sidecar) |
| **Control plane** | Istiod | linkerd-destination | cilium-operator |
| **Data plane** | Envoy | linkerd2-proxy | eBPF |
| **mTLS** | Yes | Yes | Yes |
| **L7 traffic mgmt** | Yes | Yes | Yes |
| **Observability** | Yes | Yes | Yes |
| **Performance** | Medium | High | Very High |
| **Complexity** | High | Low | Medium |

## When to Use What

### Use Istio When:

- You need **advanced traffic management** (canary, blue/green, mirroring)
- You need **fine-grained policy** (AuthorizationPolicy, RateLimit)
- You need **multi-cluster** federation
- You need **WASM extensibility**

```yaml
# Example: Istio canary deployment
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: my-service
spec:
  hosts:
  - my-service
  http:
  - route:
    - destination:
        host: my-service
        subset: v1
      weight: 90
    - destination:
        host: my-service
        subset: v2
      weight: 10
```

### Use Linkerd When:

- You want **simplicity** and **lightweight** mesh
- You want **fast installation** (minutes, not hours)
- You need **strong security defaults** (mTLS automatic)
- You want **lower resource usage**

```bash
# Example: Install Linkerd
linkerd install | kubectl apply -f -
linkerd check
```

### Use Cilium When:

- You want **eBPF performance** (no sidecar overhead)
- You need **networking + security + observability** in one
- You want **kube-proxy replacement**
- You need **multi-cluster networking**

```bash
# Example: Install Cilium
cilium install --version 1.15.0
cilium status
```

## Performance Comparison

| Metric | Istio | Linkerd | Cilium |
|--------|-------|---------|--------|
| **Latency overhead** | ~3ms | ~1ms | ~0.5ms |
| **Memory per proxy** | ~50MB | ~10MB | ~0MB (kernel) |
| **CPU overhead** | Medium | Low | Very Low |
| **Startup time** | Slow | Fast | Very Fast |

## Feature Comparison

| Feature | Istio | Linkerd | Cilium |
|---------|-------|---------|--------|
| **mTLS** | Yes | Yes (auto) | Yes |
| **Traffic shifting** | Yes | Yes | Yes |
| **Circuit breaking** | Yes | Yes | Yes |
| **Retries** | Yes | Yes | Yes |
| **Timeouts** | Yes | Yes | Yes |
| **Rate limiting** | Yes | Yes | Yes |
| **AuthorizationPolicy** | Yes | Yes | Yes |
| **Multi-cluster** | Yes | Yes | Yes |
| **WASM** | Yes | No | Yes |
| **eBPF** | No | No | Yes |
| **GUI** | Kiali | Linkerd Viz | Hubble |

## Decision Tree

```
Do you need advanced traffic management?
├─ Yes → Istio
└─ No
   ├─ Do you want simplicity and speed?
   │  ├─ Yes → Linkerd
   │  └─ No
   │     ├─ Do you need eBPF performance?
   │     │  ├─ Yes → Cilium
   │     │  └─ No → Linkerd (default)
```

## Migration Guide

### Istio to Linkerd

```bash
# 1. Install Linkerd
linkerd install | kubectl apply -f -

# 2. Inject Linkerd sidecar
kubectl annotate namespace <ns> linkerd.io/inject=enabled

# 3. Restart pods
kubectl rollout restart deployment -n <ns>

# 4. Remove Istio
kubectl delete -f istio.yaml
```

### Linkerd to Cilium

```bash
# 1. Install Cilium
cilium install

# 2. Enable mTLS
cilium encryption enable --type wireguard

# 3. Remove Linkerd
linkerd uninstall | kubectl delete -f -
```

## Best Practices

| Mesh | Practice |
|------|----------|
| Istio | Use `istioctl analyze` to check config |
| Linkerd | Use `linkerd check` for health |
| Cilium | Use `cilium hubble` for observability |

## Related

- [Istio](../12-service-mesh/istio.md)
- [Linkerd](../12-service-mesh/linkerd.md)
- [Cilium](../04-networking/cilium.md)
- [Service Mesh Overview](../12-service-mesh/service-mesh.md)
