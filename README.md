# kube-podname-dns

kube-podname-dns는 pod의 고유한 name으로 ip를 찾을 때 사용합니다.

DNS Protocol을 사용하여 일반적으로 DNS Query하듯이 사용 가능하며

kube-dns혹은 coredns와 연동하여 사용할 수 있습니다.

hbase의 경우 hostname으로 ip를 찾는데 kubernetes상에서 hbase를 운용할 때 유용하게 사용하실 수 있습니다.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: kube-podname-dns
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: kube-podname-dns-role
  namespace: kube-system
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
# This role binding allows "jane" to read pods in the "default" namespace.
kind: RoleBinding
metadata:
  name: kube-podname-dns-role
  namespace: kube-system
subjects:
- kind: ServiceAccount
  name: kube-podname-dns
  namespace: zeron-master
roleRef:
  kind: Role
  name: kube-podname-dns-role
  apiGroup: rbac.authorization.k8s.io
---
apiVersion: v1
kind: Secret
type: kubernetes.io/service-account-token
metadata:
  name: kube-podname-dns
  namespace: kube-system
  annotations:
    kubernetes.io/service-account.name: kube-podname-dns
---
kind: Deployment
apiVersion: apps/v1
metadata:
  name: kube-podname-dns
  namespace: kube-system
  labels:
    app: kube-podname-dns-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kube-podname-dns-app
  template:
    metadata:
      labels:
        app: kube-podname-dns-app
    spec:
      volumes:
      - name: secret-token
        secret:
          secretName: kube-podname-dns-token
      containers:
      - name: kube-podname-dns-container
        image: "docker.io/jclab/kube-podname-dns:1.0.0"
        volumeMounts:
        - name: secret-token
          readOnly: false
          mountPath: "/secret"
        ports:
        - containerPort: 53
---
kind: Service
apiVersion: v1
metadata:
  name: kube-podname-dns
  namespace: kube-system
  labels:
    app: kube-podname-dns-app
spec:
  selector:
    app: kube-podname-dns-app
  ports:
  - protocol: UDP
    port: 53
    targetPort: 53
  type: ClusterIP
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: kube-dns
  namespace: kube-system
data:
  stubDomains: |
    {"podname.cluster.local" : ["kube-podname-dns"]}
```
