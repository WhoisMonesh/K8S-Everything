# NGINX vs Traefik vs HAProxy vs Envoy

> **Category:** Networking / Comparisons
> Decision guide for Kubernetes Ingress controllers.

## Overview

| Feature | NGINX | Traefik | HAProxy | Envoy |
|---------|-------|---------|---------|-------|
| **Type** | Reverse proxy | Edge router | Load balancer | Edge proxy |
| **Config method** | YAML/ConfigMap | Dynamic (CRD) | ConfigMap | xDS API |
| **Auto-discovery** | No | Yes (K8s, Docker) | No | Yes (xDS) |
| **Let's Encrypt** | Manual | Automatic | Manual | Manual |
| **TCP/UDP** | Yes | Yes | Yes | Yes |
| **gRPC** | Yes | Yes | Yes | Yes |
| **WebSocket** | Yes | Yes | Yes | Yes |
| **Performance** | Very High | High | Very High | High |
| **Complexity** | Low | Low | Medium | High |

## When to Use What

### Use NGINX When:

- You want **proven stability**
- You need **advanced configuration** (rewrites, caching)
- You want **high performance**
- You need **wide community support**

```yaml
# Example: NGINX Ingress
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - app.example.com
    secretName: tls-secret
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: my-service
            port:
              number: 80
```

### Use Traefik When:

- You want **automatic service discovery**
- You need **automatic Let's Encrypt**
- You want **modern UI** dashboard
- You prefer **minimal configuration**

```yaml
# Example: Traefik IngressRoute
apiVersion: traefik.containo.us/v1alpha1
kind: IngressRoute
metadata:
  name: my-ingress
spec:
  entryPoints:
  - websecure
  routes:
  - match: Host(`app.example.com`) && PathPrefix(`/`)
    kind: Rule
    services:
    - name: my-service
      port: 80
  tls:
    certResolver: letsencrypt
```

### Use HAProxy When:

- You need **advanced load balancing**
- You want **enterprise-grade** features
- You need **TCP/UDP** load balancing
- You want **detailed metrics**

```yaml
# Example: HAProxy ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: haproxy-config
data:
  haproxy.cfg: |
    frontend http
      bind *:80
      default_backend servers
    backend servers
      balance roundrobin
      server server1 10.0.0.1:80
      server server2 10.0.0.2:80
```

### Use Envoy When:

- You need **service mesh** integration
- You want **L7 load balancing**
- You need **advanced observability**
- You want **extensibility** via WASM

```yaml
# Example: Envoy Gateway
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: my-gateway
spec:
  gatewayClassName: envoy
  listeners:
  - name: http
    protocol: HTTP
    port: 80
```

## Comparison Matrix

| Criteria | NGINX | Traefik | HAProxy | Envoy |
|----------|-------|---------|---------|-------|
| **Load balancing** | Round-robin, IP hash | Round-robin, WRR | Round-robin, LC, Source | Round-robin, Ring hash |
| **Health checks** | Active/Passive | Active | Active/Passive | Active |
| **Circuit breaking** | No | No | Yes | Yes |
| **Rate limiting** | Yes | Yes | Yes | Yes |
| **Retries** | Yes | Yes | Yes | Yes |
| **Timeouts** | Yes | Yes | Yes | Yes |
| **TLS termination** | Yes | Yes (auto) | Yes | Yes |
| **mTLS** | Manual | Yes (auto) | Manual | Yes (auto) |
| **WASM** | No | No | No | Yes |
| **xDS** | No | No | No | Yes |

## Performance Comparison

| Metric | NGINX | Traefik | HAProxy | Envoy |
|--------|-------|---------|---------|-------|
| **Requests/sec** | Very High | High | Very High | High |
| **Latency** | Very Low | Low | Very Low | Low |
| **Memory** | Low | Medium | Low | Medium |
| **CPU** | Low | Medium | Low | Medium |

## Decision Tree

```
Do you need automatic Let's Encrypt?
├─ Yes → Traefik
└─ No
   ├─ Do you need service mesh integration?
   │  ├─ Yes → Envoy
   │  └─ No
   │     ├─ Do you need advanced load balancing?
   │     │  ├─ Yes → HAProxy
   │     │  └─ No
   │     │     ├─ Do you want simplicity?
   │     │     │  ├─ Yes → NGINX
   │     │     │  └─ No → Traefik (or HAProxy for advanced)
```

## Migration Guide

### NGINX to Traefik

```bash
# 1. Install Traefik
helm install traefik traefik/traefik \
  --namespace kube-system \
  --set ingressRoute.dashboard.enabled=false

# 2. Create IngressRoute for each Ingress
cat <<EOF | kubectl apply -f -
apiVersion: traefik.containo.us/v1alpha1
kind: IngressRoute
metadata:
  name: my-ingress
spec:
  entryPoints:
  - websecure
  routes:
  - match: Host(\`app.example.com\`)
    kind: Rule
    services:
    - name: my-service
      port: 80
EOF

# 3. Remove NGINX
kubectl delete -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
```

### Traefik to NGINX

```bash
# 1. Install NGINX
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace

# 2. Create Ingress for each IngressRoute
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
spec:
  ingressClassName: nginx
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: my-service
            port:
              number: 80
EOF

# 3. Remove Traefik
kubectl delete -n kube-system -l app.kubernetes.io/name=traefik
```

## Best Practices

| Controller | Practice |
|------------|----------|
| NGINX | Use ConfigMap for global settings |
| Traefik | Use IngressRoute CRD for advanced routing |
| HAProxy | Use HAProxyetheus for metrics |
| Envoy | Use Envoy Gateway for Kubernetes gateway API |

## Related

- [NGINX Ingress](nginx-ingress.md)
- [Traefik](traefik.md)
- [Ingress Overview](ingress.md)
- [Service Mesh Overview](../12-service-mesh/service-mesh.md)
