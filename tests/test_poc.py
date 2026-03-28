"""
Pytest test suite for Hays Edinburgh AWS DevOps POC.
Pure file-based tests — no live AWS / API calls.
"""

import json
import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).parent.parent

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def read_text(rel_path: str) -> str:
    return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def read_yaml(rel_path: str):
    return yaml.safe_load(read_text(rel_path))


def read_json(rel_path: str):
    return json.loads(read_text(rel_path))


# ===========================================================================
# 1. FILE / DIRECTORY STRUCTURE
# ===========================================================================

class TestDirectoryStructure:
    def test_terraform_dir_exists(self):
        assert (REPO_ROOT / "terraform").is_dir()

    def test_k8s_dir_exists(self):
        assert (REPO_ROOT / "k8s").is_dir()

    def test_helm_dir_exists(self):
        assert (REPO_ROOT / "helm").is_dir()

    def test_helm_app_chart_dir_exists(self):
        assert (REPO_ROOT / "helm" / "app-chart").is_dir()

    def test_jenkins_dir_exists(self):
        assert (REPO_ROOT / "jenkins").is_dir()

    def test_github_workflows_dir_exists(self):
        assert (REPO_ROOT / ".github" / "workflows").is_dir()

    def test_monitoring_dir_exists(self):
        assert (REPO_ROOT / "monitoring").is_dir()

    def test_migration_dir_exists(self):
        assert (REPO_ROOT / "migration").is_dir()

    def test_scripts_dir_exists(self):
        assert (REPO_ROOT / "scripts").is_dir()

    def test_app_dir_exists(self):
        assert (REPO_ROOT / "app").is_dir()

    def test_tests_dir_exists(self):
        assert (REPO_ROOT / "tests").is_dir()

    def test_terraform_modules_dir_exists(self):
        assert (REPO_ROOT / "terraform" / "modules").is_dir()


class TestFilePresence:
    def test_readme_exists(self):
        assert (REPO_ROOT / "README.md").is_file()

    def test_terraform_main_tf_exists(self):
        assert (REPO_ROOT / "terraform" / "main.tf").is_file()

    def test_terraform_outputs_tf_exists(self):
        assert (REPO_ROOT / "terraform" / "outputs.tf").is_file()

    def test_terraform_module_vpc_exists(self):
        assert (REPO_ROOT / "terraform" / "modules" / "vpc" / "main.tf").is_file()

    def test_terraform_module_eks_exists(self):
        assert (REPO_ROOT / "terraform" / "modules" / "eks" / "main.tf").is_file()

    def test_terraform_module_rds_exists(self):
        assert (REPO_ROOT / "terraform" / "modules" / "rds" / "main.tf").is_file()

    def test_terraform_module_s3_exists(self):
        assert (REPO_ROOT / "terraform" / "modules" / "s3" / "main.tf").is_file()

    def test_terraform_module_iam_exists(self):
        assert (REPO_ROOT / "terraform" / "modules" / "iam" / "main.tf").is_file()

    def test_terraform_module_kms_exists(self):
        assert (REPO_ROOT / "terraform" / "modules" / "kms" / "main.tf").is_file()

    def test_k8s_deployment_yaml_exists(self):
        assert (REPO_ROOT / "k8s" / "deployment.yaml").is_file()

    def test_k8s_service_yaml_exists(self):
        assert (REPO_ROOT / "k8s" / "service.yaml").is_file()

    def test_k8s_ingress_yaml_exists(self):
        assert (REPO_ROOT / "k8s" / "ingress.yaml").is_file()

    def test_k8s_hpa_yaml_exists(self):
        assert (REPO_ROOT / "k8s" / "hpa.yaml").is_file()

    def test_helm_chart_yaml_exists(self):
        assert (REPO_ROOT / "helm" / "app-chart" / "Chart.yaml").is_file()

    def test_helm_values_yaml_exists(self):
        assert (REPO_ROOT / "helm" / "app-chart" / "values.yaml").is_file()

    def test_helm_templates_deployment_exists(self):
        assert (REPO_ROOT / "helm" / "app-chart" / "templates" / "deployment.yaml").is_file()

    def test_helm_templates_helpers_exists(self):
        assert (REPO_ROOT / "helm" / "app-chart" / "templates" / "_helpers.tpl").is_file()

    def test_jenkinsfile_exists(self):
        assert (REPO_ROOT / "jenkins" / "Jenkinsfile").is_file()

    def test_github_actions_workflow_exists(self):
        assert (REPO_ROOT / ".github" / "workflows" / "ci-cd.yml").is_file()

    def test_monitoring_cloudwatch_dashboard_exists(self):
        assert (REPO_ROOT / "monitoring" / "cloudwatch_dashboard.json").is_file()

    def test_monitoring_prometheus_exists(self):
        assert (REPO_ROOT / "monitoring" / "prometheus.yml").is_file()

    def test_monitoring_grafana_dashboard_exists(self):
        assert (REPO_ROOT / "monitoring" / "grafana_dashboard.json").is_file()

    def test_migration_assessment_script_exists(self):
        assert (REPO_ROOT / "migration" / "assessment_script.py").is_file()

    def test_migration_wave_plan_exists(self):
        assert (REPO_ROOT / "migration" / "wave_plan.md").is_file()

    def test_scripts_iam_audit_exists(self):
        assert (REPO_ROOT / "scripts" / "iam_audit.sh").is_file()

    def test_scripts_kms_setup_exists(self):
        assert (REPO_ROOT / "scripts" / "kms_setup.sh").is_file()

    def test_app_main_py_exists(self):
        assert (REPO_ROOT / "app" / "main.py").is_file()

    def test_app_dockerfile_exists(self):
        assert (REPO_ROOT / "app" / "Dockerfile").is_file()

    def test_app_requirements_txt_exists(self):
        assert (REPO_ROOT / "app" / "requirements.txt").is_file()


# ===========================================================================
# 2. TERRAFORM — ROOT MODULE
# ===========================================================================

class TestTerraformMain:
    def _content(self):
        return read_text("terraform/main.tf")

    def test_terraform_required_version(self):
        assert ">= 1.6.0" in self._content()

    def test_aws_provider_declared(self):
        assert 'source  = "hashicorp/aws"' in self._content()

    def test_aws_provider_version(self):
        assert "~> 5.0" in self._content()

    def test_kubernetes_provider_declared(self):
        assert 'source  = "hashicorp/kubernetes"' in self._content()

    def test_helm_provider_declared(self):
        assert 'source  = "hashicorp/helm"' in self._content()

    def test_s3_backend_configured(self):
        assert 'backend "s3"' in self._content()

    def test_s3_backend_bucket(self):
        assert "hays-terraform-state" in self._content()

    def test_s3_backend_dynamodb_table(self):
        assert "hays-terraform-locks" in self._content()

    def test_s3_backend_encrypt(self):
        assert "encrypt        = true" in self._content()

    def test_region_variable(self):
        assert 'variable "aws_region"' in self._content()

    def test_environment_variable(self):
        assert 'variable "environment"' in self._content()

    def test_account_id_variable(self):
        assert 'variable "account_id"' in self._content()

    def test_db_password_variable_sensitive(self):
        assert "sensitive   = true" in self._content()

    def test_module_kms_called(self):
        assert 'module "kms"' in self._content()

    def test_module_vpc_called(self):
        assert 'module "vpc"' in self._content()

    def test_module_iam_called(self):
        assert 'module "iam"' in self._content()

    def test_module_eks_called(self):
        assert 'module "eks"' in self._content()

    def test_module_rds_called(self):
        assert 'module "rds"' in self._content()

    def test_module_s3_artifacts_called(self):
        assert 'module "s3_artifacts"' in self._content()

    def test_module_s3_backups_called(self):
        assert 'module "s3_backups"' in self._content()

    def test_region_default_eu_west_2(self):
        assert 'default     = "eu-west-2"' in self._content()

    def test_default_tags_present(self):
        assert "default_tags" in self._content()

    def test_project_tag(self):
        assert "hays-devops-poc" in self._content()


class TestTerraformOutputs:
    def _content(self):
        return read_text("terraform/outputs.tf")

    def test_eks_cluster_name_output(self):
        assert 'output "eks_cluster_name"' in self._content()

    def test_eks_cluster_endpoint_output(self):
        assert 'output "eks_cluster_endpoint"' in self._content()

    def test_vpc_id_output(self):
        assert 'output "vpc_id"' in self._content()

    def test_rds_endpoint_output(self):
        assert 'output "rds_endpoint"' in self._content()

    def test_artifacts_bucket_output(self):
        assert 'output "artifacts_bucket"' in self._content()

    def test_cicd_role_arn_output(self):
        assert 'output "cicd_role_arn"' in self._content()

    def test_eks_kms_key_arn_output(self):
        assert 'output "eks_kms_key_arn"' in self._content()


# ===========================================================================
# 3. TERRAFORM MODULES
# ===========================================================================

class TestTerraformModuleVPC:
    def _content(self):
        return read_text("terraform/modules/vpc/main.tf")

    def test_vpc_cidr_variable(self):
        assert 'variable "vpc_cidr"' in self._content()

    def test_default_cidr_block(self):
        assert "10.0.0.0/16" in self._content()

    def test_aws_vpc_resource(self):
        assert 'resource "aws_vpc" "main"' in self._content()

    def test_dns_hostnames_enabled(self):
        assert "enable_dns_hostnames = true" in self._content()

    def test_public_subnet_resource(self):
        assert 'resource "aws_subnet" "public"' in self._content()

    def test_private_subnet_resource(self):
        assert 'resource "aws_subnet" "private"' in self._content()

    def test_internet_gateway_resource(self):
        assert 'resource "aws_internet_gateway" "main"' in self._content()

    def test_nat_gateway_resource(self):
        assert 'resource "aws_nat_gateway" "main"' in self._content()

    def test_route_table_public(self):
        assert 'resource "aws_route_table" "public"' in self._content()

    def test_route_table_private(self):
        assert 'resource "aws_route_table" "private"' in self._content()

    def test_security_group_eks_cluster(self):
        assert 'resource "aws_security_group" "eks_cluster"' in self._content()

    def test_three_availability_zones(self):
        assert "eu-west-2a" in self._content()
        assert "eu-west-2b" in self._content()
        assert "eu-west-2c" in self._content()

    def test_elb_subnet_tag(self):
        assert "kubernetes.io/role/elb" in self._content()

    def test_internal_elb_subnet_tag(self):
        assert "kubernetes.io/role/internal-elb" in self._content()

    def test_vpc_id_output(self):
        assert 'output "vpc_id"' in self._content()

    def test_private_subnet_ids_output(self):
        assert 'output "private_subnet_ids"' in self._content()

    def test_public_subnet_ids_output(self):
        assert 'output "public_subnet_ids"' in self._content()


class TestTerraformModuleEKS:
    def _content(self):
        return read_text("terraform/modules/eks/main.tf")

    def test_eks_cluster_resource(self):
        assert 'resource "aws_eks_cluster" "main"' in self._content()

    def test_kubernetes_version_default(self):
        assert '"1.28"' in self._content()

    def test_endpoint_public_access_disabled(self):
        assert "endpoint_public_access  = false" in self._content()

    def test_endpoint_private_access_enabled(self):
        assert "endpoint_private_access = true" in self._content()

    def test_encryption_config_present(self):
        assert "encryption_config" in self._content()

    def test_kms_key_arn_variable(self):
        assert 'variable "kms_key_arn"' in self._content()

    def test_cloudwatch_logging_enabled(self):
        assert "enabled_cluster_log_types" in self._content()

    def test_audit_logging(self):
        assert '"audit"' in self._content()

    def test_node_group_resource(self):
        assert 'resource "aws_eks_node_group" "main"' in self._content()

    def test_t3_medium_instance_type(self):
        assert '"t3.medium"' in self._content()

    def test_scaling_config_present(self):
        assert "scaling_config" in self._content()

    def test_coredns_addon(self):
        assert '"coredns"' in self._content()

    def test_kube_proxy_addon(self):
        assert '"kube-proxy"' in self._content()

    def test_vpc_cni_addon(self):
        assert '"vpc-cni"' in self._content()

    def test_cluster_name_output(self):
        assert 'output "cluster_name"' in self._content()

    def test_cluster_endpoint_output(self):
        assert 'output "cluster_endpoint"' in self._content()


class TestTerraformModuleRDS:
    def _content(self):
        return read_text("terraform/modules/rds/main.tf")

    def test_db_instance_resource(self):
        assert 'resource "aws_db_instance" "main"' in self._content()

    def test_postgres_engine(self):
        assert '"postgres"' in self._content()

    def test_multi_az_enabled(self):
        assert "multi_az               = true" in self._content()

    def test_storage_encrypted(self):
        assert "storage_encrypted = true" in self._content()

    def test_deletion_protection(self):
        assert "deletion_protection    = true" in self._content()

    def test_publicly_accessible_false(self):
        assert "publicly_accessible    = false" in self._content()

    def test_performance_insights_enabled(self):
        assert "performance_insights_enabled          = true" in self._content()

    def test_backup_retention(self):
        assert "backup_retention_period = 7" in self._content()

    def test_cloudwatch_logs_export(self):
        assert "enabled_cloudwatch_logs_exports" in self._content()

    def test_subnet_group_resource(self):
        assert 'resource "aws_db_subnet_group" "main"' in self._content()

    def test_rds_security_group_resource(self):
        assert 'resource "aws_security_group" "rds"' in self._content()

    def test_rds_endpoint_output(self):
        assert 'output "rds_endpoint"' in self._content()


class TestTerraformModuleS3:
    def _content(self):
        return read_text("terraform/modules/s3/main.tf")

    def test_s3_bucket_resource(self):
        assert 'resource "aws_s3_bucket" "main"' in self._content()

    def test_versioning_resource(self):
        assert 'resource "aws_s3_bucket_versioning" "main"' in self._content()

    def test_encryption_resource(self):
        assert 'resource "aws_s3_bucket_server_side_encryption_configuration" "main"' in self._content()

    def test_kms_encryption_algorithm(self):
        assert '"aws:kms"' in self._content()

    def test_public_access_block_resource(self):
        assert 'resource "aws_s3_bucket_public_access_block" "main"' in self._content()

    def test_block_public_acls(self):
        assert "block_public_acls       = true" in self._content()

    def test_block_public_policy(self):
        assert "block_public_policy     = true" in self._content()

    def test_restrict_public_buckets(self):
        assert "restrict_public_buckets = true" in self._content()

    def test_lifecycle_configuration(self):
        assert 'resource "aws_s3_bucket_lifecycle_configuration" "main"' in self._content()

    def test_lifecycle_glacier_transition(self):
        assert '"GLACIER"' in self._content()

    def test_lifecycle_standard_ia_transition(self):
        assert '"STANDARD_IA"' in self._content()

    def test_logging_resource(self):
        assert 'resource "aws_s3_bucket_logging" "main"' in self._content()

    def test_bucket_arn_output(self):
        assert 'output "bucket_arn"' in self._content()

    def test_bucket_name_output(self):
        assert 'output "bucket_name"' in self._content()


class TestTerraformModuleIAM:
    def _content(self):
        return read_text("terraform/modules/iam/main.tf")

    def test_eks_cluster_role_resource(self):
        assert 'resource "aws_iam_role" "eks_cluster"' in self._content()

    def test_eks_node_role_resource(self):
        assert 'resource "aws_iam_role" "eks_node"' in self._content()

    def test_cicd_role_resource(self):
        assert 'resource "aws_iam_role" "cicd"' in self._content()

    def test_oidc_federation_for_cicd(self):
        assert "AssumeRoleWithWebIdentity" in self._content()

    def test_github_actions_oidc_provider(self):
        assert "token.actions.githubusercontent.com" in self._content()

    def test_eks_cluster_policy_attachment(self):
        assert "AmazonEKSClusterPolicy" in self._content()

    def test_eks_worker_node_policy_attachment(self):
        assert "AmazonEKSWorkerNodePolicy" in self._content()

    def test_eks_cni_policy_attachment(self):
        assert "AmazonEKS_CNI_Policy" in self._content()

    def test_ecr_readonly_policy(self):
        assert "AmazonEC2ContainerRegistryReadOnly" in self._content()

    def test_cicd_policy_ecr_access(self):
        assert "ECRAccess" in self._content()

    def test_cicd_policy_eks_access(self):
        assert "EKSAccess" in self._content()

    def test_cicd_role_arn_output(self):
        assert 'output "cicd_role_arn"' in self._content()

    def test_saikirangvariganti_in_oidc_condition(self):
        assert "saikirangvariganti" in self._content()


class TestTerraformModuleKMS:
    def _content(self):
        return read_text("terraform/modules/kms/main.tf")

    def test_eks_kms_key_resource(self):
        assert 'resource "aws_kms_key" "eks"' in self._content()

    def test_rds_kms_key_resource(self):
        assert 'resource "aws_kms_key" "rds"' in self._content()

    def test_s3_kms_key_resource(self):
        assert 'resource "aws_kms_key" "s3"' in self._content()

    def test_key_rotation_enabled(self):
        assert "enable_key_rotation     = true" in self._content()

    def test_eks_kms_alias(self):
        assert 'resource "aws_kms_alias" "eks"' in self._content()

    def test_rds_kms_alias(self):
        assert 'resource "aws_kms_alias" "rds"' in self._content()

    def test_s3_kms_alias(self):
        assert 'resource "aws_kms_alias" "s3"' in self._content()

    def test_eks_kms_key_arn_output(self):
        assert 'output "eks_kms_key_arn"' in self._content()

    def test_rds_kms_key_arn_output(self):
        assert 'output "rds_kms_key_arn"' in self._content()

    def test_s3_kms_key_arn_output(self):
        assert 'output "s3_kms_key_arn"' in self._content()

    def test_deletion_window_variable(self):
        assert 'variable "deletion_window_in_days"' in self._content()


# ===========================================================================
# 4. KUBERNETES MANIFESTS
# ===========================================================================

class TestK8sDeployment:
    def _doc(self):
        return read_yaml("k8s/deployment.yaml")

    def test_kind_is_deployment(self):
        assert self._doc()["kind"] == "Deployment"

    def test_namespace_is_production(self):
        assert self._doc()["metadata"]["namespace"] == "production"

    def test_app_name(self):
        assert self._doc()["metadata"]["name"] == "hays-devops-app"

    def test_replicas_is_three(self):
        assert self._doc()["spec"]["replicas"] == 3

    def test_rolling_update_strategy(self):
        assert self._doc()["spec"]["strategy"]["type"] == "RollingUpdate"

    def test_run_as_non_root(self):
        assert self._doc()["spec"]["template"]["spec"]["securityContext"]["runAsNonRoot"] is True

    def test_run_as_user_1000(self):
        assert self._doc()["spec"]["template"]["spec"]["securityContext"]["runAsUser"] == 1000

    def test_container_port_8080(self):
        containers = self._doc()["spec"]["template"]["spec"]["containers"]
        ports = [p["containerPort"] for p in containers[0]["ports"]]
        assert 8080 in ports

    def test_liveness_probe_health_path(self):
        probe = self._doc()["spec"]["template"]["spec"]["containers"][0]["livenessProbe"]
        assert probe["httpGet"]["path"] == "/health"

    def test_readiness_probe_ready_path(self):
        probe = self._doc()["spec"]["template"]["spec"]["containers"][0]["readinessProbe"]
        assert probe["httpGet"]["path"] == "/ready"

    def test_no_privilege_escalation(self):
        sc = self._doc()["spec"]["template"]["spec"]["containers"][0]["securityContext"]
        assert sc["allowPrivilegeEscalation"] is False

    def test_read_only_root_filesystem(self):
        sc = self._doc()["spec"]["template"]["spec"]["containers"][0]["securityContext"]
        assert sc["readOnlyRootFilesystem"] is True

    def test_all_capabilities_dropped(self):
        sc = self._doc()["spec"]["template"]["spec"]["containers"][0]["securityContext"]
        assert "ALL" in sc["capabilities"]["drop"]

    def test_prometheus_scrape_annotation(self):
        ann = self._doc()["spec"]["template"]["metadata"]["annotations"]
        assert ann.get("prometheus.io/scrape") == "true"

    def test_resource_limits_present(self):
        res = self._doc()["spec"]["template"]["spec"]["containers"][0]["resources"]
        assert "limits" in res
        assert "requests" in res

    def test_pod_anti_affinity_configured(self):
        affinity = self._doc()["spec"]["template"]["spec"]["affinity"]
        assert "podAntiAffinity" in affinity

    def test_tmp_volume_mount(self):
        containers = self._doc()["spec"]["template"]["spec"]["containers"]
        mounts = [v["mountPath"] for v in containers[0].get("volumeMounts", [])]
        assert "/tmp" in mounts

    def test_secret_ref_for_db_host(self):
        containers = self._doc()["spec"]["template"]["spec"]["containers"]
        env_vars = containers[0].get("env", [])
        db_host_env = next((e for e in env_vars if e["name"] == "DB_HOST"), None)
        assert db_host_env is not None
        assert "secretKeyRef" in db_host_env.get("valueFrom", {})


class TestK8sHPA:
    def _doc(self):
        return read_yaml("k8s/hpa.yaml")

    def test_kind_is_hpa(self):
        assert self._doc()["kind"] == "HorizontalPodAutoscaler"

    def test_min_replicas_is_two(self):
        assert self._doc()["spec"]["minReplicas"] == 2

    def test_max_replicas_is_twenty(self):
        assert self._doc()["spec"]["maxReplicas"] == 20

    def test_cpu_metric_present(self):
        metrics = self._doc()["spec"]["metrics"]
        cpu_metrics = [m for m in metrics if m["resource"]["name"] == "cpu"]
        assert len(cpu_metrics) >= 1

    def test_memory_metric_present(self):
        metrics = self._doc()["spec"]["metrics"]
        mem_metrics = [m for m in metrics if m["resource"]["name"] == "memory"]
        assert len(mem_metrics) >= 1

    def test_scale_target_ref_deployment(self):
        ref = self._doc()["spec"]["scaleTargetRef"]
        assert ref["kind"] == "Deployment"
        assert ref["name"] == "hays-devops-app"

    def test_scale_down_stabilization(self):
        behavior = self._doc()["spec"]["behavior"]
        assert behavior["scaleDown"]["stabilizationWindowSeconds"] == 300


class TestK8sIngress:
    def _doc(self):
        return read_yaml("k8s/ingress.yaml")

    def test_kind_is_ingress(self):
        assert self._doc()["kind"] == "Ingress"

    def test_alb_ingress_class(self):
        annotations = self._doc()["metadata"]["annotations"]
        assert annotations.get("kubernetes.io/ingress.class") == "alb"

    def test_internal_scheme(self):
        annotations = self._doc()["metadata"]["annotations"]
        assert annotations.get("alb.ingress.kubernetes.io/scheme") == "internal"

    def test_https_listener_configured(self):
        annotations = self._doc()["metadata"]["annotations"]
        assert "443" in annotations.get("alb.ingress.kubernetes.io/listen-ports", "")

    def test_waf_annotation_present(self):
        annotations = self._doc()["metadata"]["annotations"]
        assert "alb.ingress.kubernetes.io/wafv2-acl-arn" in annotations

    def test_tls_configured(self):
        assert "tls" in self._doc()["spec"]

    def test_health_check_path(self):
        annotations = self._doc()["metadata"]["annotations"]
        assert annotations.get("alb.ingress.kubernetes.io/healthcheck-path") == "/health"


class TestK8sService:
    def _doc(self):
        return read_yaml("k8s/service.yaml")

    def test_kind_is_service(self):
        assert self._doc()["kind"] == "Service"

    def test_service_type_clusterip(self):
        assert self._doc()["spec"]["type"] == "ClusterIP"

    def test_http_port_80(self):
        ports = self._doc()["spec"]["ports"]
        http_port = next((p for p in ports if p["name"] == "http"), None)
        assert http_port is not None
        assert http_port["port"] == 80

    def test_metrics_port_present(self):
        ports = self._doc()["spec"]["ports"]
        metrics_port = next((p for p in ports if p["name"] == "metrics"), None)
        assert metrics_port is not None

    def test_selector_matches_app(self):
        assert self._doc()["spec"]["selector"]["app"] == "hays-devops-app"


# ===========================================================================
# 5. HELM CHART
# ===========================================================================

class TestHelmChart:
    def _chart(self):
        return read_yaml("helm/app-chart/Chart.yaml")

    def test_chart_api_version_v2(self):
        assert self._chart()["apiVersion"] == "v2"

    def test_chart_name(self):
        assert self._chart()["name"] == "hays-devops-app"

    def test_chart_type_application(self):
        assert self._chart()["type"] == "application"

    def test_chart_version(self):
        assert "version" in self._chart()

    def test_maintainer_present(self):
        maintainers = self._chart().get("maintainers", [])
        assert len(maintainers) >= 1

    def test_maintainer_name(self):
        maintainers = self._chart().get("maintainers", [])
        names = [m.get("name", "") for m in maintainers]
        assert any("Sai Kiran" in n for n in names)

    def test_github_home_url(self):
        assert "saikirangvariganti" in self._chart().get("home", "")


class TestHelmValues:
    def _values(self):
        return read_yaml("helm/app-chart/values.yaml")

    def test_replica_count_present(self):
        assert "replicaCount" in self._values()

    def test_image_pull_policy_always(self):
        assert self._values()["image"]["pullPolicy"] == "Always"

    def test_service_account_with_irsa(self):
        sa = self._values().get("serviceAccount", {})
        annotations = sa.get("annotations", {})
        assert "eks.amazonaws.com/role-arn" in annotations

    def test_prometheus_scrape_annotation(self):
        pod_ann = self._values().get("podAnnotations", {})
        assert pod_ann.get("prometheus.io/scrape") == "true"

    def test_run_as_non_root(self):
        assert self._values()["podSecurityContext"]["runAsNonRoot"] is True

    def test_allow_privilege_escalation_false(self):
        assert self._values()["securityContext"]["allowPrivilegeEscalation"] is False

    def test_read_only_root_filesystem(self):
        assert self._values()["securityContext"]["readOnlyRootFilesystem"] is True

    def test_autoscaling_enabled(self):
        assert self._values()["autoscaling"]["enabled"] is True

    def test_autoscaling_min_replicas(self):
        assert self._values()["autoscaling"]["minReplicas"] == 2

    def test_autoscaling_max_replicas(self):
        assert self._values()["autoscaling"]["maxReplicas"] == 20

    def test_alb_ingress_class(self):
        assert self._values()["ingress"]["className"] == "alb"

    def test_liveness_probe_path(self):
        assert self._values()["livenessProbe"]["httpGet"]["path"] == "/health"

    def test_readiness_probe_path(self):
        assert self._values()["readinessProbe"]["httpGet"]["path"] == "/ready"

    def test_cpu_resource_limits(self):
        assert "cpu" in self._values()["resources"]["limits"]

    def test_memory_resource_requests(self):
        assert "memory" in self._values()["resources"]["requests"]

    def test_monitoring_enabled(self):
        assert self._values()["monitoring"]["enabled"] is True


# ===========================================================================
# 6. GITHUB ACTIONS CI/CD PIPELINE
# ===========================================================================

class TestGitHubActionsWorkflow:
    def _pipeline(self):
        return read_yaml(".github/workflows/ci-cd.yml")

    def _raw(self):
        return read_text(".github/workflows/ci-cd.yml")

    def _on_block(self):
        pipeline = self._pipeline()
        return pipeline.get("on", pipeline.get(True, {}))

    def test_workflow_name_present(self):
        assert self._pipeline().get("name") is not None

    def test_trigger_on_push_to_main(self):
        on = self._on_block()
        branches = on.get("push", {}).get("branches", [])
        assert "main" in branches

    def test_trigger_on_push_to_develop(self):
        on = self._on_block()
        branches = on.get("push", {}).get("branches", [])
        assert "develop" in branches

    def test_trigger_on_pull_request(self):
        on = self._on_block()
        assert "pull_request" in on

    def test_feature_branch_trigger(self):
        on = self._on_block()
        branches = on.get("push", {}).get("branches", [])
        assert any("feature" in str(b) for b in branches)

    def test_oidc_id_token_permission(self):
        perms = self._pipeline().get("permissions", {})
        assert perms.get("id-token") == "write"

    def test_contents_read_permission(self):
        perms = self._pipeline().get("permissions", {})
        assert perms.get("contents") == "read"

    def test_env_aws_region_eu_west_2(self):
        env = self._pipeline().get("env", {})
        assert env.get("AWS_REGION") == "eu-west-2"

    def test_env_eks_cluster_name(self):
        env = self._pipeline().get("env", {})
        assert env.get("EKS_CLUSTER_NAME") == "hays-devops-eks"

    def test_env_ecr_repository(self):
        env = self._pipeline().get("env", {})
        assert env.get("ECR_REPOSITORY") == "hays-devops-app"

    def test_lint_and_validate_job_present(self):
        assert "lint-and-validate" in self._pipeline().get("jobs", {})

    def test_unit_tests_job_present(self):
        assert "unit-tests" in self._pipeline().get("jobs", {})

    def test_security_scan_job_present(self):
        assert "security-scan" in self._pipeline().get("jobs", {})

    def test_build_and_push_job_present(self):
        assert "build-and-push" in self._pipeline().get("jobs", {})

    def test_deploy_staging_job_present(self):
        assert "deploy-staging" in self._pipeline().get("jobs", {})

    def test_deploy_production_job_present(self):
        assert "deploy-production" in self._pipeline().get("jobs", {})

    def test_trivy_scan_used(self):
        assert "trivy-action" in self._raw()

    def test_checkov_scan_used(self):
        assert "checkov-action" in self._raw()

    def test_helm_deploy_to_production(self):
        assert "helm upgrade --install" in self._raw()

    def test_configure_aws_credentials_oidc(self):
        assert "configure-aws-credentials" in self._raw()

    def test_ecr_login_action_used(self):
        assert "amazon-ecr-login" in self._raw()

    def test_terraform_validate_step(self):
        assert "terraform validate" in self._raw()

    def test_helm_lint_step(self):
        assert "helm lint" in self._raw()

    def test_python_version_env(self):
        assert "PYTHON_VERSION" in self._raw()

    def test_atomic_production_deploy(self):
        assert "--atomic" in self._raw()

    def test_kubectl_rollout_status(self):
        assert "kubectl rollout status" in self._raw()


# ===========================================================================
# 7. JENKINSFILE
# ===========================================================================

class TestJenkinsfile:
    def _content(self):
        return read_text("jenkins/Jenkinsfile")

    def test_pipeline_declaration(self):
        assert "pipeline {" in self._content()

    def test_kubernetes_agent(self):
        assert "kubernetes {" in self._content()

    def test_docker_container(self):
        assert "docker:24-dind" in self._content()

    def test_kubectl_container(self):
        assert "bitnami/kubectl" in self._content()

    def test_helm_container(self):
        assert "alpine/helm" in self._content()

    def test_trivy_container(self):
        assert "aquasec/trivy" in self._content()

    def test_terraform_container(self):
        assert "hashicorp/terraform" in self._content()

    def test_aws_region_env(self):
        assert "AWS_REGION          = 'eu-west-2'" in self._content()

    def test_ecr_repository_env(self):
        assert "ECR_REPOSITORY      = 'hays-devops-app'" in self._content()

    def test_eks_cluster_name_env(self):
        assert "EKS_CLUSTER_NAME    = 'hays-devops-eks'" in self._content()

    def test_sonar_project_key_env(self):
        assert "SONAR_PROJECT_KEY" in self._content()

    def test_checkout_stage(self):
        assert "stage('Checkout')" in self._content()

    def test_static_analysis_stage(self):
        assert "stage('Static Analysis')" in self._content()

    def test_unit_tests_stage(self):
        assert "stage('Unit Tests')" in self._content()

    def test_build_docker_image_stage(self):
        assert "stage('Build Docker Image')" in self._content()

    def test_security_scan_stage(self):
        assert "stage('Security Scan')" in self._content()

    def test_push_to_ecr_stage(self):
        assert "stage('Push to ECR')" in self._content()

    def test_terraform_apply_stage(self):
        assert "stage('Terraform Apply')" in self._content()

    def test_deploy_staging_stage(self):
        assert "stage('Deploy to Staging')" in self._content()

    def test_deploy_production_stage(self):
        assert "stage('Deploy to Production')" in self._content()

    def test_smoke_test_stage(self):
        assert "stage('Smoke Test')" in self._content()

    def test_production_deploy_requires_input(self):
        assert "input {" in self._content()

    def test_post_success_slack_notification(self):
        assert "slackSend(" in self._content()

    def test_post_failure_slack_notification(self):
        assert "#devops-alerts" in self._content()

    def test_parallel_stages_used(self):
        assert "parallel {" in self._content()

    def test_timeout_option_set(self):
        assert "timeout(time: 60" in self._content()

    def test_build_discarder_option(self):
        assert "buildDiscarder" in self._content()

    def test_deploy_env_parameter(self):
        assert "DEPLOY_ENV" in self._content()

    def test_run_terraform_parameter(self):
        assert "RUN_TERRAFORM" in self._content()

    def test_skip_tests_parameter(self):
        assert "SKIP_TESTS" in self._content()

    def test_trivy_container_scan(self):
        assert "trivy image" in self._content()

    def test_trivy_iac_scan(self):
        assert "trivy config" in self._content()

    def test_helm_upgrade_install(self):
        assert "helm upgrade --install" in self._content()

    def test_atomic_production_flag(self):
        assert "--atomic" in self._content()

    def test_clean_workspace_post(self):
        assert "cleanWs()" in self._content()


# ===========================================================================
# 8. APPLICATION (app/main.py)
# ===========================================================================

class TestAppMainPy:
    def _content(self):
        return read_text("app/main.py")

    def test_shebang_line(self):
        assert "#!/usr/bin/env python3" in self._content()

    def test_json_import(self):
        assert "import json" in self._content()

    def test_logging_import(self):
        assert "import logging" in self._content()

    def test_os_import(self):
        assert "import os" in self._content()

    def test_http_server_import(self):
        assert "from http.server import" in self._content()

    def test_app_name_constant(self):
        assert 'APP_NAME = "hays-devops-app"' in self._content()

    def test_app_version_constant(self):
        assert "APP_VERSION" in self._content()

    def test_port_constant(self):
        assert 'PORT = int(os.getenv("PORT"' in self._content()

    def test_get_health_status_function(self):
        assert "def get_health_status()" in self._content()

    def test_get_readiness_status_function(self):
        assert "def get_readiness_status()" in self._content()

    def test_get_metrics_function(self):
        assert "def get_metrics()" in self._content()

    def test_get_app_info_function(self):
        assert "def get_app_info()" in self._content()

    def test_request_handler_class(self):
        assert "class RequestHandler(BaseHTTPRequestHandler)" in self._content()

    def test_do_get_method(self):
        assert "def do_GET(self)" in self._content()

    def test_run_server_function(self):
        assert "def run_server(" in self._content()

    def test_health_endpoint_route(self):
        assert '"/health"' in self._content()

    def test_ready_endpoint_route(self):
        assert '"/ready"' in self._content()

    def test_metrics_endpoint_route(self):
        assert '"/metrics"' in self._content()

    def test_prometheus_metrics_format(self):
        assert "hays_app_requests_total" in self._content()

    def test_metrics_counter_dict(self):
        assert "_metrics" in self._content()

    def test_structured_logging_format(self):
        assert "timestamp" in self._content()

    def test_send_json_response_method(self):
        assert "def send_json_response(" in self._content()

    def test_github_url_in_app_info(self):
        assert "saikirangvariganti" in self._content()

    def test_main_guard(self):
        assert 'if __name__ == "__main__"' in self._content()


# ===========================================================================
# 9. DOCKERFILE
# ===========================================================================

class TestDockerfile:
    def _content(self):
        return read_text("app/Dockerfile")

    def test_multi_stage_build_builder(self):
        assert "AS builder" in self._content()

    def test_multi_stage_build_runtime(self):
        assert "AS runtime" in self._content()

    def test_python_311_base_image(self):
        assert "python:3.11-slim" in self._content()

    def test_non_root_user_created(self):
        assert "appuser" in self._content()

    def test_non_root_group_created(self):
        assert "appgroup" in self._content()

    def test_user_directive(self):
        assert "USER appuser" in self._content()

    def test_expose_8080(self):
        assert "EXPOSE 8080" in self._content()

    def test_healthcheck_instruction(self):
        assert "HEALTHCHECK" in self._content()

    def test_entrypoint_set(self):
        assert "ENTRYPOINT" in self._content()

    def test_build_args_present(self):
        assert "ARG BUILD_DATE" in self._content()
        assert "ARG GIT_COMMIT" in self._content()
        assert "ARG VERSION" in self._content()

    def test_oci_labels(self):
        assert "org.opencontainers.image" in self._content()

    def test_pythondontwritebytecode_env(self):
        assert "PYTHONDONTWRITEBYTECODE=1" in self._content()

    def test_pythonunbuffered_env(self):
        assert "PYTHONUNBUFFERED=1" in self._content()

    def test_no_create_home_for_appuser(self):
        assert "--no-create-home" in self._content()

    def test_tmp_dir_created(self):
        assert "mkdir -p /tmp" in self._content()


# ===========================================================================
# 10. MONITORING CONFIG
# ===========================================================================

class TestPrometheusConfig:
    def _config(self):
        return read_yaml("monitoring/prometheus.yml")

    def test_scrape_interval_30s(self):
        assert self._config()["global"]["scrape_interval"] == "30s"

    def test_external_labels_cluster(self):
        labels = self._config()["global"]["external_labels"]
        assert labels.get("cluster") == "hays-devops-eks"

    def test_external_labels_environment(self):
        labels = self._config()["global"]["external_labels"]
        assert labels.get("environment") == "production"

    def test_external_labels_region(self):
        labels = self._config()["global"]["external_labels"]
        assert labels.get("region") == "eu-west-2"

    def test_hays_app_scrape_job(self):
        jobs = [j["job_name"] for j in self._config()["scrape_configs"]]
        assert "hays-devops-app" in jobs

    def test_kubernetes_pods_scrape_job(self):
        jobs = [j["job_name"] for j in self._config()["scrape_configs"]]
        assert "kubernetes-pods" in jobs

    def test_kubernetes_nodes_scrape_job(self):
        jobs = [j["job_name"] for j in self._config()["scrape_configs"]]
        assert "kubernetes-nodes" in jobs

    def test_node_exporter_job(self):
        jobs = [j["job_name"] for j in self._config()["scrape_configs"]]
        assert "node-exporter" in jobs

    def test_kube_state_metrics_job(self):
        jobs = [j["job_name"] for j in self._config()["scrape_configs"]]
        assert "kube-state-metrics" in jobs

    def test_alertmanager_configured(self):
        assert "alerting" in self._config()

    def test_hays_app_metrics_path(self):
        jobs = self._config()["scrape_configs"]
        app_job = next((j for j in jobs if j["job_name"] == "hays-devops-app"), None)
        assert app_job is not None
        assert app_job.get("metrics_path") == "/metrics"

    def test_hays_app_scrape_namespace(self):
        jobs = self._config()["scrape_configs"]
        app_job = next((j for j in jobs if j["job_name"] == "hays-devops-app"), None)
        assert app_job is not None
        k8s_cfg = app_job.get("kubernetes_sd_configs", [{}])[0]
        namespaces = k8s_cfg.get("namespaces", {}).get("names", [])
        assert "production" in namespaces

    def test_cloudwatch_exporter_job(self):
        jobs = [j["job_name"] for j in self._config()["scrape_configs"]]
        assert "aws-cloudwatch-exporter" in jobs


class TestCloudWatchDashboard:
    def _dashboard(self):
        return read_json("monitoring/cloudwatch_dashboard.json")

    def test_dashboard_is_valid_json(self):
        assert self._dashboard() is not None

    def test_dashboard_is_dict_or_nonempty(self):
        d = self._dashboard()
        assert d is not None and (isinstance(d, dict) or isinstance(d, list))


class TestGrafanaDashboard:
    def _dashboard(self):
        return read_json("monitoring/grafana_dashboard.json")

    def test_dashboard_is_valid_json(self):
        assert self._dashboard() is not None

    def test_dashboard_is_dict(self):
        assert isinstance(self._dashboard(), dict)


# ===========================================================================
# 11. MIGRATION SCRIPTS
# ===========================================================================

class TestMigrationAssessmentScript:
    def _content(self):
        return read_text("migration/assessment_script.py")

    def test_shebang_line(self):
        assert "#!/usr/bin/env python3" in self._content()

    def test_dataclass_import(self):
        assert "from dataclasses import dataclass" in self._content()

    def test_system_info_dataclass(self):
        assert "class SystemInfo:" in self._content()

    def test_migration_recommendation_dataclass(self):
        assert "class MigrationRecommendation:" in self._content()

    def test_assessment_report_dataclass(self):
        assert "class AssessmentReport:" in self._content()

    def test_capture_system_info_function(self):
        assert "def capture_system_info()" in self._content()

    def test_get_aws_instance_recommendation_function(self):
        assert "def get_aws_instance_recommendation(" in self._content()

    def test_get_rds_recommendation_function(self):
        assert "def get_rds_recommendation(" in self._content()

    def test_estimate_monthly_cost_function(self):
        assert "def estimate_monthly_cost(" in self._content()

    def test_assess_workloads_function(self):
        assert "def assess_workloads(" in self._content()

    def test_generate_assessment_report_function(self):
        assert "def generate_assessment_report(" in self._content()

    def test_migration_waves_defined(self):
        assert "MIGRATION_WAVES" in self._content()

    def test_five_waves_defined(self):
        assert '"wave1"' in self._content()
        assert '"wave5"' in self._content()

    def test_eu_west_2_target_region(self):
        assert "eu-west-2" in self._content()

    def test_replatform_strategy(self):
        assert "replatform" in self._content()

    def test_rehost_strategy(self):
        assert "rehost" in self._content()

    def test_aws_instance_mapping(self):
        assert "AWS_INSTANCE_MAPPING" in self._content()

    def test_t3_medium_in_mapping(self):
        assert "t3.medium" in self._content()

    def test_rds_instance_mapping_postgresql(self):
        assert '"postgresql"' in self._content()

    def test_json_output_supported(self):
        assert "json.dump" in self._content()

    def test_main_guard(self):
        assert 'if __name__ == "__main__"' in self._content()


class TestMigrationWavePlan:
    def _content(self):
        return read_text("migration/wave_plan.md")

    def test_wave1_foundation(self):
        assert "Wave 1" in self._content()

    def test_wave2_stateless_applications(self):
        assert "Wave 2" in self._content()

    def test_wave3_data_layer(self):
        assert "Wave 3" in self._content()

    def test_wave4_observability(self):
        assert "Wave 4" in self._content()

    def test_wave5_optimisation(self):
        assert "Wave 5" in self._content()

    def test_eu_west_2_target_region(self):
        assert "eu-west-2" in self._content()

    def test_16_weeks_total(self):
        assert "16 weeks" in self._content()

    def test_eks_mentioned(self):
        assert "EKS" in self._content()

    def test_rds_mentioned(self):
        assert "RDS" in self._content()

    def test_terraform_mentioned(self):
        assert "Terraform" in self._content()

    def test_risk_register_present(self):
        assert "Risk Register" in self._content()

    def test_rollback_strategy_present(self):
        assert "Rollback" in self._content()

    def test_dms_mentioned(self):
        assert "DMS" in self._content()

    def test_kms_mentioned(self):
        assert "KMS" in self._content()


# ===========================================================================
# 12. BASH SCRIPTS
# ===========================================================================

class TestIAMAuditScript:
    def _content(self):
        return read_text("scripts/iam_audit.sh")

    def test_shebang_line(self):
        assert "#!/usr/bin/env bash" in self._content()

    def test_set_euo_pipefail(self):
        assert "set -euo pipefail" in self._content()

    def test_report_file_variable(self):
        assert "REPORT_FILE=" in self._content()

    def test_region_defaults_to_eu_west_2(self):
        assert "eu-west-2" in self._content()

    def test_log_function_defined(self):
        assert "log()" in self._content()

    def test_check_root_account_usage(self):
        assert "check_root_account_usage()" in self._content()

    def test_check_mfa_on_users(self):
        assert "check_mfa_on_users()" in self._content()

    def test_check_access_key_rotation(self):
        assert "check_access_key_rotation()" in self._content()

    def test_check_password_policy(self):
        assert "check_password_policy()" in self._content()

    def test_check_inline_policies(self):
        assert "check_inline_policies()" in self._content()

    def test_check_admin_policies(self):
        assert "check_admin_policies()" in self._content()

    def test_generate_report_function(self):
        assert "generate_report()" in self._content()

    def test_main_function(self):
        assert "main()" in self._content()

    def test_pass_count_tracked(self):
        assert "PASS_COUNT" in self._content()

    def test_fail_count_tracked(self):
        assert "FAIL_COUNT" in self._content()

    def test_json_output_format(self):
        assert '"report_type"' in self._content()

    def test_90_day_rotation_policy(self):
        assert "90" in self._content()

    def test_exit_code_on_failure(self):
        assert "exit 1" in self._content()


class TestKMSSetupScript:
    def _content(self):
        return read_text("scripts/kms_setup.sh")

    def test_shebang_line(self):
        assert "#!/usr/bin/env bash" in self._content()

    def test_set_euo_pipefail(self):
        assert "set -euo pipefail" in self._content()

    def test_region_defaults_to_eu_west_2(self):
        assert "eu-west-2" in self._content()

    def test_get_account_id_function(self):
        assert "get_account_id()" in self._content()

    def test_create_kms_key_function(self):
        assert "create_kms_key()" in self._content()

    def test_verify_key_rotation_function(self):
        assert "verify_key_rotation()" in self._content()

    def test_generate_report_function(self):
        assert "generate_report()" in self._content()

    def test_main_function(self):
        assert "main()" in self._content()

    def test_eks_key_creation(self):
        assert "eks-secrets" in self._content()

    def test_rds_key_creation(self):
        assert "rds-storage" in self._content()

    def test_s3_key_creation(self):
        assert "s3-encryption" in self._content()

    def test_enable_key_rotation_call(self):
        assert "enable-key-rotation" in self._content()

    def test_create_alias_call(self):
        assert "create-alias" in self._content()

    def test_json_report_generated(self):
        assert '"report_type"' in self._content()

    def test_three_keys_created(self):
        assert '"eks_secrets"' in self._content()
        assert '"rds_storage"' in self._content()
        assert '"s3_buckets"' in self._content()


# ===========================================================================
# 13. README COMPLETENESS
# ===========================================================================

class TestReadme:
    def _content(self):
        return read_text("README.md")

    def test_has_title(self):
        assert "Hays Edinburgh" in self._content()

    def test_has_architecture_overview(self):
        assert "Architecture" in self._content()

    def test_has_terraform_section(self):
        assert "Terraform" in self._content()

    def test_has_eks_mention(self):
        assert "EKS" in self._content()

    def test_has_cicd_section(self):
        assert "CI/CD" in self._content()

    def test_has_jenkins_mention(self):
        assert "Jenkins" in self._content()

    def test_has_github_actions_mention(self):
        assert "GitHub Actions" in self._content()

    def test_has_monitoring_section(self):
        assert "observability" in self._content().lower() or "monitoring" in self._content().lower()

    def test_has_prometheus_mention(self):
        assert "Prometheus" in self._content()

    def test_has_grafana_mention(self):
        assert "Grafana" in self._content()

    def test_has_cloudwatch_mention(self):
        assert "CloudWatch" in self._content()

    def test_has_iam_mention(self):
        assert "IAM" in self._content()

    def test_has_kms_mention(self):
        assert "KMS" in self._content()

    def test_has_migration_section(self):
        assert "migration" in self._content().lower() or "Migration" in self._content()

    def test_has_running_tests_section(self):
        assert "Running the Tests" in self._content() or "pytest" in self._content()

    def test_has_github_link(self):
        assert "saikirangvariganti" in self._content()

    def test_has_author_section(self):
        assert "Sai Kiran" in self._content()

    def test_has_helm_deploy_instructions(self):
        assert "helm upgrade --install" in self._content()

    def test_repository_structure_section(self):
        assert "Repository Structure" in self._content() or "terraform/" in self._content()

    def test_vpc_architecture_mentioned(self):
        assert "VPC" in self._content()


# ===========================================================================
# 14. MIGRATION ASSESSMENT LOGIC (unit-style, no I/O)
# ===========================================================================

class TestMigrationAssessmentLogic:
    """Import the module in-process to verify pure-logic functions."""

    @pytest.fixture(scope="class")
    def module(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "assessment_script",
            str(REPO_ROOT / "migration" / "assessment_script.py"),
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_instance_mapping_t3_medium_for_4_cpus(self, module):
        result = module.get_aws_instance_recommendation(4, 8)
        assert result == "t3.medium"

    def test_instance_mapping_large_cpu(self, module):
        result = module.get_aws_instance_recommendation(64, 128)
        assert "xlarge" in result or "large" in result

    def test_rds_recommendation_small_postgres(self, module):
        result = module.get_rds_recommendation("postgresql", 50)
        assert "micro" in result or "small" in result

    def test_rds_recommendation_medium_postgres(self, module):
        result = module.get_rds_recommendation("postgresql", 200)
        assert "medium" in result

    def test_rds_recommendation_unknown_engine_defaults_postgres(self, module):
        result = module.get_rds_recommendation("unknown_db", 50)
        assert result is not None

    def test_estimate_monthly_cost_t3_medium(self, module):
        cost = module.estimate_monthly_cost("ec2", "t3.medium")
        assert cost == pytest.approx(33.60, abs=0.01)

    def test_estimate_monthly_cost_with_storage(self, module):
        cost_no_storage = module.estimate_monthly_cost("ec2", "t3.medium", 0)
        cost_with_storage = module.estimate_monthly_cost("ec2", "t3.medium", 100)
        assert cost_with_storage > cost_no_storage

    def test_five_migration_waves_defined(self, module):
        assert len(module.MIGRATION_WAVES) == 5

    def test_assess_workloads_returns_list(self, module):
        mock_info = module.SystemInfo()
        result = module.assess_workloads(mock_info)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_build_migration_wave_plan_returns_dict(self, module):
        mock_info = module.SystemInfo()
        recommendations = module.assess_workloads(mock_info)
        wave_plan = module.build_migration_wave_plan(recommendations)
        assert isinstance(wave_plan, dict)
        assert "wave1" in wave_plan


# ===========================================================================
# 15. APP LOGIC (unit-style, no server startup)
# ===========================================================================

class TestAppLogic:
    """Import app/main.py to verify pure logic functions."""

    @pytest.fixture(scope="class")
    def app_module(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "app_main",
            str(REPO_ROOT / "app" / "main.py"),
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_get_health_status_returns_healthy(self, app_module):
        result = app_module.get_health_status()
        assert result["status"] == "healthy"

    def test_get_health_status_has_version(self, app_module):
        result = app_module.get_health_status()
        assert "version" in result

    def test_get_health_status_has_uptime(self, app_module):
        result = app_module.get_health_status()
        assert "uptime_seconds" in result

    def test_get_readiness_status_returns_ready(self, app_module):
        result = app_module.get_readiness_status()
        assert result["status"] == "ready"

    def test_get_readiness_status_has_checks(self, app_module):
        result = app_module.get_readiness_status()
        assert "checks" in result

    def test_get_metrics_contains_requests_total(self, app_module):
        output = app_module.get_metrics()
        assert "hays_app_requests_total" in output

    def test_get_metrics_contains_uptime(self, app_module):
        output = app_module.get_metrics()
        assert "hays_app_uptime_seconds" in output

    def test_get_app_info_has_name(self, app_module):
        result = app_module.get_app_info()
        assert result["name"] == "hays-devops-app"

    def test_get_app_info_has_github(self, app_module):
        result = app_module.get_app_info()
        assert "saikirangvariganti" in result.get("github", "")

    def test_get_app_info_has_features(self, app_module):
        result = app_module.get_app_info()
        assert len(result.get("features", [])) >= 1

    def test_get_app_info_has_endpoints(self, app_module):
        result = app_module.get_app_info()
        assert "endpoints" in result

    def test_metrics_is_prometheus_format(self, app_module):
        output = app_module.get_metrics()
        assert output.startswith("# HELP")
