# On-Premises to AWS Migration Wave Plan
## Hays Edinburgh AWS DevOps POC

**Target Region:** eu-west-2 (London)
**Estimated Total Duration:** 16 weeks
**Migration Strategy:** Lift-and-shift rehost + replatform to EKS/RDS

---

## Wave 1: Foundation (Weeks 1–2)

**Objective:** Establish core network and IAM infrastructure

### Tasks
- [ ] Create VPC with public/private subnets across 3 AZs
- [ ] Configure Internet Gateway and NAT Gateways
- [ ] Set up AWS Direct Connect or Site-to-Site VPN to on-prem
- [ ] Configure Route 53 private hosted zones
- [ ] Deploy baseline IAM roles and policies (least privilege)
- [ ] Configure AWS Organizations and SCPs
- [ ] Enable CloudTrail, Config, and Security Hub
- [ ] Deploy Terraform remote state backend (S3 + DynamoDB)

### AWS Services
- VPC, Subnets, IGW, NAT Gateway
- Direct Connect / VPN Gateway
- Route 53
- IAM, AWS Organizations, SCPs
- CloudTrail, AWS Config, Security Hub

### Success Criteria
- Network connectivity verified between on-prem and AWS
- All Terraform modules validate and plan successfully
- IAM baseline in place with no root account usage

---

## Wave 2: Stateless Applications (Weeks 3–6)

**Objective:** Containerize and deploy stateless workloads to EKS

### Tasks
- [ ] Deploy EKS cluster with managed node groups
- [ ] Configure EKS addons (CoreDNS, kube-proxy, VPC CNI)
- [ ] Set up ECR repositories
- [ ] Containerize web application servers using Docker
- [ ] Create Helm charts for all services
- [ ] Configure ALB Ingress Controller
- [ ] Set up WAF rules and ACLs
- [ ] Configure HPA for auto-scaling
- [ ] Deploy Jenkins CI/CD pipeline on EKS
- [ ] Set up GitHub Actions workflows

### AWS Services
- EKS, ECR, Helm
- ALB, WAF
- GitHub Actions, Jenkins (on EKS)

### Success Criteria
- All stateless apps running in EKS pods
- CI/CD pipelines deploying to EKS successfully
- Load balancer health checks passing
- HPA scaling verified under load testing

---

## Wave 3: Data Layer (Weeks 7–12)

**Objective:** Migrate databases and file storage to AWS managed services

### Tasks
- [ ] Provision RDS PostgreSQL Multi-AZ instances
- [ ] Configure KMS CMK for RDS encryption
- [ ] Deploy AWS DMS replication instances
- [ ] Run full load migration with DMS
- [ ] Enable CDC (change data capture) for live replication
- [ ] Validate data integrity post-migration
- [ ] Create S3 buckets with versioning and lifecycle policies
- [ ] Migrate file storage using AWS DataSync or AWS CLI
- [ ] Update application configuration to point to AWS data sources
- [ ] Cutover from on-premises databases

### AWS Services
- RDS (PostgreSQL Multi-AZ)
- AWS DMS (Database Migration Service)
- S3, S3 Lifecycle
- KMS CMK
- AWS DataSync

### Success Criteria
- Zero data loss verified post-migration
- Application latency to RDS within SLA
- S3 storage fully replicated from on-prem
- Automated backup and restore tested

---

## Wave 4: Observability and Security (Weeks 13–14)

**Objective:** Full-stack observability and security hardening

### Tasks
- [ ] Deploy Prometheus and Grafana on EKS
- [ ] Configure CloudWatch Container Insights
- [ ] Create CloudWatch dashboards and alarms
- [ ] Configure GuardDuty threat detection
- [ ] Enable Amazon Inspector for vulnerability scanning
- [ ] Set up AWS Config rules for compliance
- [ ] Configure SNS notifications for critical alarms
- [ ] Set up PagerDuty / Slack integration for alerting

### AWS Services
- CloudWatch (Logs, Metrics, Alarms, Dashboards)
- GuardDuty
- Amazon Inspector
- AWS Config
- SNS, PagerDuty

### Success Criteria
- All critical services have CloudWatch alarms
- Grafana dashboards showing real-time metrics
- GuardDuty findings reviewed and actioned
- Mean Time to Detect (MTTD) baseline established

---

## Wave 5: Optimisation (Weeks 15–16)

**Objective:** Cost optimisation, right-sizing, and performance tuning

### Tasks
- [ ] Run AWS Cost Explorer analysis
- [ ] Review Compute Optimizer recommendations
- [ ] Purchase Reserved Instances for stable workloads (1-year)
- [ ] Implement S3 Intelligent-Tiering
- [ ] Right-size EKS node groups based on observed usage
- [ ] Configure Spot Instances for dev/test workloads
- [ ] Review and remove unused resources
- [ ] Document lessons learned and runbooks

### AWS Services
- Cost Explorer, Budgets
- Compute Optimizer
- Trusted Advisor
- Reserved Instances / Savings Plans

### Success Criteria
- 20%+ cost reduction vs initial estimate achieved
- All recommendations from Trusted Advisor addressed
- Complete runbook documentation delivered
- Decommissioning plan for on-prem resources approved

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Data loss during database migration | Medium | High | DMS CDC + validation scripts, rollback plan |
| Application incompatibility with containers | Medium | Medium | Thorough containerization testing in staging |
| Network latency to AWS exceeds SLA | Low | High | Direct Connect with guaranteed bandwidth |
| Cost overrun | Medium | Medium | AWS Budgets alerts at 80% and 100% thresholds |
| Key personnel unavailability | Low | Medium | Cross-train team, detailed runbooks |
| DMS schema conversion failures | Medium | High | AWS SCT pre-assessment + manual review |

---

## Rollback Strategy

Each wave has an independent rollback procedure:

1. **Wave 1:** Delete Terraform resources with `terraform destroy`
2. **Wave 2:** Traffic can be routed back to on-prem via DNS TTL changes
3. **Wave 3:** DMS replication kept running in reverse for 72h post-cutover
4. **Wave 4/5:** Observability and optimisation changes are non-destructive

---

## Contacts

| Role | Responsibility |
|------|---------------|
| Cloud Architect | Overall design and Wave 1-2 |
| DBA | Database migration (Wave 3) |
| DevOps Engineer | CI/CD and EKS deployment |
| Security Engineer | IAM, KMS, GuardDuty (Wave 4) |
| Project Manager | Timeline and stakeholder communication |
