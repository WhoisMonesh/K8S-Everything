# Production Readiness Checklist

> **Category:** Operations / Checklists
> Pre-deployment validation checklist for production Kubernetes clusters.

## Overview

```mermaid
graph LR
    A[Planning] --> B[Infrastructure]
    B --> C[Security]
    C --> D[Networking]
    D --> E[Storage]
    E --> F[Monitoring]
    F --> G[Testing]
```

## Checklist Summary

| Category | Items | Status |
|----------|-------|--------|
| Planning | 8 | ☐ |
| Infrastructure | 10 | ☐ |
| Security | 12 | ☐ |
| Networking | 8 | ☐ |
| Storage | 6 | ☐ |
| Monitoring | 8 | ☐ |
| Testing | 6 | ☐ |
| **Total** | **58** | |

## 1. Planning

| # | Item | Check |
|---|------|-------|
| 1.1 | Capacity planning | ☐ Documented resource requirements |
| 1.2 | SLA definition | ☐ Uptime and performance targets defined |
| 1.3 | Budget approval | ☐ Infrastructure costs approved |
| 1.4 | Team readiness | ☐ Team trained on K8s operations |
| 1.5 | Runbooks | ☐ Operational runbooks created |
| 1.6 | DR plan | ☐ Disaster recovery plan documented |
| 1.7 | Change management | ☐ Deployment process defined |
| 1.8 | Compliance | ☐ Regulatory requirements met |

## 2. Infrastructure

| # | Item | Check |
|---|------|-------|
| 2.1 | Cluster size | ☐ Sufficient nodes for workload |
| 2.2 | Node types | ☐ Right instance types for workloads |
| 2.3 | Auto-scaling | ☐ Cluster autoscaler configured |
| 2.4 | HA control plane | ☐ Multi-master setup |
| 2.5 | etcd backup | ☐ Automated backups configured |
| 2.6 | Node taints | ☐ System nodes tainted |
| 2.7 | Resource quotas | ☐ Namespace quotas set |
| 2.8 | Limit ranges | ☐ Default limits configured |
| 2.9 | Pod Disruption Budgets | ☐ PDBs for critical workloads |
| 2.10 | Node selectors | ☐ Workload placement configured |

## 3. Security

| # | Item | Check |
|---|------|-------|
| 3.1 | RBAC | ☐ Roles and bindings configured |
| 3.2 | Service accounts | ☐ Dedicated service accounts |
| 3.3 | Network policies | ☐ Default deny policies |
| 3.4 | Pod security | ☐ PSA labels applied |
| 3.5 | Secrets encryption | ☐ Encryption at rest enabled |
| 3.6 | TLS certificates | ☐ Valid certificates for all services |
| 3.7 | Image scanning | ☐ Vulnerability scanning enabled |
| 3.8 | Admission control | ☐ OPA/Kyverno policies |
| 3.9 | Audit logging | ☐ Audit logs enabled |
| 3.10 | Secrets management | ☐ External secrets configured |
| 3.11 | Container security | ☐ Non-root containers |
| 3.12 | CIS benchmarks | ☐ CIS compliance verified |

## 4. Networking

| # | Item | Check |
|---|------|-------|
| 4.1 | CNI | ☐ CNI plugin installed and configured |
| 4.2 | DNS | ☐ CoreDNS working |
| 4.3 | Ingress | ☐ Ingress controller installed |
| 4.4 | TLS termination | ☐ TLS configured at ingress |
| 4.5 | Network policies | ☐ Default deny in place |
| 4.6 | Service mesh | ☐ Mesh configured (if needed) |
| 4.7 | Load balancing | ☐ External load balancer configured |
| 4.8 | DNS resolution | ☐ Internal DNS working |

## 5. Storage

| # | Item | Check |
|---|------|-------|
| 5.1 | Storage class | ☐ Storage classes defined |
| 5.2 | Dynamic provisioning | ☐ PVs auto-provisioned |
| 5.3 | Backup strategy | ☐ PV backups configured |
| 5.4 | Snapshot policy | ☐ Volume snapshots scheduled |
| 5.5 | Storage monitoring | ☐ Storage metrics collected |
| 5.6 | Capacity alerts | ☐ Storage capacity alerts |

## 6. Monitoring

| # | Item | Check |
|---|------|-------|
| 6.1 | Metrics collection | ☐ Prometheus scraping metrics |
| 6.2 | Dashboard | ☐ Grafana dashboards configured |
| 6.3 | Alerting | ☐ Alertmanager configured |
| 6.4 | Log aggregation | ☐ Centralized logging |
| 6.5 | Distributed tracing | ☐ Tracing configured (if needed) |
| 6.6 | Uptime monitoring | ☐ External uptime checks |
| 6.7 | SLO monitoring | ☐ SLO dashboards and alerts |
| 6.8 | Cost monitoring | ☐ Cost allocation tags |

## 7. Testing

| # | Item | Check |
|---|------|-------|
| 7.1 | Smoke tests | ☐ Basic functionality tests |
| 7.2 | Load testing | ☐ Performance benchmarks |
| 7.3 | Chaos testing | ☐ Chaos engineering tests |
| 7.4 | DR testing | ☐ Disaster recovery tested |
| 7.5 | Security testing | ☐ Penetration testing |
| 7.6 | Regression testing | ☐ Regression test suite |

## Quick Validation Commands

```bash
# Check cluster health
kubectl get nodes
kubectl get pods -A --field-selector=status.phase!=Running

# Check system pods
kubectl get pods -n kube-system

# Check resource usage
kubectl top nodes
kubectl top pods -A

# Check DNS
kubectl run test --image=busybox --rm -it -- nslookup kubernetes.default

# Check storage
kubectl get pv,pvc
kubectl get storageclasses

# Check networking
kubectl get svc -A
kubectl get ingress -A

# Check security
kubectl get networkpolicies -A
kubectl get pods -A -o json | jq '.items[] | select(.spec.containers[].securityContext.privileged == true)'

# Check monitoring
kubectl get pods -n monitoring
kubectl get prometheus -A
```

## Pre-Deployment Checklist

```bash
# Run before deploying to production

echo "=== Pre-Deployment Checklist ==="

# 1. Check cluster health
echo "1. Cluster health:"
kubectl get nodes | grep -v "NotReady"

# 2. Check resource availability
echo "2. Resource availability:"
kubectl describe nodes | grep -A 5 "Allocated resources"

# 3. Check system pods
echo "3. System pods:"
kubectl get pods -n kube-system | grep -v Running

# 4. Check PDBs
echo "4. Pod Disruption Budgets:"
kubectl get pdb -A

# 5. Check quotas
echo "5. Resource Quotas:"
kubectl get resourcequotas -A

# 6. Check network policies
echo "6. Network Policies:"
kubectl get networkpolicies -A

# 7. Check storage
echo "7. Storage:"
kubectl get pv,pvc

# 8. Check certificates
echo "8. Certificates:"
kubectl get certificates -A

echo "=== Checklist Complete ==="
```

## Post-Deployment Checklist

```bash
# Run after deploying to production

echo "=== Post-Deployment Checklist ==="

# 1. Verify deployment
echo "1. Deployment status:"
kubectl get deployment <deployment-name> -n <namespace>

# 2. Check pods
echo "2. Pod status:"
kubectl get pods -n <namespace> -l app=<app-name>

# 3. Check logs
echo "3. Pod logs:"
kubectl logs -n <namespace> -l app=<app-name> --tail=50

# 4. Check events
echo "4. Events:"
kubectl get events -n <namespace> --sort-by='.lastTimestamp' | tail -20

# 5. Check service
echo "5. Service status:"
kubectl get svc -n <namespace> <service-name>

# 6. Check ingress
echo "6. Ingress status:"
kubectl get ingress -n <namespace> <ingress-name>

# 7. Run smoke tests
echo "7. Smoke tests:"
kubectl run test --rm -it --image=busybox -- wget -qO- http://<service>/health

# 8. Check metrics
echo "8. Metrics:"
kubectl top pods -n <namespace> -l app=<app-name>

echo "=== Deployment Verified ==="
```

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Pods not scheduling | Insufficient resources | Scale up or optimize |
| Network policies blocking | Default deny too strict | Add allow rules |
| Storage not provisioning | StorageClass not set | Set default StorageClass |
| DNS not working | CoreDNS not ready | Restart CoreDNS |
| Metrics not collecting | Prometheus not scraping | Check scrape configs |

## Best Practices

| Category | Practice |
|----------|----------|
| Planning | Start small, scale as needed |
| Infrastructure | Use managed services when possible |
| Security | Apply defense in depth |
| Networking | Use network policies |
| Storage | Test backup and restore |
| Monitoring | Monitor everything |
| Testing | Automate tests |

## Related

- [Cluster Upgrade Playbook](cluster-upgrade-playbook.md)
- [Disaster Recovery Runbook](disaster-recovery-runbook.md)
- [Security Hardening Guide](../docs/security-hardening-guide.md)
- [Performance Tuning Guide](../docs/performance-tuning-guide.md)
