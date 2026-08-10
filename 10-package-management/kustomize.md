# Kustomize

> **Category:** Package Management / GitOps

## What It Is

**Kustomize** customizes Kubernetes config through **overlays** — you keep a **base** set of manifests and layer **patch-based** changes on top, with no templating or scripting. Its CLI is native to `kubectl` (`kubectl apply -k`).

One repo of vanilla manifests, customized per environment (dev/staging/prod) by patching — no duplication, no templating engine.

## Why It Exists

- **Helm** uses templates (Jinja-like); **Kustomize** uses plain YAML overlays
- **Git-first** — overlays live in Git; `kubectl apply -k` is built into `kubectl`
- Works natively with GitOps tools (Argo CD, Flux)

## Directory Layout

```
my-app/
  base/
    deployment.yaml
    service.yaml
    kustomization.yaml       # Lists files + common labels
  overlays/
    dev/
      kustomization.yaml     # bases: ../../base  +  a patch
      replica-count.yaml
    prod/
      kustomization.yaml
      replica-count.yaml
```

Apply: `kubectl apply -k overlays/prod`

## kustomization.yaml

```yaml
# base/kustomization.yaml
apiVersion: k8s
kind: Kustomization
metadata:
  name: my-app-base
resources:
- deployment.yaml
- service.yaml
- configmap.yaml
commonLabels:
  app: my-app
commonAnnotations:
  example.com/owner: team-a
namespace: my-app
namePrefix: dev-
nameSuffix: -v2
configMapGenerator:
- name: app-config
  literals:
  - LOG_LEVEL=debug
  files:
  - config.json
  envs:
  - prod.env
secretGenerator:
- name: db-password
  literals:
  - password=s3cr3t
  type: Opaque
generatorOptions:
  disableNameSuffixHash: false
  annotations:
    managed-by: kustomize
```

### Overlay kustomization
```yaml
apiVersion: k8s
kind: Kustomization
namespace: my-app-dev
namePrefix: dev-
bases:
- ../../base
patches:
- target:
    kind: Deployment
    name: dev-my-app
  patch: |-
    spec:
      replicas: 1
configMapGenerator:
- name: app-config
  literals:
  - LOG_LEVEL=error     # Override one value on top of the base
```

## Patching

Two patch kinds:

### 1. Strategic Merge Patch (`patch:`)
```yaml
patches:
- target:
    kind: Deployment
    name: my-app
  patch: |-
    spec:
      replicas: 4
      template:
        spec:
          containers:
          - name: my-app
            resources:
              limits:
                memory: 512Mi
```

### 2. JSON Patch (`patch:` with `path`/`op`)
```yaml
patches:
- target:
    kind: Service
    name: my-service
  patch: |-
    - op: replace
      path: /spec/ports/0/port
      value: 8443
    - op: add
      path: /metadata/annotations/example-com~1version
      value: v2
```

## Generators

- `configMapGenerator`, `secretGenerator` — generate from literals, files, or envs. They get a suffix (`-5d558`) appended to the name.
- `generatorOptions` — set default behavior, or `disableNameSuffixHash: true` to stop the random hash.

## Transformers

- `commonLabels`, `commonAnnotations`, `namespace`, `namePrefix`, `nameSuffix` — applied to all resources.
- `images:` — change an image's repo/tag: `images: - name: nginx newTag: "1.25"`.

## Commands

```bash
# Render (no install)
kustomize build overlays/prod
kubectl kustomize build overlays/prod   # (kubectl 1.14+)

# Apply / diff / delete
kubectl apply -k overlays/prod
kubectl diff -k overlays/prod           # See the diff
kubectl delete -k overlays/prod

# Create a starter overlay
kustomize init
kustomize create --add-base ../../base
kustomize edit set replicas 3

# Install kustomize (if missing)
curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" | bash
```

## Common Issues

### "must have a name" / no namePrefix applied in patch
```yaml
# Patches match the FINAL name (after namePrefix/suffix is applied).
# If base has name: my-app and overlay sets namePrefix: dev-, the patch must target dev-my-app
patches:
- target:
    name: dev-my-app     # NOT my-app
```

### Generated ConfigMap/Secret name has a hash
```yaml
configMapGenerator:
- name: config
  env: prod.env
# Becomes: config-5d858t8d88 (hash appended)
# Use: refs in deployments must match — so use $(CONFIG_MAP_NAME) var, OR disableNameSuffixHash
generatorOptions:
  disableNameSuffixHash: true    # Use plain "config"
```

### `bases:` deprecated in favor of `resources:`
```yaml
# Old:
bases:
- ../../base
# New (Kustomize 4.0+, but bases still works):
resources:
- ../../base
```

### "no matches for kind" in a patch
```yaml
# The patch target Kind doesn't exist, or the base file is missing it.
# Check: does the base have that Kind? Is the apiVersion correct?
kubectl kustomize build overlays/prod | grep <kind>
```

### Namespace mismatch across overlays
```yaml
# Set namespace in the base OR each overlay consistently.
# If base sets namespace: prod and overlay sets namespace: dev, the last one wins.
```

## Kustomize vs Helm

| Feature | Kustomize | Helm |
|---------|-----------|------|
| Customization | YAML overlays / patches | Templates (Jinja-like) |
| State | None (stateless) | Stores release in a Secret |
| Git diff | Clean (only your patches) | Harder (rendered manifest) |
| Learning | YAML merge/patch only | Template syntax + functions |
| Best for | GitOps, stable bases, small per-env changes | Reusable packages, charts, versioned releases |

## Best Practices

1. **Base + overlays** for environments
2. **Set `namespace`** in the base (consistency)
3. **Use `kubectl diff -k`** before applying
4. **Pin images via `images:`** (not in the base YAML)
5. **Use `${ENV}`-style via vars** carefully — `var` is deprecated; prefer `configMapGenerator` + `envFrom`
6. **Avoid name collisions** with `namePrefix`/`suffix`
7. **Disable hash suffix** where you need a known name: `disableNameSuffixHash`
8. **Use `commonLabels`** to ensure your app labels are everywhere
9. **Test both `build` and `apply`** in a dry env
10. **Keep patches minimal** — diff-friendly

## Interview Questions

**Q: What is Kustomize and how does it work?**
A: A YAML customization tool — you keep a base set of manifests and write **overlay patches** (strategic or JSON 6902) that layer on environment-specific changes. `kubectl apply -k` renders + applies.

**Q: How is Kustomize different from Helm?**
A: Helm uses **templates** + stores a release. Kustomize uses **plain YAML patches** and is stateless — it just renders manifests. Kustomize is more Git-diff-friendly; Helm is more reusable/shareable.

**Q: Why might a patch not apply?**
A: (1) The target `name` must include the `namePrefix`, (2) the Kind must exist in the base, (3) field paths must be valid.

**Q: What is `namePrefix`?**
A: A string prepended to **all resource names** in a kustomization (e.g., `dev-` makes `my-app` → `dev-my-app`). Useful for scoping environments.

**Q: How does `kubectl diff` help?**
A: `kubectl diff -k overlays/prod` shows the live-vs-desired diff before you apply — a safe preview (no cluster changes).

## Related Resources

- [helm.md](helm.md)
- [helm-charts.md](helm-charts.md)
- [GitOps](../11-ci-cd-gitops/README.md)
