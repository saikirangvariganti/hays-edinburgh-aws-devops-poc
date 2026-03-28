#!/usr/bin/env python3
"""
On-Premises to AWS Migration Assessment Script
Hays Edinburgh AWS DevOps POC

This script assesses on-premises workloads and generates migration recommendations
for moving to AWS, focusing on containerization (EKS), database migration (RDS),
and storage migration (S3).
"""

import json
import os
import platform
import socket
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional


# Compatibility: Use importlib.resources for Python 3.9+
try:
    import importlib.resources as pkg_resources
except ImportError:
    pkg_resources = None

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


MIGRATION_WAVES = {
    "wave1": {
        "name": "Foundation",
        "description": "Network connectivity, IAM, and core infrastructure",
        "duration_weeks": 2,
        "services": ["VPC", "IAM", "Direct Connect / VPN", "Route 53"],
    },
    "wave2": {
        "name": "Stateless Applications",
        "description": "Containerize and deploy stateless workloads to EKS",
        "duration_weeks": 4,
        "services": ["EKS", "ECR", "ALB", "WAF"],
    },
    "wave3": {
        "name": "Data Layer",
        "description": "Migrate databases to RDS and storage to S3",
        "duration_weeks": 6,
        "services": ["RDS", "S3", "DMS", "Snowball Edge"],
    },
    "wave4": {
        "name": "Observability and Security",
        "description": "CloudWatch, GuardDuty, Security Hub, Config",
        "duration_weeks": 2,
        "services": ["CloudWatch", "GuardDuty", "Security Hub", "Config", "KMS"],
    },
    "wave5": {
        "name": "Optimisation",
        "description": "Right-sizing, Reserved Instances, Cost Explorer",
        "duration_weeks": 2,
        "services": ["Cost Explorer", "Trusted Advisor", "Compute Optimizer"],
    },
}

AWS_INSTANCE_MAPPING = {
    1: "t3.micro",
    2: "t3.small",
    4: "t3.medium",
    8: "t3.large",
    16: "t3.xlarge",
    32: "t3.2xlarge",
    64: "m5.4xlarge",
    128: "m5.8xlarge",
}

DB_INSTANCE_MAPPING = {
    "postgresql": {
        "small": "db.t3.micro",
        "medium": "db.t3.medium",
        "large": "db.r5.large",
        "xlarge": "db.r5.xlarge",
    },
    "mysql": {
        "small": "db.t3.micro",
        "medium": "db.t3.medium",
        "large": "db.r5.large",
        "xlarge": "db.r5.xlarge",
    },
    "oracle": {
        "small": "db.r5.large",
        "medium": "db.r5.2xlarge",
        "large": "db.r5.4xlarge",
        "xlarge": "db.r5.8xlarge",
    },
    "sqlserver": {
        "small": "db.r5.large",
        "medium": "db.r5.2xlarge",
        "large": "db.r5.4xlarge",
        "xlarge": "db.r5.8xlarge",
    },
}


@dataclass
class SystemInfo:
    """Captured system information."""
    hostname: str = ""
    os_type: str = ""
    os_version: str = ""
    cpu_count: int = 0
    cpu_model: str = ""
    memory_gb: float = 0.0
    disk_gb: float = 0.0
    ip_address: str = ""
    running_services: List[str] = field(default_factory=list)
    open_ports: List[int] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class MigrationRecommendation:
    """Migration recommendation for a workload."""
    workload_name: str
    current_spec: Dict[str, Any]
    recommended_aws_service: str
    recommended_instance_type: str
    migration_strategy: str  # rehost, replatform, refactor, repurchase, retire
    estimated_cost_monthly_usd: float
    migration_wave: str
    complexity: str  # low, medium, high
    notes: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class AssessmentReport:
    """Full migration assessment report."""
    assessment_id: str
    generated_at: str
    target_region: str
    system_info: SystemInfo
    recommendations: List[MigrationRecommendation]
    migration_waves: Dict[str, Any]
    total_estimated_monthly_cost_usd: float = 0.0
    total_estimated_migration_weeks: int = 0
    summary: Dict[str, Any] = field(default_factory=dict)


def capture_system_info() -> SystemInfo:
    """Capture current system information for migration assessment."""
    info = SystemInfo()

    try:
        info.hostname = socket.gethostname()
        info.ip_address = socket.gethostbyname(info.hostname)
    except Exception:
        info.hostname = "unknown"
        info.ip_address = "unknown"

    info.os_type = platform.system()
    info.os_version = platform.version()

    if PSUTIL_AVAILABLE:
        try:
            info.cpu_count = psutil.cpu_count(logical=True)
            memory = psutil.virtual_memory()
            info.memory_gb = round(memory.total / (1024 ** 3), 2)
            disk = psutil.disk_usage("/")
            info.disk_gb = round(disk.total / (1024 ** 3), 2)
        except Exception:
            pass
    else:
        # Fallback without psutil
        info.cpu_count = os.cpu_count() or 1
        info.memory_gb = 4.0  # default assumption
        info.disk_gb = 100.0  # default assumption

    info.cpu_model = platform.processor() or "Unknown"

    return info


def get_aws_instance_recommendation(cpu_count: int, memory_gb: float) -> str:
    """Map on-premises specs to recommended AWS instance type."""
    # Find the smallest instance that meets requirements
    for cpu_threshold, instance_type in sorted(AWS_INSTANCE_MAPPING.items()):
        if cpu_count <= cpu_threshold:
            return instance_type
    return "m5.4xlarge"


def get_rds_recommendation(db_engine: str, data_size_gb: float) -> str:
    """Recommend RDS instance type based on database engine and size."""
    db_engine = db_engine.lower()
    if db_engine not in DB_INSTANCE_MAPPING:
        db_engine = "postgresql"

    mapping = DB_INSTANCE_MAPPING[db_engine]

    if data_size_gb < 100:
        return mapping["small"]
    elif data_size_gb < 500:
        return mapping["medium"]
    elif data_size_gb < 2000:
        return mapping["large"]
    else:
        return mapping["xlarge"]


def estimate_monthly_cost(service: str, instance_type: str, storage_gb: float = 0) -> float:
    """Rough monthly cost estimation for AWS services (eu-west-2 pricing)."""
    cost_map = {
        # EC2 / EKS worker nodes
        "t3.micro": 8.50,
        "t3.small": 17.00,
        "t3.medium": 33.60,
        "t3.large": 67.20,
        "t3.xlarge": 134.40,
        "t3.2xlarge": 268.80,
        "m5.4xlarge": 672.00,
        "m5.8xlarge": 1344.00,
        # RDS
        "db.t3.micro": 16.00,
        "db.t3.medium": 67.00,
        "db.r5.large": 196.00,
        "db.r5.xlarge": 392.00,
        "db.r5.2xlarge": 785.00,
        "db.r5.4xlarge": 1570.00,
        "db.r5.8xlarge": 3140.00,
    }

    base_cost = cost_map.get(instance_type, 100.0)

    # Add storage cost ($0.115/GB/month for gp3 in eu-west-2)
    storage_cost = storage_gb * 0.115

    return round(base_cost + storage_cost, 2)


def assess_workloads(system_info: SystemInfo, workload_definitions: Optional[List[Dict]] = None) -> List[MigrationRecommendation]:
    """Generate migration recommendations for discovered workloads."""
    recommendations = []

    if workload_definitions is None:
        # Default workload definitions for a typical enterprise on-prem stack
        workload_definitions = [
            {
                "name": "Web Application Servers",
                "type": "application",
                "cpu_count": system_info.cpu_count or 4,
                "memory_gb": system_info.memory_gb or 16,
                "instances": 3,
            },
            {
                "name": "PostgreSQL Database",
                "type": "database",
                "db_engine": "postgresql",
                "data_size_gb": 200,
                "cpu_count": 4,
                "memory_gb": 32,
            },
            {
                "name": "File Storage",
                "type": "storage",
                "data_size_gb": 500,
            },
            {
                "name": "Jenkins CI/CD",
                "type": "application",
                "cpu_count": 4,
                "memory_gb": 16,
                "instances": 1,
            },
        ]

    for workload in workload_definitions:
        wl_type = workload.get("type", "application")
        wl_name = workload.get("name", "Unknown Workload")

        if wl_type == "application":
            cpu = workload.get("cpu_count", 2)
            mem = workload.get("memory_gb", 8)
            instances = workload.get("instances", 1)
            instance_type = get_aws_instance_recommendation(cpu, mem)
            monthly_cost = estimate_monthly_cost("ec2", instance_type) * instances

            rec = MigrationRecommendation(
                workload_name=wl_name,
                current_spec={"cpu": cpu, "memory_gb": mem, "instances": instances},
                recommended_aws_service="EKS (Kubernetes Deployment)",
                recommended_instance_type=f"{instance_type} x{instances}",
                migration_strategy="replatform",
                estimated_cost_monthly_usd=monthly_cost,
                migration_wave="wave2",
                complexity="medium",
                notes=[
                    f"Containerize application using Docker",
                    f"Deploy to EKS with {instances} replicas minimum",
                    "Set up HPA for auto-scaling based on CPU/memory",
                    "Configure ALB Ingress Controller for load balancing",
                ],
                risks=[
                    "Application may have stateful components that need refactoring",
                    "Dependency on local file system needs S3 or EFS migration",
                ],
                dependencies=["VPC", "EKS Cluster", "ECR", "ALB"],
            )
            recommendations.append(rec)

        elif wl_type == "database":
            db_engine = workload.get("db_engine", "postgresql")
            data_size = workload.get("data_size_gb", 100)
            rds_instance = get_rds_recommendation(db_engine, data_size)
            monthly_cost = estimate_monthly_cost("rds", rds_instance, storage_gb=data_size)

            rec = MigrationRecommendation(
                workload_name=wl_name,
                current_spec={"engine": db_engine, "data_size_gb": data_size},
                recommended_aws_service="Amazon RDS",
                recommended_instance_type=rds_instance,
                migration_strategy="replatform",
                estimated_cost_monthly_usd=monthly_cost,
                migration_wave="wave3",
                complexity="high",
                notes=[
                    f"Use AWS DMS for zero-downtime migration",
                    f"Enable Multi-AZ for high availability",
                    "Enable automated backups with 7-day retention",
                    "Encrypt storage with KMS CMK",
                    "Enable Performance Insights",
                ],
                risks=[
                    "Schema compatibility issues between source and target",
                    "Stored procedures/triggers may require manual review",
                    "Application connection string changes required",
                ],
                dependencies=["VPC", "Private Subnets", "KMS", "Security Groups"],
            )
            recommendations.append(rec)

        elif wl_type == "storage":
            data_size = workload.get("data_size_gb", 100)
            monthly_cost = round(data_size * 0.023, 2)  # S3 Standard pricing eu-west-2

            rec = MigrationRecommendation(
                workload_name=wl_name,
                current_spec={"data_size_gb": data_size},
                recommended_aws_service="Amazon S3",
                recommended_instance_type="S3 Standard",
                migration_strategy="rehost",
                estimated_cost_monthly_usd=monthly_cost,
                migration_wave="wave3",
                complexity="low",
                notes=[
                    "Use AWS DataSync or S3 CLI for data transfer",
                    "Enable S3 versioning for data protection",
                    "Implement lifecycle policies for cost optimisation",
                    "Encrypt with KMS CMK",
                ],
                risks=[
                    "Large data transfers may require Snowball Edge for data > 10TB",
                    "Applications using local file paths need updating",
                ],
                dependencies=["S3 Bucket", "KMS", "IAM Policies"],
            )
            recommendations.append(rec)

    return recommendations


def build_migration_wave_plan(recommendations: List[MigrationRecommendation]) -> Dict[str, Any]:
    """Build a phased migration wave plan from recommendations."""
    wave_plan = {}

    for wave_id, wave_info in MIGRATION_WAVES.items():
        wave_workloads = [
            r.workload_name for r in recommendations
            if r.migration_wave == wave_id
        ]

        wave_plan[wave_id] = {
            "name": wave_info["name"],
            "description": wave_info["description"],
            "duration_weeks": wave_info["duration_weeks"],
            "aws_services": wave_info["services"],
            "workloads": wave_workloads,
            "estimated_cost_usd": sum(
                r.estimated_cost_monthly_usd for r in recommendations
                if r.migration_wave == wave_id
            ),
        }

    return wave_plan


def generate_assessment_report(
    target_region: str = "eu-west-2",
    workload_definitions: Optional[List[Dict]] = None,
    output_file: Optional[str] = None,
) -> AssessmentReport:
    """Generate a full migration assessment report."""

    assessment_id = f"HAYS-ASSESS-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    print(f"[+] Starting migration assessment: {assessment_id}")
    print(f"[+] Target AWS Region: {target_region}")

    # Capture system info
    print("[+] Capturing system information...")
    system_info = capture_system_info()
    print(f"    Hostname: {system_info.hostname}")
    print(f"    OS: {system_info.os_type} {system_info.os_version[:30]}")
    print(f"    CPUs: {system_info.cpu_count}, Memory: {system_info.memory_gb} GB")

    # Generate recommendations
    print("[+] Assessing workloads...")
    recommendations = assess_workloads(system_info, workload_definitions)
    print(f"    Found {len(recommendations)} workloads to migrate")

    # Build wave plan
    wave_plan = build_migration_wave_plan(recommendations)

    # Calculate totals
    total_monthly_cost = sum(r.estimated_cost_monthly_usd for r in recommendations)
    total_weeks = sum(w["duration_weeks"] for w in MIGRATION_WAVES.values())

    # Build summary
    strategy_counts: Dict[str, int] = {}
    complexity_counts: Dict[str, int] = {}
    for r in recommendations:
        strategy_counts[r.migration_strategy] = strategy_counts.get(r.migration_strategy, 0) + 1
        complexity_counts[r.complexity] = complexity_counts.get(r.complexity, 0) + 1

    summary = {
        "total_workloads": len(recommendations),
        "migration_strategies": strategy_counts,
        "complexity_breakdown": complexity_counts,
        "total_monthly_cost_usd": total_monthly_cost,
        "total_migration_weeks": total_weeks,
        "recommended_aws_region": target_region,
        "key_services": ["EKS", "RDS", "S3", "VPC", "IAM", "KMS", "CloudWatch"],
    }

    report = AssessmentReport(
        assessment_id=assessment_id,
        generated_at=datetime.utcnow().isoformat(),
        target_region=target_region,
        system_info=system_info,
        recommendations=recommendations,
        migration_waves=wave_plan,
        total_estimated_monthly_cost_usd=total_monthly_cost,
        total_estimated_migration_weeks=total_weeks,
        summary=summary,
    )

    print(f"\n[+] Assessment Complete!")
    print(f"    Total workloads: {len(recommendations)}")
    print(f"    Estimated monthly AWS cost: ${total_monthly_cost:,.2f}")
    print(f"    Estimated migration duration: {total_weeks} weeks")

    if output_file:
        report_dict = asdict(report)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report_dict, f, indent=2, default=str)
        print(f"\n[+] Report saved to: {output_file}")

    return report


if __name__ == "__main__":
    output_path = "migration_assessment_report.json"
    if len(sys.argv) > 1:
        output_path = sys.argv[1]

    report = generate_assessment_report(
        target_region="eu-west-2",
        output_file=output_path,
    )

    print("\n=== Migration Wave Summary ===")
    for wave_id, wave_data in report.migration_waves.items():
        print(f"\n{wave_id.upper()}: {wave_data['name']} ({wave_data['duration_weeks']} weeks)")
        print(f"  Description: {wave_data['description']}")
        print(f"  Workloads: {', '.join(wave_data['workloads']) or 'None'}")
        print(f"  AWS Services: {', '.join(wave_data['aws_services'])}")
        print(f"  Estimated Cost: ${wave_data['estimated_cost_usd']:,.2f}/month")
