# YAML Cheatsheet

> Kubernetes YAML reference — the essential fields you need to know.

## YAML Basics

```yaml
# Comments start with #
# key: value (string)
# number: 42 (integer)
# flag: true (boolean)
# list: (array)
#   - item1
#   - item2
# object: (nested map)
#   key: value
```

## Pod Manifest (Minimal)

```yaml
apiVersion: v1          # Required - API version
kind: Pod               # Required - Resource type
metadata:               # Required - Object metadata
  name: my-pod          #   Name must be DNS-1123 compliant
  labels:               #   Labels for selection
    app: MyApp
spec:                   # Required - Pod spec
  containers:           # Required - List of containers
  - name: my-container  #   Required - Container name
    image: nginx:1.25   #   Required - Image reference
    ports:              #   Optional - Ports to expose
    - containerPort: 80 #     Required - Container port
```

## Deployment Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deploy
  labels:
    app: nginx
spec:
  replicas: 3                    # Number of pods
  selector:                      # How to find pods for this deploy
    matchLabels:
      app: nginx
  strategy:                      # Deployment strategy
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: nginx
  template:                     # Pod template
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.25
        ports:
        - containerPort: 80
        resources:               # Resource requests & limits
          requests:
            cpu: "100m"         # 100 milliCPU = 0.1 CPU
            memory: "128Mi"     # 128 Mebibytes
          limits:
            cpu: "250m"
            memory: "256Mi"
```

## Service Manifest

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:                     # Which pods to route to
    app: nginx
  ports:                        # Port mappings
  - name: http                  #   Port name (optional)
    port: 80                    #   Service port
    targetPort: 80              #   Pod container port
    protocol: TCP               # Protocol (TCP/UDP/SCTP)
  type: ClusterIP               # Service type (see below)
```

## Service Types

```yaml
# type: ClusterIP (default) - internal only
type: ClusterIP

# type: NodePort - exposed on each node IP
type: NodePort
# Adds nodePort: <30000-32767>

# type: LoadBalancer - cloud load balancer
type: LoadBalancer
loadBalancerIP: 203.0.113.1

# type: ExternalName - CNAME record
type: ExternalName
externalName: my.service.local
```

## Ingress Manifest

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: main-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx       # Which controller to use
  tls:                          # TLS secrets
  - hosts:
    - example.com
    secretName: tls-secret
  rules:                        # Routing rules
  - host: example.com
    http:
      paths:
      - path: /api
        pathType: Prefix        # Exact | Prefix | ImplementationSpecific
        backend:
          service:
            name: api-service
            port:
              number: 80
```

## ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:                              # Plain text data
  LOG_LEVEL: "info"
  TIMEOUT: "30"
  DATABASE_URL: "postgres://..."
binaryData:                        # Binary data (base64)
  logo: <base64-encoded>
```

## Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque                       # Secret type
data:                              # Base64 encoded data
  username: YWRtaW4=
  password: c2VjcmV0
# OR use stringData for automatic base64 encoding
stringData:
  username: admin
  password: secret
```

## ConfigMap & Secret in Pods

```yaml
spec:
  containers:
  - name: app
    envFrom:                     # Import all keys as env vars
    - configMapRef:
        name: app-config
    - secretRef:
        name: app-secrets
    env:
    - name: DB_PASSWORD            # Single key as env var
      valueFrom:
        secretKeyRef:
          name: app-secrets
          key: password
    volumeMounts:                # Mount as files
    - name: config-volume
      mountPath: /etc/config
  volumes:
  - name: config-volume
    configMap:
      name: app-config
  - name: secret-volume
    secret:
      secretName: app-secrets
```

## Namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    environment: production
    team: backend
```

## PersistentVolumeClaim

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  accessModes:                   # Access mode (see below)
    - ReadWriteOnce
  storageClassName: "fast-ssd"   # StorageClass name
  resources:
    requests:
      storage: 10Gi             # Size of storage
  volumeMode: Filesystem         # Filesystem | Block
```

## Storage Access Modes

```yaml
accessModes:
# RWO - ReadWriteOnce:   Read/Write on exactly 1 node
# ROX - ReadOnlyMany:    Read-only from many nodes
# RWX - ReadWriteMany:   Read/Write from many nodes
# RWOP - ReadWriteOncePod: Read/Write on exactly 1 pod (K8s 1.22+)
```

## Volume Types

```yaml
spec:
  containers:
  - name: app
    volumeMounts:
    - name: data
      mountPath: /data
  volumes:
  - name: data
    emptyDir: {}                  # Empty directory (ephemeral)
  - name: data
    hostPath:                    # Host node filesystem
      path: /var/data
      type: DirectoryOrCreate
  - name: data
    persistentVolumeClaim:       # Reference existing PVC
      claimName: my-pvc
  - name: data
    configMap:                  # ConfigMap as files
      name: my-config
  - name: data
    secret:                     # Secret as files
      secretName: my-secret
  - name: data
    nfs:                        # NFS mount
      server: nfs-server
      path: /shared
```

## Resource Requirements

```yaml
resources:
  requests:                      # Minimum guaranteed
    cpu: "100m"                  # 0.1 CPU core
    memory: "128Mi"              # 128 MiB
  limits:                        # Maximum allowed
    cpu: "250m"
    memory: "256Mi"
    ephemeral-storage: "1Gi"     # Disk space for container
```

## Health Probes

```yaml
livenessProbe:                   # Restart container if fails
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
readinessProbe:                  # Remove from Service if fails
  exec:
    command: ["/bin/check"]
  initialDelaySeconds: 5
  periodSeconds: 5
startupProbe:                    # Wait for app to start
  tcpSocket:
    port: 8080
  failureThreshold: 30
  periodSeconds: 10
```

## Init Containers

```yaml
spec:
  initContainers:                # Run before main containers
  - name: wait-for-db
    image: busybox
    command: ['sh', '-c', 'until nslookup database; do echo waiting; sleep 2; done']
  containers:
  - name: app
    image: myapp
```

## Node Affinity

```yaml
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: kubernetes.io/arch
            operator: In
            values: ["arm64"]
          - key: kubernetes.io/os
            operator: In
            values: ["linux"]
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 1
        preference:
          matchExpressions:
          - key: topology.kubernetes.io/zone
            operator: In
            values: ["us-east-1a"]
```

## Tolerations

```yaml
spec:
  tolerations:
  - key: "dedicated"
    operator: "Equal"
    value: "gpu"
    effect: "NoSchedule"
  - key: "node.kubernetes.io/unschedulable"
    operator: "Exists"
    effect: "NoSchedule"
    tolerationSeconds: 300        # Grace period
```

## PriorityClass

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: high-priority
value: 1000000                  # Higher = more important
globalDefault: false              # True = default for pods without PC
description: "High priority for critical services"
---
spec:
  priorityClassName: high-priority
  containers:
  - name: app
    image: myapp
```

## Pod Disruption Budget

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: my-pdb
spec:
  minAvailable: 1                 # Minimum pods that must be available
  # OR
  maxUnavailable: 1               # Maximum pods that can be unavailable
  selector:
    matchLabels:
      app: myapp
```

---

## Related Resources

- [Common Patterns](../examples/common-patterns/README.md)
- [kubectl Cheatsheet](kubectl.md)
- [CKA Exam Cheatsheet](cert-cheatsheet.md)
