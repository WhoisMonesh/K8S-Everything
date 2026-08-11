# Monitoring Examples

> Prometheus Operator and alerting patterns.

## Contents
- `app-service-monitor.yaml` — app exposing /metrics + Service + ServiceMonitor.
- `service-monitor.yaml` — a standalone ServiceMonitor for an existing Service.
- `prometheus-alert.yaml` — an SLO-style recording/alert rule.

## Usage

```bash
kubectl apply -R -f .          # deploy all in this directory
kubectl apply -f . --dry-run=client   # validate first
kubectl delete -R -f .            # remove
```
