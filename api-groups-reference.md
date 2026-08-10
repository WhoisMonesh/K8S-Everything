# Kubernetes API Groups Reference

> **Category:** Reference / Specification

## What It Is

The Kubernetes API is organized into groups. This reference lists all stable, beta, and alpha API groups, their resources, and common verbs.

## Why It Exists

The Kubernetes API surface is large and constantly evolving. API groups organize resources logically, and each group has its own versioning. This reference helps you:
- Understand API maturity levels
- Know which APIs are deprecated
- Look up resource names for `kubectl` commands
- Understand RBAC verb coverage

## API Group Maturity Levels

| Level | Stability | SLA | Notes |
|-------|-----------|-----|-------|
| GA (General Availability) | Stable | Guaranteed | `v1`, `v2`, etc. |
| Beta | Beta | Limited | `v1beta1`, `v1beta2` |
| Alpha | Experimental | No SLA | `v1alpha1`, `v1alpha2` |

## Discovering APIs

```bash
# List all API groups
kubectl api-versions

# List all API resources
kubectl api-resources

# Get details of a specific resource
kubectl api-resources --api-group=apps

# Show verb matrix (what actions are available on each resource)
kubectl api-resources -o wide
```

## Major API Groups

### 1. Core API Group (empty/`""`)

The most fundamental group. Also called the "legacy" or "core" group.

| Kind | Endpoint | Verbs | Description |
|------|----------|-------|-------------|
| Pod | `/api/v1/pods` | get, list, watch, create, update, patch, delete | Smallest deployable unit |
| Service | `/api/v1/services` | get, list, watch, create, update, patch, delete | Network abstraction |
| Namespace | `/api/v1/namespaces` | get, list, watch, create, update, patch, delete | Logical cluster partition |
| Node | `/api/v1/nodes` | get, list, watch, patch | Worker machine (no create/update) |
| Secret | `/api/v1/secrets` | get, list, watch, create, update, patch, delete | Sensitive data |
| ConfigMap | `/api/v1/configmaps` | get, list, watch, create, update, patch, delete | Configuration data |
| PersistentVolume | `/api/v1/persistentvolumes` | get, list, watch, create, update, patch, delete | Cluster storage |
| PersistentVolumeClaim | `/api/v1/persistentvolumeclaims` | get, list, watch, create, update, patch, delete | Storage request |
| ServiceAccount | `/api/v1/serviceaccounts` | get, list, watch, create, update, patch, delete | Identity for pods |
| Event | `/api/v1/events` | get, list, watch, create, patch | Audit trail |
| ResourceQuota | `/api/v1/resourcequotas` | get, list, watch, create, update, patch, delete | Quota limits |
| LimitRange | `/api/v1/limitranges` | get, list, watch, create, update, patch, delete | Default limits |

### 2. apps (Workload APIs)

| Kind | Endpoint | Verbs | Description |
|------|----------|-------|-------------|
| Deployment | `/apis/apps/v1/deployments` | get, list, watch, create, update, patch, delete | Declarative workload |
| ReplicaSet | `/apis/apps/v1/replicasets` | get, list, watch, create, update, patch, delete | Ensure pod replicas |
| StatefulSet | `/apis/apps/v1/statefulsets` | get, list, watch, create, update, patch, delete | Stateful workload |
| DaemonSet | `/apis/apps/v1/daemonsets` | get, list, watch, create, update, patch, delete | Run on all nodes |
| ReplicaSet | `/apis/apps/v1/replicasets` | get, list, watch, create, update, patch, delete | Replica management |

### 3. networking.k8s.io

| Kind | Endpoint | Verbs | Description |
|------|----------|-------|-------------|
| Ingress | `/apis/networking.k8s.io/v1/ingresses` | get, list, watch, create, update, patch, delete | HTTP routing |
| IngressClass | `/apis/networking.k8s.io/v1/ingressclasses` | get, list, watch, create, update, patch, delete | Ingress controller config |
| NetworkPolicy | `/apis/networking.k8s.io/v1/networkpolicies` | get, list, watch, create, update, patch, delete | Pod network isolation |
| GatewayClass | `/apis/networking.k8s.io/v1/gatewayclasses` | get, list, watch, create, update, patch, delete | Gateway controller |
| Gateway | `/apis/networking.k8s.io/v1/gateways` | get, list, watch, create, update, patch, delete | Service gateway |
| HTTPRoute | `/apis/networking.k8s.io/v1/httproutes` | get, list, watch, create, update, patch, delete | HTTP routing rule |
| GRPCRoute | `/apis/networking.k8s.io/v1/grpcroutes` | get, list, watch, create, update, patch, delete | gRPC routing |
| ServiceEntry | `/apis/networking.k8s.io/v1alpha1/serviceentries` | get, list, watch, create, update, patch, delete | Istio service discovery |

### 4. rbac.authorization.k8s.io

| Kind | Endpoint | Verbs | Description |
|------|----------|-------|-------------|
| Role | `/apis/rbac.authorization.k8s.io/v1/roles` | get, list, watch, create, update, patch, delete | Namespace-scoped permissions |
| RoleBinding | `/apis/rbac.authorization.k8s.io/v1/rolebindings` | get, list, watch, create, update, patch, delete | Bind roles |
| ClusterRole | `/apis/rbac.authorization.k8s.io/v1/clusterroles` | get, list, watch, create, update, patch, delete | Cluster-scoped permissions |
| ClusterRoleBinding | `/apis/rbac.authorization.k8s.io/v1/clusterrolebindings` | get, list, watch, create, update, patch, delete | Bind cluster roles |

### 5. batch

| Kind | Endpoint | Verbs | Description |
|------|----------|-------|-------------|
| Job | `/apis/batch/v1/jobs` | get, list, watch, create, update, patch, delete | Run to completion |
| CronJob | `/apis/batch/v1/cronjobs` | get, list, watch, create, update, patch, delete | Scheduled job |

### 6. autoscaling

| Kind | Endpoint | Verbs | Description |
|------|----------|-------|-------------|
| HorizontalPodAutoscaler | `/apis/autoscaling/v2/horizontalpodautoscalers` | get, list, watch, create, update, patch, delete, patch | Scale pods |
| VerticalPodAutoscaler | `/apis/autoscaling.k8s.io/v1/verticalpodautoscalers` | get, list, watch, create, update, patch, delete | Scale resources |
| PriorityClass | `/apis/scheduling.k8s.io/v1/priorityclasses` | get, list, watch, create, update, patch, delete | Pod priority |

### 7. policy

| Kind | Endpoint | Verbs | Description |
|------|----------|-------|-------------|
| PodDisruptionBudget | `/apis/policy/v1/poddisruptionbudgets` | get, list, watch, create, update, patch, delete, patch | Graceful disruption |
| PodSecurityPolicy | `/apis/policy/v1beta1/podsecuritypolicies` | ⚠️ Deprecated | Use PSA instead |

### 8. metrics.k8s.io

| Kind | Endpoint | Verbs | Description |
|------|----------|-------|-------------|
| PodMetrics | `/apis/metrics.k8s.io/v1/pods` | get, list, watch | CPU/memory per pod |
| NodeMetrics | `/apis/metrics.k8s.io/v1/nodes` | get, list, watch | CPU/memory per node |

### 9. keda.sh (KEDA)

| Kind | Endpoint | Verbs | Description |
|------|----------|-------|-------------|
| ScaledObject | `/apis/keda.sh/v1alpha1/scaledobjects` | get, list, watch, create, update, patch, delete | Event-driven scaling |
| TriggerAuthentication | `/apis/keda.sh/v1alpha1/triggerauthentications` | get, list, watch, create, update, patch, delete | Auth for scaler |
| ScaledJob | `/apis/keda.sh/v1alpha1/scaledjobs` | get, list, watch, create, update, patch, delete | Job scaling |

### 10. CustomResourceDefinition (apiextensions.k8s.io)

| Kind | Endpoint | Verbs | Description |
|------|----------|-------|-------------|
| CustomResourceDefinition | `/apis/apiextensions.k8s.io/v1/customresourcedefinitions` | get, list, watch, create, update, patch, delete | Define custom resources |
| APIService | `/apis/apiregistration.k8s.io/v1/apiservices` | get, list, watch, create, update, patch, delete | Aggregated API servers |

## Common kubectl Verbs

| Verb | CLI Command | Description |
|------|-------------|-------------|
| get | `kubectl get <resource>` | Display one or more resources |
| list | `kubectl get <resources>` | Same as get (plural) |
| watch | `kubectl get -w <resource>` | Watch changes |
| describe | `kubectl describe <resource>` | Detailed info |
| create | `kubectl create <resource>` | Create new resource |
| apply | `kubectl apply -f <file>` | Apply desired state |
| edit | `kubectl edit <resource>` | Edit resource in place |
| delete | `kubectl delete <resource>` | Remove resource |
| patch | `kubectl patch <resource>` | Partially update |
| replace | `kubectl replace -f` | Full replacement |
| expose | `kubectl expose` | Create service |
| exec | `kubectl exec` | Execute command |
| logs | `kubectl logs` | Print logs |
| port-forward | `kubectl port-forward` | Forward ports |
| proxy | `kubectl proxy` | Run proxy |
| label | `kubectl label` | Update labels |
| annotate | `kubectl annotate` | Update annotations |
| scale | `kubectl scale` | Set replicas |
| rollout | `kubectl rollout` | Manage rollout |
| config | `kubectl config` | Modify config |
| auth | `kubectl auth` | Inspect auth |

## Quick Reference

```bash
# Show all API resources with their verbs
kubectl api-resources -o wide

# Show OpenAPI schema for a resource type
kubectl explain pods.spec.containers --recursive

# Show which group/version a resource belongs to
kubectl api-resources --api-group=apps

# Show full API discovery
kubectl api-versions
```

---

## Related Resources

- [kubectl Cheatsheet](cheat-sheets/kubectl.md)
- [RBAC Documentation](06-security/rbac.md)
- [Kubernetes API Concepts](https://kubernetes.io/docs/reference/using-api/)
