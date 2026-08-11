# Advanced YAML Examples

> **Category:** Examples / Advanced Patterns
> Production-ready YAML examples for common patterns.

---

## 1. Multi-Container Pod (Sidecar)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-sidecar
  labels:
    app: myapp
spec:
  containers:
  # Main application container
  - name: app
    image: myapp:1.0
    ports:
    - containerPort: 8080
    resources:
      requests:
        cpu: 100m
        memory: 128Mi
      limits:
        cpu: 500m
        memory: 256Mi

  # Log shipping sidecar
  - name: logshipper
    image: fluentd:latest
    volumeMounts:
    - name: varlog
      mountPath: /var/log
    resources:
      requests:
        cpu: 50m
        memory: 64Mi

  volumes:
  - name: varlog
    emptyDir: {}
```

---

## 2. Init Container

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      initContainers:
      # Wait for database to be ready
      - name: wait-for-db
        image: busybox:1.36
        command: ['sh', '-c', 'until nc -z postgres-svc 5432; do echo waiting for db; sleep 2; done']

      # Run migrations
      - name: migrate
        image: myapp:1.0
        command: ['python', 'manage.py', 'migrate']

      containers:
      - name: app
        image: myapp:1.0
        ports:
        - containerPort: 8080
```

---

## 3. CronJob with Deadline

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: daily-backup
spec:
  schedule: "0 2 * * *"  # 2 AM daily
  concurrencyPolicy: Forbid
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 3
  jobTemplate:
    spec:
      activeDeadlineSeconds: 3600  # 1 hour timeout
      backoffLimit: 2
      template:
        spec:
          restartPolicy: Never
          containers:
          - name: backup
            image: backup-tool:1.0
            env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: db-secret
                  key: url
            resources:
              requests:
                cpu: 200m
                memory: 256Mi
              limits:
                cpu: "1"
                memory: 1Gi
```

---

## 4. StatefulSet with PVC

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres
  replicas: 3
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: "2"
            memory: 4Gi
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 10Gi
```

---

## 5. DaemonSet

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-exporter
  namespace: monitoring
  labels:
    app: node-exporter
spec:
  selector:
    matchLabels:
      app: node-exporter
  template:
    metadata:
      labels:
        app: node-exporter
    spec:
      hostNetwork: true
      hostPID: true
      containers:
      - name: node-exporter
        image: prom/node-exporter:latest
        ports:
        - containerPort: 9100
        resources:
          requests:
            cpu: 50m
            memory: 64Mi
          limits:
            cpu: 200m
            memory: 128Mi
```

---

## 6. Network Policy (Advanced)

```yaml
# Allow traffic only from specific namespaces
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-frontend
  namespace: backend
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: frontend
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
```

---

## 7. HPA with Custom Metrics

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app
  minReplicas: 3
  maxReplicas: 50
  metrics:
  # CPU-based scaling
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70

  # Custom metric: requests per second
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "100"

  # External metric: SQS queue depth
  - type: External
    external:
      metric:
        name: sqs_queue_length
        selector:
          matchLabels:
            queue: my-queue
      target:
        type: AverageValue
        averageValue: "30"
```

---

## 8. Priority Class + Preemption

```yaml
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata:
  name: system-critical
value: 1000000000
globalDefault: false
preemptionPolicy: PreemptLowerPriority
description: "System critical workloads"

---
# High-priority pod
apiVersion: v1
kind: Pod
metadata:
  name: critical-app
spec:
  priorityClassName: system-critical
  containers:
  - name: app
    image: critical-app:1.0
```

---

## 9. ConfigMap with Hot Reload

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
data:
  nginx.conf: |
    server {
      listen 80;
      location / {
        proxy_pass http://backend:8080;
      }
    }

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
      annotations:
        checksum/config: "{{ sha256sum of ConfigMap }}"  # Triggers rolling update
    spec:
      containers:
      - name: nginx
        image: nginx:1.25
        volumeMounts:
        - name: config
          mountPath: /etc/nginx/conf.d
      volumes:
      - name: config
        configMap:
          name: nginx-config
```

---

## 10. Resource Quota per Namespace

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: team-quota
  namespace: team-a
spec:
  hard:
    # Compute
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi

    # Storage
    persistentvolumeclaims: "10"
    requests.storage: 100Gi

    # Object count
    pods: "50"
    services: "20"
    secrets: "50"
    configmaps: "50"

---
apiVersion: v1
kind: LimitRange
metadata:
  name: team-limits
  namespace: team-a
spec:
  limits:
  - type: Container
    default:
      cpu: 500m
      memory: 256Mi
    defaultRequest:
      cpu: 100m
      memory: 128Mi
    max:
      cpu: "4"
      memory: 8Gi
    min:
      cpu: 50m
      memory: 64Mi
```

## Related

- [Common Patterns](../examples/common-patterns/)
- [Learning Path](../docs/learning-path.md)
- [Glossary](../cheat-sheets/glossary.md)
