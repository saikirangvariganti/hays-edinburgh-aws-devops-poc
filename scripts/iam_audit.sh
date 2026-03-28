#!/usr/bin/env bash
# IAM Security Audit Script
# Hays Edinburgh AWS DevOps POC
# Audits IAM users, roles, and policies for security best practices

set -euo pipefail

REPORT_FILE="iam_audit_report_$(date +%Y%m%d_%H%M%S).json"
REGION="${AWS_DEFAULT_REGION:-eu-west-2}"
ACCOUNT_ID=""
FINDINGS=()
PASS_COUNT=0
FAIL_COUNT=0

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

check_root_account_usage() {
    log "Checking root account usage..."

    local root_last_used
    root_last_used=$(aws iam get-account-summary \
        --query 'SummaryMap.AccountAccessKeysPresent' \
        --output text 2>/dev/null || echo "0")

    if [[ "$root_last_used" == "0" ]]; then
        log "PASS: No root account access keys present"
        PASS_COUNT=$((PASS_COUNT + 1))
        FINDINGS+=('{"check":"root_access_keys","status":"PASS","detail":"No root access keys found"}')
    else
        log "FAIL: Root account has active access keys"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        FINDINGS+=('{"check":"root_access_keys","status":"FAIL","detail":"Root account has active access keys — immediate remediation required"}')
    fi
}

check_mfa_on_users() {
    log "Checking MFA enforcement on IAM users..."

    local users_without_mfa=0
    local user_list

    user_list=$(aws iam list-users --query 'Users[].UserName' --output text 2>/dev/null || echo "")

    for user in $user_list; do
        local mfa_devices
        mfa_devices=$(aws iam list-mfa-devices \
            --user-name "$user" \
            --query 'length(MFADevices)' \
            --output text 2>/dev/null || echo "0")

        if [[ "$mfa_devices" == "0" ]]; then
            users_without_mfa=$((users_without_mfa + 1))
            log "WARN: User $user does not have MFA enabled"
        fi
    done

    if [[ $users_without_mfa -eq 0 ]]; then
        log "PASS: All IAM users have MFA enabled"
        PASS_COUNT=$((PASS_COUNT + 1))
        FINDINGS+=('{"check":"mfa_enforcement","status":"PASS","detail":"All users have MFA enabled"}')
    else
        log "FAIL: $users_without_mfa user(s) without MFA"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        FINDINGS+=("{\"check\":\"mfa_enforcement\",\"status\":\"FAIL\",\"detail\":\"$users_without_mfa user(s) without MFA enabled\"}")
    fi
}

check_access_key_rotation() {
    log "Checking access key rotation (90-day policy)..."

    local old_keys=0
    local user_list

    user_list=$(aws iam list-users --query 'Users[].UserName' --output text 2>/dev/null || echo "")

    for user in $user_list; do
        local keys
        keys=$(aws iam list-access-keys \
            --user-name "$user" \
            --query 'AccessKeyMetadata[?Status==`Active`].[CreateDate]' \
            --output text 2>/dev/null || echo "")

        while IFS= read -r create_date; do
            if [[ -n "$create_date" ]]; then
                local create_timestamp
                create_timestamp=$(date -d "$create_date" +%s 2>/dev/null || date -j -f "%Y-%m-%dT%H:%M:%S+00:00" "$create_date" +%s 2>/dev/null || echo "0")
                local now_timestamp
                now_timestamp=$(date +%s)
                local age_days=$(( (now_timestamp - create_timestamp) / 86400 ))

                if [[ $age_days -gt 90 ]]; then
                    old_keys=$((old_keys + 1))
                    log "WARN: User $user has access key older than 90 days (${age_days} days)"
                fi
            fi
        done <<< "$keys"
    done

    if [[ $old_keys -eq 0 ]]; then
        log "PASS: All access keys are within 90-day rotation policy"
        PASS_COUNT=$((PASS_COUNT + 1))
        FINDINGS+=('{"check":"access_key_rotation","status":"PASS","detail":"All access keys rotated within 90 days"}')
    else
        log "FAIL: $old_keys access key(s) exceed 90-day rotation policy"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        FINDINGS+=("{\"check\":\"access_key_rotation\",\"status\":\"FAIL\",\"detail\":\"$old_keys access key(s) older than 90 days\"}")
    fi
}

check_password_policy() {
    log "Checking account password policy..."

    local policy
    policy=$(aws iam get-account-password-policy 2>/dev/null || echo "null")

    if [[ "$policy" == "null" ]]; then
        log "FAIL: No account password policy configured"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        FINDINGS+=('{"check":"password_policy","status":"FAIL","detail":"No account password policy configured"}')
        return
    fi

    local min_length
    min_length=$(echo "$policy" | python3 -c "import json,sys; p=json.load(sys.stdin).get('PasswordPolicy',{}); print(p.get('MinimumPasswordLength',0))" 2>/dev/null || echo "0")

    local require_uppercase
    require_uppercase=$(echo "$policy" | python3 -c "import json,sys; p=json.load(sys.stdin).get('PasswordPolicy',{}); print(p.get('RequireUppercaseCharacters',False))" 2>/dev/null || echo "False")

    if [[ "$min_length" -ge 14 && "$require_uppercase" == "True" ]]; then
        log "PASS: Password policy meets minimum requirements"
        PASS_COUNT=$((PASS_COUNT + 1))
        FINDINGS+=('{"check":"password_policy","status":"PASS","detail":"Password policy meets CIS benchmark requirements"}')
    else
        log "FAIL: Password policy does not meet requirements (min length: $min_length, require uppercase: $require_uppercase)"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        FINDINGS+=("{\"check\":\"password_policy\",\"status\":\"FAIL\",\"detail\":\"Password min length $min_length (need 14+), uppercase required: $require_uppercase\"}")
    fi
}

check_inline_policies() {
    log "Checking for inline policies on users and roles (should use managed policies)..."

    local inline_count=0

    local users
    users=$(aws iam list-users --query 'Users[].UserName' --output text 2>/dev/null || echo "")

    for user in $users; do
        local policies
        policies=$(aws iam list-user-policies \
            --user-name "$user" \
            --query 'length(PolicyNames)' \
            --output text 2>/dev/null || echo "0")

        if [[ "$policies" != "0" ]]; then
            inline_count=$((inline_count + 1))
            log "WARN: User $user has $policies inline policy/policies"
        fi
    done

    if [[ $inline_count -eq 0 ]]; then
        log "PASS: No inline policies found on users"
        PASS_COUNT=$((PASS_COUNT + 1))
        FINDINGS+=('{"check":"inline_policies","status":"PASS","detail":"No inline policies on IAM users"}')
    else
        log "FAIL: $inline_count user(s) have inline policies"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        FINDINGS+=("{\"check\":\"inline_policies\",\"status\":\"FAIL\",\"detail\":\"$inline_count user(s) have inline policies — convert to managed policies\"}")
    fi
}

check_admin_policies() {
    log "Checking for overly broad admin policies..."

    local admin_users=0

    local users
    users=$(aws iam list-users --query 'Users[].UserName' --output text 2>/dev/null || echo "")

    for user in $users; do
        local attached
        attached=$(aws iam list-attached-user-policies \
            --user-name "$user" \
            --query 'AttachedPolicies[?PolicyArn==`arn:aws:iam::aws:policy/AdministratorAccess`]' \
            --output text 2>/dev/null || echo "")

        if [[ -n "$attached" ]]; then
            admin_users=$((admin_users + 1))
            log "WARN: User $user has AdministratorAccess policy attached"
        fi
    done

    if [[ $admin_users -eq 0 ]]; then
        log "PASS: No users have AdministratorAccess policy"
        PASS_COUNT=$((PASS_COUNT + 1))
        FINDINGS+=('{"check":"admin_policy","status":"PASS","detail":"No users with AdministratorAccess policy"}')
    else
        log "FAIL: $admin_users user(s) have AdministratorAccess"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        FINDINGS+=("{\"check\":\"admin_policy\",\"status\":\"FAIL\",\"detail\":\"$admin_users user(s) have AdministratorAccess — apply least privilege\"}")
    fi
}

generate_report() {
    log "Generating JSON report: $REPORT_FILE"

    local findings_json
    findings_json=$(IFS=,; echo "[${FINDINGS[*]}]")

    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "unknown")

    cat > "$REPORT_FILE" <<EOF
{
  "report_type": "IAM Security Audit",
  "account_id": "${ACCOUNT_ID}",
  "region": "${REGION}",
  "generated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "summary": {
    "total_checks": $((PASS_COUNT + FAIL_COUNT)),
    "passed": ${PASS_COUNT},
    "failed": ${FAIL_COUNT},
    "compliance_score": "$(echo "scale=1; $PASS_COUNT * 100 / ($PASS_COUNT + $FAIL_COUNT + 1)" | bc)%"
  },
  "findings": ${findings_json}
}
EOF

    log "Report saved to: $REPORT_FILE"
    log "Summary: $PASS_COUNT passed, $FAIL_COUNT failed"
}

main() {
    log "=== IAM Security Audit — Hays Edinburgh DevOps POC ==="
    log "Region: $REGION"
    log ""

    check_root_account_usage
    check_mfa_on_users
    check_access_key_rotation
    check_password_policy
    check_inline_policies
    check_admin_policies

    generate_report

    log ""
    log "=== Audit Complete ==="
    log "Passed: $PASS_COUNT | Failed: $FAIL_COUNT"

    if [[ $FAIL_COUNT -gt 0 ]]; then
        exit 1
    fi
}

main "$@"
