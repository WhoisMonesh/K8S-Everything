# k9s — Terminal UI for Kubernetes

> **Category:** Tools / Terminal UI

## What It Is

**k9s** is a terminal-based UI for Kubernetes that provides real-time cluster monitoring and management. It's the most popular K8s terminal UI and essential for troubleshooting.

## Why Use It

| Feature | kubectl | k9s |
|---------|---------|-----|
| Real-time updates | Manual refresh | Auto-refresh |
| Multi-resource view | One resource at a time | Scan all resources |
| Pod shell | `kubectl exec -it` | One keystroke |
| Log streaming | `kubectl logs -f` | Integrated viewer |
| Resource filtering | `kubectl get --field-selector` | Interactive filter |

## Install

```bash
# macOS
brew install derailed/k9s/k9s

# Linux
curl -sS https://webinstall.dev/k9s | bash

# Windows
choco install k9s

# Go install
go install github.com/derailed/k9s@latest
```

## Launch

```bash
# Default context
k9s

# Specific namespace
k9s -n production

# Specific context
k9s --context my-cluster

# Headless mode (log only)
k9s --headless
```

## Key Bindings

| Key | Action |
|-----|--------|
| `:` | Command mode (filter, namespace switch) |
| `/` | Filter resources |
| `0` | Show all namespaces |
| `ctrl-d` | Delete resource |
| `e` | Edit resource |
| `l` | View logs |
| `s` | Shell into Pod |
| `p` | Describe resource |
| `y` | YAML view |
| `j/k` | Navigate up/down |
| `Tab` | Switch views |
| `ctrl-a` | Show all containers in Pod |
| `q` | Quit |

## Commands

```
# Command mode
:pod                          # View pods
:svc                          # View services
:ns                           # View namespaces
:deploy                       # View deployments
:rs                           # View replicasets
:cm                           # View configmaps
:secrets                      # View secrets
:pv                           # View persistent volumes
:events                       # View events
:xray deploy <name>           # X-ray view (shows all related resources)
:trace deploy <name>          # Trace view
:pulse deploy <name>          # Pulse view (live status)
:summary deploy <name>        # Summary view
```

## Filtering

```
# Filter by name
:pod /nginx                   # Show pods containing "nginx"

# Filter by label
:pod -l app=nginx             # Show pods with label app=nginx

# Filter by namespace
:pod -n production            # Show pods in production namespace

# Combine filters
:pod /nginx -n production     # Show nginx pods in production
```

## Pod Operations

```
# Shell into Pod
s                             # Select Pod, press s

# View logs
l                             # Select Pod, press l

# View all container logs
ctrl-a                        # Switch to all containers, then l

# Delete Pod
ctrl-d                        # Select Pod, press ctrl-d

# Edit Pod
e                             # Select Pod, press e
```

## Configuration

```yaml
# ~/.k9s/config.yml
k9s:
  refreshRate: 2
  headless: false
  logoless: false
  writeBack: false
  readOnly: false
  noShell: false
  command: default
  threshold: 5
  ui:
    enableMouse: true
    headless: false
    logoless: false
    crumbsless: false
    noIcons: false
```

## Best Practices

1. **Use for troubleshooting** — k9s excels at quick resource inspection
2. **Combine with kubectl** — use k9s for browsing, kubectl for complex operations
3. **Set namespace** — use `k9s -n <ns>` to stay in a namespace
4. **Learn the filters** — `:` command mode is fastest for navigation
5. **Use xray** — `:xray deploy <name>` shows all related resources

## Related

- [kubectl Cheatsheet](../../cheat-sheets/kubectl.md)
- [stern](stern.md)
- [Troubleshooting](../../14-troubleshooting/troubleshooting-patterns.md)
