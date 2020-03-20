#!/usr/bin/env bash

USERS=()

for user in "${USERS[@]}"; do
  # retrieve information about when the specified access key was last used.
  for key in $(aws iam list-access-keys --user-name "${user}" | jq -r '.AccessKeyMetadata | map(.AccessKeyId) | .[]'); do
    echo User: "${user}"
    echo Access key: "${key}" last used on $(aws iam get-access-key-last-used --access-key-id "${key}" | jq -r '.AccessKeyLastUsed.LastUsedDate')
    echo
  done
done
