# stern — Multi-Pod Log Tailer

> **Category:** Tools / Logging

## What It Is

**stern** is a command-line tool for tailing multiple Kubernetes Pod logs simultaneously. It's the go-to tool for debugging distributed systems where you need to see logs from multiple Pods at once.

## Why Use It

| Feature | kubectl logs | stern |
|---------|--------------|-------|
| Multi-Pod | One Pod at a time | Regex-based multi-Pod |
| Multi-container | Manual container selection | All containers or filtered |
| Timestamp | Optional | Always included |
| Color coding | No | By Pod/container name |
| Regex filtering | No | Full regex support |

## Install

```bash
# macOS
brew install stern

# Linux
curl -Lo stern https://github.com/stern/stern/releases/download/v1.28.0/stern_linux_amd64
chmod +x stern && sudo mv stern /usr/local/bin/

# Go install
go install github.com/stern/stern@latest

# Windows
choco install stern
```

## Basic Usage

```bash
# Tail all Pods in a namespace
stern -n production

# Tail Pods matching regex
stern "nginx.*"

# Tail specific Pod
stern nginx-abc123

# Tail Pods with label selector
stern -l app=nginx

# Tail specific container in multi-container Pod
stern -c istio-proxy nginx-abc123
```

## Options

| Option | Description | Example |
|--------|-------------|---------|
| `-n, --namespace` | Namespace | `stern -n production` |
| `-l, --selector` | Label selector | `stern -l app=nginx` |
| `-c, --container` | Container name | `stern -c sidecar` |
| `-o, --output` | Output format | `stern -o json` |
| `-t, --timestamps` | Show timestamps | `stern -t` |
| `--since` | Time duration | `stern --since 10m` |
| `--tail` | Number of lines | `stern --tail 100` |
| `--include` | Include regex | `stern --include "ERROR"` |
| `--exclude` | Exclude regex | `stern --exclude "DEBUG"` |
| `-p, --pod` | Specific pod | `stern -p nginx-abc123` |
| `-f, --field-selector` | Field selector | `stern -f "status.phase=Running"` |
| `--context` | Kubeconfig context | `stern --context my-cluster` |

## Examples

```bash
# Tail all logs in namespace with timestamps
stern -n production -t

# Tail only error logs from nginx pods
stern "nginx.*" --include "ERROR|error|Error"

# Tail logs from last 5 minutes
stern "nginx.*" --since 5m

# Tail specific container in all pods
stern -c istio-proxy

# Tail logs with JSON output
stern "nginx.*" -o json

# Tail logs from specific node
stern -l "kubernetes.io/hostname=node-1"

# Tail only pods with phase Running
stern -f "status.phase=Running"

# Tail logs excluding debug messages
stern "nginx.*" --exclude "DEBUG|TRACE"

# Tail logs from a Deployment's pods
stern -l app=nginx,version=v1
```

## Output Formats

| Format | Description |
|--------|-------------|
| `default` | `[pod-name] log message` |
| `json` | JSON with pod, container, message, timestamp |
| `raw` | Raw log message only |

## Common Use Cases

```bash
# Debug connection issues
stern "api-gateway.*" --include "connection|timeout|refused"

# Monitor deployment rollout
stern -l app=myapp --since 2m

# Debug OOM kills
stern "myapp.*" --include "OOMKilled|killed|oom"

# Monitor certificate expiry
stern "cert-manager.*" --include "expir|renew"

# Debug DNS issues
stern -n kube-system coredns --include "dns|resolve"
```

## Best Practices

1. **Use regex wisely** — `stern "api.*"` matches api-gateway, api-server, etc.
2. **Combine with --include** — filter for specific patterns like errors
3. **Use --since** — avoid reading old logs during debugging
4. **Use label selectors** — more precise than regex for targeting
5. **Use -o json** — for piping to jq or other tools

## Related

- [Logging](../../13-observability/logging.md)
- [k9s](k9s.md)
- [Troubleshooting](../../14-troubleshooting/troubleshooting-patterns.md)
- [kubectl Cheatsheet](../../cheat-sheets/kubectl.md)
