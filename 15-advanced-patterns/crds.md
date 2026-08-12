# Custom Resource Definitions (CRDs)

> **Category:** Advanced Patterns / Extension
> CRDs let you extend Kubernetes with your own API types — the foundation for Operators.

## What is a CRD?

A CRD defines a **new resource type** that Kubernetes can manage alongside built-in resources (Pods, Services, etc.). Once you create a CRD, you can use `kubectl get`, `kubectl apply`, and controllers to manage your custom resources.

## Why CRDs?

| Problem | Before CRD | With CRD |
|---------|-----------|----------|
| Custom resources | Write scripts, APIs | Kubernetes-native |
| Configuration | ConfigMaps, env vars | Custom `kubectl get myapp` |
| Automation | CronJobs, scripts | Controller watches CRD |
| Reconciliation | Manual | Controller auto-reconciles |

## CRD Definition

```yaml
# save as myapp-crd.yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: webapps.stable.example.com
spec:
  group: stable.example.com
  versions:
  - name: v1
    served: true
    storage: true
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              image:
                type: string
              replicas:
                type: integer
                minimum: 1
              domain:
                type: string
              resources:
                type: object
                properties:
                  cpu:
                    type: string
                  memory:
                    type: string
            required:
            - image
  scope: Namespaced
  names:
    plural: webapps
    singular: webapp
    kind: WebApp
    shortNames:
    - wa
```

## Custom Resource (instance)

```yaml
# save as myapp-instance.yaml
apiVersion: stable.example.com/v1
kind: WebApp
metadata:
  name: my-blog
  namespace: default
spec:
  image: nginx:1.25
  replicas: 3
  domain: blog.example.com
  resources:
    cpu: "500m"
    memory: "256Mi"
```

## Apply CRD + Instance

```bash
# Apply CRD first
kubectl apply -f myapp-crd.yaml

# Verify CRD is created
kubectl get crd webapps.stable.example.com
kubectl describe crd webapps.stable.example.com

# Apply instance
kubectl apply -f myapp-instance.yaml

# Use it like any K8s resource
kubectl get webapps
kubectl get wa                    # short name
kubectl describe webapp my-blog
kubectl get webapp my-blog -o yaml
kubectl delete webapp my-blog
```

## Status Subresource

```yaml
# CRD with status
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: webapps.stable.example.com
spec:
  group: stable.example.com
  versions:
  - name: v1
    served: true
    storage: true
    subresources:
      status: {}
    schema:
      openAPIV3Schema:
        type: object
        properties:
          spec:
            type: object
            properties:
              image:
                type: string
              replicas:
                type: integer
          status:
            type: object
            properties:
              phase:
                type: string
              message:
                type: string
              readyReplicas:
                type: integer
  scope: Namespaced
  names:
    plural: webapps
    singular: webapp
    kind: WebApp
```

## Update Status

```bash
# Update status (requires status subresource)
kubectl patch webapp my-blog --type=merge -p '{"status":{"phase":"Running","readyReplicas":3}}'

# Check status
kubectl get webapp my-blog -o jsonpath='{.status.phase}'
```

## Validation with OpenAPI

CRDs support OpenAPI v3 schema validation:

```yaml
schema:
  openAPIV3Schema:
    type: object
    properties:
      spec:
        type: object
        properties:
          replicas:
            type: integer
            minimum: 1
            maximum: 10
          image:
            type: string
            pattern: "^[a-z0-9.-]+:[0-9]+$"
    required:
    - spec
```

```bash
# This will fail validation
kubectl apply -f - <<EOF
apiVersion: stable.example.com/v1
kind: WebApp
metadata:
  name: invalid
spec:
  replicas: 0    # violates minimum: 1
  image: nginx   # violates pattern (missing :tag)
# Error: spec.replicas must be >= 1, spec.image must match pattern
```

## Conversion Webhooks (Multi-Version)

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: webapps.stable.example.com
spec:
  group: stable.example.com
  versions:
  - name: v1
    served: true
    storage: true
  - name: v2
    served: true
    storage: false
    # conversion webhook for v1 ↔ v2
```

## Best Practices

1. **Use status subresource** — separate spec from status
2. **Validate with OpenAPI** — enforce required fields, types, ranges
3. **Short names** — `kubectl get wa` is faster than `kubectl get webapps`
4. **Multi-version** — support v1 and v2 with conversion webhooks
5. **Documentation** — CRD description helps `kubectl explain`
6. **RBAC** — define roles for custom resources

## Related

- [Operators](./operators.md)
- [Advanced Patterns](./README.md)