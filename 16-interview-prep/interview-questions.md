# Kubernetes Interview Questions

> **Category:** Interview Prep
> Common Kubernetes interview questions with answers.

## Core Concepts

| # | Question | Answer |
|---|----------|--------|
| 1 | What is a Pod? | Smallest deployable unit; one or more containers sharing network/Storage. |
| 2 | What is a Service? | Stable network endpoint (ClusterIP, NodePort, LoadBalancer) mapping to Pods. |
| 3 | What is a Deployment? | Manages ReplicaSets; declarative updates, rollbacks, scaling. |
| 4 | What is a Namespace? | Virtual cluster within physical cluster; isolates resources. |
| 5 | What is a ConfigMap? | Stores non-sensitive config data as key-value pairs. |
| 6 | What is a Secret? | Stores sensitive data (passwords, tokens) encoded in base64. |
| 7 | What is a PV/PVC? | PersistentVolume (cluster storage) and PersistentVolumeClaim (request for storage). |
| 8 | What is a DaemonSet? | Ensures one Pod runs on every (or selected) node. |
| 9 | What is a StatefulSet? | For stateful workloads; stable network identity, persistent storage. |
| 10 | What is a Job? | Runs Pods to completion (batch processing). |

## Architecture

| # | Question | Answer |
|---|----------|--------|
| 11 | What is the control plane? | API server, etcd, scheduler, controller-manager. |
| 12 | What is etcd? | Distributed key-value store; single source of truth for cluster state. |
| 13 | What does kubelet do? | Agent on each node; manages Pods and containers. |
| 14 | What does kube-proxy do? | Maintains network rules for Services (iptables/IPVS). |
| 15 | What is CNI? | Container Network Interface; plugin standard for pod networking. |
| 16 | What is CSI? | Container Storage Interface; plugin standard for storage. |
| 17 | What is the API server? | Front-end for control plane; validates and processes REST calls. |
| 18 | What is the scheduler? | Assigns Pods to nodes based on constraints and resources. |
| 19 | What is a controller? | Control loop; watches state, makes changes to reach desired state. |
| 20 | What is a CRD? | Custom Resource Definition; extends K8s API with custom resources. |

## Networking

| # | Question | Answer |
|---|----------|--------|
| 21 | What are the 4 types of Services? | ClusterIP, NodePort, LoadBalancer, ExternalName. |
| 22 | What is ClusterIP? | Internal virtual IP; only accessible within cluster. |
| 23 | What is NodePort? | Exposes service on each node's IP at a static port (30000-32767). |
| 24 | What is LoadBalancer? | Provisions external load balancer (cloud provider). |
| 25 | What is Ingress? | HTTP/HTTPS routing rules via Ingress Controller. |
| 26 | What is CoreDNS? | DNS server for service discovery. |
| 27 | What is a NetworkPolicy? | Firewall rules for pod-to-pod traffic. |
| 28 | How does service discovery work? | DNS: `<service>.<namespace>.svc.cluster.local`. |
| 29 | What is EndpointSlice? | Scalable endpoint tracking (replaces Endpoints). |
| 30 | What is the difference between Ingress and Gateway API? | Gateway API is next-gen; supports TCP/UDP, weighted routing. |

## Scheduling & Autoscaling

| # | Question | Answer |
|---|----------|--------|
| 31 | What are taints and tolerations? | Taints repel Pods; tolerations allow Pods on tainted nodes. |
| 32 | What is node affinity? | Rules that attract Pods to specific nodes. |
| 33 | What is pod affinity? | Rules that co-locate Pods on same node/zone. |
| 34 | What is HPA? | Horizontal Pod Autoscaler; scales pod count based on metrics. |
| 35 | What is VPA? | Vertical Pod Autoscaler; right-sizes resource requests. |
| 36 | What is Cluster Autoscaler? | Adds/removes nodes based on pending pods or utilization. |
| 37 | What is KEDA? | Kubernetes Event-Driven Autoscaling; scales based on external events. |
| 38 | What are resource requests? | Guaranteed resources reserved for a container. |
| 39 | What are resource limits? | Maximum resources a container can use. |
| 40 | What is a PriorityClass? | Defines priority for pod scheduling and preemption. |

## Security

| # | Question | Answer |
|---|----------|--------|
| 41 | What is RBAC? | Role-Based Access Control; controls who can do what. |
| 42 | What is a ServiceAccount? | Identity for workloads (Pods) to authenticate to API. |
| 43 | What is Pod Security Admission? | Admission controller enforcing Pod Security Standards. |
| 44 | What are the 3 Pod Security Standards? | Privileged, Baseline, Restricted. |
| 45 | What is an admission controller? | Intercepts requests to API server for validation/mutation. |
| 46 | What is OPA Gatekeeper? | Policy engine for Kubernetes admission control. |
| 47 | What is Kyverno? | Kubernetes-native policy engine. |
| 48 | What is network segmentation? | Isolating network traffic using NetworkPolicies. |
| 49 | How do you encrypt secrets at rest? | Enable KMS provider or use etcd encryption config. |
| 50 | What is mTLS? | Mutual TLS; both client and server authenticate via certificates. |

## Storage

| # | Question | Answer |
|---|----------|--------|
| 51 | What is a PersistentVolume? | Cluster storage resource (NFS, iSCSI, cloud disk). |
| 52 | What is a PersistentVolumeClaim? | Request for storage by a user/Pod. |
| 53 | What is dynamic provisioning? | Automatic PV creation when PVC is created. |
| 54 | What is a StorageClass? | Defines type of storage (SSD, HDD, etc.). |
| 55 | What is a volume snapshot? | Point-in-time copy of a PersistentVolume. |
| 56 | What is CSI? | Container Storage Interface; plugin for storage drivers. |
| 57 | What is ReadWriteOnce? | Volume can be mounted by one node read-write. |
| 58 | What is ReadOnlyMany? | Volume can be mounted by many nodes read-only. |
| 59 | What is ReadWriteMany? | Volume can be mounted by many nodes read-write. |
| 60 | What is reclaim policy? | What happens to PV when PVC is deleted (Retain, Delete, Recycle). |

## Operations

| # | Question | Answer |
|---|----------|--------|
| 61 | How do you backup etcd? | `etcdctl snapshot save` with certs. |
| 62 | How do you upgrade a cluster? | Control plane first, then worker nodes (drain → upgrade → uncordon). |
| 63 | What is a Pod Disruption Budget? | Limits voluntary disruptions during maintenance. |
| 64 | How do you debug a CrashLoopBackOff pod? | `kubectl logs --previous`, check events, exec into pod. |
| 65 | How do you scale a deployment? | `kubectl scale deployment <name> --replicas=N`. |
| 66 | How do you rollback a deployment? | `kubectl rollout undo deployment <name>`. |
| 67 | How do you check resource usage? | `kubectl top nodes`, `kubectl top pods`. |
| 68 | How do you get pod logs? | `kubectl logs <pod>`, `kubectl logs -f <pod>` (follow). |
| 69 | How do you exec into a pod? | `kubectl exec -it <pod> -- sh`. |
| 70 | How do you port-forward? | `kubectl port-forward <pod> 8080:80`. |

## Service Mesh & Advanced

| # | Question | Answer |
|---|----------|--------|
| 71 | What is a service mesh? | Layer-7 network (Istio, Linkerd); mTLS, traffic management. |
| 72 | What is a sidecar? | Helper container in a pod (e.g., Envoy proxy). |
| 73 | What is Istio? | Most popular service mesh; Istiod control plane + Envoy data plane. |
| 74 | What is VirtualService? | Istio CRD for traffic routing rules. |
| 75 | What is DestinationRule? | Istio CRD for load balancing, circuit breaking. |
| 76 | What is Gateway API? | Next-gen Ingress (K8s SIG); supports TCP/UDP, weighted routing. |
| 77 | What is Cilium? | eBPF-based networking, security, and observability. |
| 78 | What is GitOps? | Declarative infrastructure managed via Git (ArgoCD, Flux). |
| 79 | What is Helm? | Package manager for Kubernetes (charts, releases). |
| 80 | What is Kustomize? | Template-free way to customize K8s resources. |

## Scenario-Based

| # | Question | Answer |
|---|----------|--------|
| 81 | Pod stuck in Pending? | Check events: resource quota, node selectors, PVC binding. |
| 82 | Pod in CrashLoopBackOff? | Check logs, command args, config mounts, image. |
| 83 | Service not reachable? | Check endpoints, selector labels, network policy, DNS. |
| 84 | Node not ready? | Check kubelet, disk pressure, memory pressure, network. |
| 85 | etcd slow? | Check disk I/O, network latency, compact history. |
| 86 | How to handle secrets in Git? | Use Sealed Secrets, External Secrets, or SOPS. |
| 87 | How to do zero-downtime deploy? | Rolling update + PDB + readiness probe + preStop hook. |
| 88 | How to handle stateful apps? | Use StatefulSet + PVC + headless Service. |
| 89 | How to secure cluster? | RBAC + NetworkPolicy + PSA + mTLS + audit logging. |
| 90 | How to monitor cluster? | Prometheus + Grafana + alerting rules. |

## Related

- [CKA Certification](cka.md)
- [CKAD Certification](ckad.md)
- [CKS Certification](cks.md)
- [Exam Walkthrough](exam-walkthrough.md)
