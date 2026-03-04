"""AWS compliance check modules for auditclaw-grc."""

from .iam import run_iam_checks
from .s3 import run_s3_checks
from .cloudtrail import run_cloudtrail_checks
from .vpc import run_vpc_checks
from .kms import run_kms_checks
from .ec2 import run_ec2_checks
from .rds import run_rds_checks
from .security_hub import run_security_hub_checks
from .guardduty import run_guardduty_checks
from .lambda_check import run_lambda_checks
from .cloudwatch import run_cloudwatch_checks
from .config import run_config_checks
from .eks_ecs import run_eks_ecs_checks
from .elb import run_elb_checks
from .credential_report import run_credential_report_checks

ALL_CHECKS = {
    "iam": run_iam_checks,
    "s3": run_s3_checks,
    "cloudtrail": run_cloudtrail_checks,
    "vpc": run_vpc_checks,
    "kms": run_kms_checks,
    "ec2": run_ec2_checks,
    "rds": run_rds_checks,
    "security_hub": run_security_hub_checks,
    "guardduty": run_guardduty_checks,
    "lambda": run_lambda_checks,
    "cloudwatch": run_cloudwatch_checks,
    "config": run_config_checks,
    "eks_ecs": run_eks_ecs_checks,
    "elb": run_elb_checks,
    "credential_report": run_credential_report_checks,
}
