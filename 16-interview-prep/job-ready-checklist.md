# Kubernetes Job-Ready Checklist

> **Category:** Interview Prep / Career
> Checklist to become job-ready for Kubernetes roles.

## Core Skills

### Must Have

| Skill | Level | How to Learn |
|-------|-------|--------------|
| **K8s Architecture** | Expert | Docs, labs |
| **kubectl** | Expert | Daily usage |
| **Pod/Deployment/Service** | Expert | Hands-on |
| **Networking** | Advanced | CNI, Services, Ingress |
| **Storage** | Advanced | PV, PVC, StorageClass |
| **Security** | Advanced | RBAC, PSA, NetworkPolicy |
| **Troubleshooting** | Expert | Debugging exercises |

### Nice to Have

| Skill | Level | How to Learn |
|-------|-------|--------------|
| **Helm** | Intermediate | Chart development |
| **Service Mesh** | Intermediate | Istio/Linkerd labs |
| **GitOps** | Intermediate | ArgoCD/Flux |
| **Monitoring** | Intermediate | Prometheus/Grafana |
| **Logging** | Intermediate | ELK/Loki |

## Day 1 Readiness

### Setup Checklist

- [ ] kubectl installed and configured
- [ ] Access to a cluster (kind, minikube, or cloud)
- [ ] IDE configured (VS Code with Kubernetes extension)
- [ ] Terminal configured (kubectl autocomplete, aliases)
- [ ] Basic commands memorized

### Basic Commands

```bash
# Pod management
kubectl get pods -A
kubectl describe pod <pod>
kubectl logs <pod>
kubectl exec -it <pod> -- sh
kubectl delete pod <pod>

# Deployment management
kubectl get deployments
kubectl create deployment <name> --image=<image>
kubectl scale deployment <name> --replicas=3
kubectl rollout restart deployment <name>
kubectl rollout undo deployment <name>

# Service management
kubectl get svc
kubectl expose deployment <name> --port=80 --type=ClusterIP
kubectl port-forward <pod> 8080:80

# Debugging
kubectl get events --sort-by='.lastTimestamp'
kubectl top pods
kubectl top nodes
```

### Basic Concepts

| Concept | Understanding |
|---------|---------------|
| Pod | Smallest deployable unit |
| Deployment | Manages ReplicaSets |
| Service | Network endpoint for Pods |
| Namespace | Virtual cluster |
| ConfigMap | Non-sensitive config |
| Secret | Sensitive config |
| PV/PVC | Persistent storage |
| Node | Worker machine |
| Control Plane | API server, etcd, scheduler |

## Week 1-2 Tasks

### Hands-On Exercises

- [ ] Deploy a simple web app (nginx)
- [ ] Create a Service and access it
- [ ] Scale the deployment
- [ ] Update the image and rollback
- [ ] Use ConfigMaps and Secrets
- [ ] Mount a PersistentVolume
- [ ] Debug a CrashLoopBackOff pod
- [ ] Read logs from multiple pods

### Reading

- [ ] K8s official docs: Core Concepts
- [ ] K8s official docs: Tasks
- [ ] K8s official docs: Reference

## Week 3-4 Tasks

### Hands-On Exercises

- [ ] Create a multi-tier app (frontend + backend + database)
- [ ] Use StatefulSet for database
- [ ] Configure Ingress
- [ ] Apply NetworkPolicies
- [ ] Set up RBAC
- [ ] Use DaemonSets for logging
- [ ] Use Jobs for batch processing
- [ ] Monitor with Prometheus

### Reading

- [ ] K8s official docs: Networking
- [ ] K8s official docs: Storage
- [ ] K8s official docs: Security

## Month 2 Tasks

### Hands-On Exercises

- [ ] Set up a cluster from scratch (kubeadm or cloud)
- [ ] Configure CNI (Calico, Cilium)
- [ ] Set up Ingress Controller (NGINX, Traefik)
- [ ] Configure persistent storage (NFS, cloud)
- [ ] Set up monitoring stack (Prometheus + Grafana)
- [ ] Set up logging stack (ELK or Loki)
- [ ] Practice CKA/CKAD mock exams

### Reading

- [ ] K8s official docs: Cluster Administration
- [ ] K8s official docs: Concepts (deep dive)
- [ ] Kubernetes Up & Running (book)

## Month 3 Tasks

### Hands-On Exercises

- [ ] Deploy a production-grade application
- [ ] Implement CI/CD pipeline
- [ ] Set up GitOps with ArgoCD
- [ ] Implement service mesh (Istio or Linkerd)
- [ ] Practice disaster recovery
- [ ] Perform cluster upgrade
- [ ] Take CKA/CKAD/CKS exam

### Portfolio Projects

- [ ] Deploy a microservices application
- [ ] Set up a complete CI/CD pipeline
- [ ] Implement monitoring and alerting
- [ ] Document architecture and runbooks

## Job Application Prep

### Resume Checklist

- [ ] Kubernetes certification (CKA/CKAD/CKS)
- [ ] Hands-on projects documented
- [ ] GitHub repo with examples
- [ ] Blog posts or articles
- [ ] Contribution to open source (optional)

### Interview Preparation

- [ ] Practice common questions
- [ ] Prepare demo scenarios
- [ ] Review architecture diagrams
- [ ] Prepare troubleshooting stories
- [ ] Research target company's stack

## Daily Habits

| Habit | Time |
|-------|------|
| Read K8s docs | 30 min |
| Hands-on lab | 1 hour |
| Practice commands | 15 min |
| Review notes | 15 min |

## Resources

| Resource | Link |
|----------|------|
| K8s Official Docs | https://kubernetes.io/docs/ |
| K8s GitHub | https://github.com/kubernetes/kubernetes |
| Killer.sh | https://killer.sh/ |
| KodeKloud | https://kodekloud.com/ |
| Mumshad's Courses | https://www.udemy.com/user/mumshad-mannambeth/ |

## Related

- [CKA Certification](cka.md)
- [CKAD Certification](ckad.md)
- [CKS Certification](cks.md)
- [Interview Questions](interview-questions.md)
- [Exam Walkthrough](exam-walkthrough.md)
