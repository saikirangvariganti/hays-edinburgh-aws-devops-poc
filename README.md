# Hays Edinburgh AWS DevOps POC

**GitHub:** https://github.com/saikirangvariganti/hays-edinburgh-aws-devops-poc

A production-grade AWS DevOps platform demonstrating Terraform IaC, EKS, CI/CD pipelines, IAM least-privilege, KMS encryption, and CloudWatch/Prometheus/Grafana observability — built for the Hays Edinburgh AWS DevOps Engineer role.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        AWS eu-west-2                            │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    VPC (10.0.0.0/16)                     │   │
│  │                                                          │   │
│  │  Public Subnets (3 AZs)    Private Subnets (3 AZs)       │   │
│  │  ┌──────────────┐          ┌────────────────────────┐   │   │
│  │  │  NAT Gateway │          │    EKS Node Group      │   │   │
│  │  │  ALB / WAF   │          │    (t3.medium x3)      │   │   │
│  │  └──────────────┘          │                        │   │   │
│  │                            │  Helm Deployments:     │   │   │
│  │                            │  • hays-devops-app     │   │   │
│  │                            │  • prometheus          │   │   │
│  │                            │  • grafana             │   │   │
│  │                            │  • jenkins             │   │   │
│  │                            └────────────────────────┘   │   │
│  │                                                          │   │
│  │  ┌──────────────┐          ┌────────────────────────┐   │   │
│  │  │  RDS Multi-AZ│          │    S3 Buckets          │   │   │
│  │  │  PostgreSQL  │          │    (KMS encrypted)     │   │   │
│  │  │  (KMS CMK)   │          │    • artifacts         │   │   │
│  │  └──────────────┘          │    • backups           │   │   │
│  │                            └────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  KMS CMKs: EKS secrets | RDS storage | S3 buckets              │
│  CloudWatch: Container Insights | Logs | Alarms | Dashboards    │
│  IAM: Least-privilege roles | IRSA | OIDC federation            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Repository Structure

```
hays-edinburgh-aws-devops-poc/
├── terraform/              Terraform IaC
│   ├── main.tf             Root module (provider, backend, module calls)
│   ├── outputs.tf          Root outputs
│   └── modules/
│       ├── vpc/            VPC, subnets, IGW, NAT, route tables, SGs
│       ├── eks/            EKS cluster, node group, addons
│       ├── rds/            RDS PostgreSQL Multi-AZ instance
│       ├── s3/             S3 buckets with versioning + lifecycle
│       ├── iam/            IAM roles for EKS, nodes, CI/CD (OIDC)
│       └── kms/            KMS CMKs for EKS, RDS, S3
├── k8s/                    Raw Kubernetes manifests
│   ├── deployment.yaml     App Deployment with security contexts
│   ├── service.yaml        ClusterIP Service
│   ├── ingress.yaml        ALB Ingress with TLS + WAF
│   └── hpa.yaml            HorizontalPodAutoscaler (CPU + memory)
├── helm/                   Helm charts
│   └── app-chart/          Application Helm chart
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
├── jenkins/
│   └── Jenkinsfile         Multi-stage Jenkins pipeline
├── .github/workflows/
│   └── ci-cd.yml           GitHub Actions CI/CD (OIDC + EKS deploy)
├── monitoring/
│   ├── cloudwatch_dashboard.json   CloudWatch dashboard definition
│   ├── prometheus.yml              Prometheus scrape configuration
│   └── grafana_dashboard.json      Grafana dashboard panels
├── migration/
│   ├── assessment_script.py        On-prem to AWS migration assessment
│   └── wave_plan.md                Phased migration wave plan
├── scripts/
│   ├── iam_audit.sh                IAM security audit script
│   └── kms_setup.sh                KMS CMK provisioning script
├── app/
│   ├── main.py                     Python application (health/metrics endpoints)
│   ├── Dockerfile                  Multi-stage Docker build
│   └── requirements.txt
├── tests/
│   └── test_poc.py                 85+ pytest tests (no live AWS calls)
└── README.md
```

---

## Key Features

### Infrastructure as Code (Terraform)
- **VPC**: Multi-AZ VPC with public/private subnets, NAT gateways, and security groups
- **EKS**: Managed Kubernetes cluster v1.28 with node auto-scaling, encrypted secrets (KMS), and CloudWatch logging
- **RDS**: PostgreSQL Multi-AZ with KMS encryption, automated backups, and Performance Insights
- **S3**: Versioned buckets with KMS SSE, public access blocking, and lifecycle policies
- **IAM**: Least-privilege roles for EKS cluster, worker nodes, and OIDC-federated CI/CD
- **KMS**: Customer-managed CMKs with automatic annual rotation for EKS, RDS, and S3

### CI/CD Pipelines
- **Jenkins**: Multi-stage Jenkinsfile (lint → test → build → scan → deploy)
- **GitHub Actions**: OIDC-authenticated pipeline with Trivy scanning, ECR push, and EKS Helm deploy

### Kubernetes
- Deployment with rolling update strategy, security contexts (non-root, read-only FS)
- HPA with CPU and memory-based scaling (min: 2, max: 20 replicas)
- ALB Ingress with TLS, WAF, and internal scheme

### Observability
- **CloudWatch**: Container Insights, custom dashboards, alarm definitions
- **Prometheus**: Kubernetes service discovery scrape configuration
- **Grafana**: EKS cluster overview dashboard (CPU, memory, latency, pod count)

### Migration
- `assessment_script.py`: Discovers workloads, recommends AWS instance types, estimates costs
- `wave_plan.md`: 5-wave migration plan (Foundation → Stateless → Data → Observability → Optimisation)

---

## Running the Tests

```bash
pip install pytest pyyaml
pytest tests/test_poc.py -v
```

---

## Terraform Usage

```bash
cd terraform
terraform init
terraform plan -var="account_id=123456789012" -var="db_password=SecurePassword123!"
terraform apply -var="account_id=123456789012" -var="db_password=SecurePassword123!"
```

---

## Deploying with Helm

```bash
# Update kubeconfig
aws eks update-kubeconfig --region eu-west-2 --name hays-devops-eks

# Deploy
helm upgrade --install hays-app helm/app-chart/ \
  --namespace production \
  --create-namespace \
  --set image.tag=1.0.0 \
  --wait
```

---

## Author

**Sai Kiran Goud Variganti**
GitHub: [saikirangvariganti](https://github.com/saikirangvariganti)
