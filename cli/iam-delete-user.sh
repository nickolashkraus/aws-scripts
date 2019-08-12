#!/usr/bin/env bash

USERS=()

for user in "${USERS[@]}"; do

  # delete the password for the specified IAM user
  if aws iam get-login-profile --user-name "${user}" > /dev/null 2>&1; then
    aws iam delete-login-profile --user-name "${user}"
  fi

  # delete the access key pair associated with the specified IAM user
  for key in $(aws iam list-access-keys --user-name "${user}" | jq -r '.AccessKeyMetadata | map(.AccessKeyId) | .[]'); do
    aws iam delete-access-key --user-name "${user}" --access-key-id "${key}"
  done

  # delete a signing certificate associated with the specified IAM user
  for id in $(aws iam list-signing-certificates --user-name "${user}" | jq -r '.Certificates | map(.CertificateId) | .[]'); do
    aws iam delete-signing-certificate --user-name "${user}" --certificate-id "${id}"
  done

  # delete the specified SSH public key
  for key in $(aws iam list-ssh-public-keys --user-name "${user}" | jq -r '.SSHPublicKeys | map(.SSHPublicKeyId) | .[]'); do
    aws iam delete-ssh-public-key --user-name "${user}" --ssh-public-key-id "${key}"
  done

  # delete the specified service-specific credential
  for id in $(aws iam list-service-specific-credentials --user-name "${user}" | jq -r '.ServiceSpecificCredentials| map(.ServiceSpecificCredentialId) | .[]'); do
    aws iam delete-service-specific-credential --user-name "${user}" --service-specific-credential-id "${id}"
  done

  for mfa in $(aws iam list-mfa-devices --user-name "${user}" | jq -r '.MFADevices | map(.SerialNumber) | .[]'); do
    # deactivate the specified MFA device and remove it from association with the specified IAM user
    # virtual MFA devices have to be deactivated before deletion; physical devices just need to be deactivated
    aws iam deactivate-mfa-device --user-name "${user}" --serial-number "${mfa}"
    # delete a virtual MFA device
    # if this fails, assume it was a physical device that didn't need to be deleted (and continue on)
    aws iam delete-virtual-mfa-device --serial-number "${mfa}" || true
  done

  # delete the specified inline policy that is embedded in the specified IAM user
  for policy in $(aws iam list-user-policies --user-name "${user}" | jq -r '.PolicyNames | .[]'); do
    aws iam delete-user-policy --user-name "${user}" --policy-name "${policy}"
  done

  # remove the specified managed policy from the specified IAM user
  for policy in $(aws iam list-attached-user-policies --user-name "${user}" | jq -r '.AttachedPolicies | map(.PolicyArn) | .[]'); do
    aws iam detach-user-policy --user-name "${user}" --policy-arn "${policy}"
  done

  # remove the specified user from the specified group
  for group in $(aws iam list-groups-for-user --user-name "${user}" | jq -r '.Groups | map(.GroupName) | .[]'); do
    aws iam remove-user-from-group --user-name "${user}" --group-name "${group}"
  done

  # delete the specified IAM user
  aws iam delete-user --user-name "${user}"

done
