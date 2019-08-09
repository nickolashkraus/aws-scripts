# -*- coding: utf-8 -*-
"""
Utility for deleting IAM users and associated resources.

Unlike the AWS Management Console, when you delete a user programmatically,
you must delete the items attached to the user manually, or the deletion fails.
For more information, see Deleting an IAM User:

https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_manage.html#id_users_deleting_cli

Before attempting to delete a user, remove the following items:

  * Password (DeleteLoginProfile)
    - delete-login-profile --user-name <user-name>
    - delete_login_profile(UserName=<user_name>)

  * Access Keys (DeleteAccessKey)
    - delete-access-key --access-key-id <access-key-id>
    - delete_access_key(AccessKeyId=<access_key_id>)

  * Signing Certificate (DeleteSigningCertificate)
    - delete-signing-certificate --certificate-id <certificate-id>
    - delete_signing_certificate(CertificateId=<certificate_id>)

  * SSH Public Key (DeleteSSHPublicKey)
    - delete-ssh-public-key --user-name <user-name> --ssh-public-key-id <ssh-public-key-id>
    - delete_ssh_public_key(UserName=<user_name>, SSHPublicKeyId=<ssh_public_key_id>)

  * Git Credentials (DeleteServiceSpecificCredential)
    - delete-service-specific-credential --service-specific-credential-id <service-specific-credential-id>
    - delete_service_specific_credentials(ServiceSpecificCredentialId=<service_specific_credential_id>)

  * Multi-factor Authentication (MFA) Device (DeactivateMFADevice, DeleteVirtualMFADevice)
    - deactivate-mfa-device --user-name <user-name> --serial-number <serial-number>
    - deactivate_mfa_device(UserName=<user_name>, SerialNumber=<serial_number>)
    - delete-virtual-mfa-device --serial_number <serial-number>
    - delete_virtual_mfa_device(SerialNumber=<serial_number>)

  * Inline Policies (DeleteUserPolicy)
    - delete-user-policy --user-name <user-name> --policy-name <policy-name>
    - delete_user_policy(UserName=<user_name>, PolicyName=<policy_name>)

  * Attached Managed Policies (DetachUserPolicy)
    - detach-user-policy --user-name <user-name> --policy-arn <policy-arn>
    - detach_user_policy(UserName=<user_name>, PolicyArn=<policy_arn>)

  * Group Memberships (RemoveUserFromGroup)
    - remove-user-from-group --user-name <user-name> --group-name <group-name>
    - remove_user_from_group(UserName=<user_name>, GroupName=<group_name>)

Finally, delete the user:

  * Delete User (DeleteUser)
   - delete-user --user-name <user-name>
   - delete_user(UserName=<user_name>)
"""

import boto3
import click

import logging

# configure Logger instance
logger = logging.getLogger()
f = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh = logging.FileHandler('logs.txt')
fh.setLevel(logging.WARNING)
fh.setFormatter(f)
logger.addHandler(fh)


@click.command()
@click.option('--user-name', default=None, help='Name of the user.')
@click.option('--dry-run',
              is_flag=True,
              help='Echo AWS CLI commands without executing them.')
def main(user_name: str, dry_run: bool) -> None:
    client = boto3.client('iam')

    access_key_ids = \
        [x['AccessKeyId']
         for x in client.list_access_keys(
             UserName=user_name)['AccessKeyMetadata']]
    certificate_ids = \
        [x['CertificateId']
         for x in client.list_signing_certificates(
             UserName=user_name)['Certificates']]
    ssh_public_key_ids = \
        [x['SSHPublicKeyId']
         for x in client.list_ssh_public_keys(
             UserName=user_name)['SSHPublicKeys']]
    service_specific_credential_ids = \
        [x['ServiceSpecificCredentialId']
         for x in client.list_service_specific_credentials(
             UserName=user_name)['ServiceSpecificCredentials']]
    serial_numbers = \
        [x['SerialNumber']
         for x in client.list_mfa_devices(
             UserName=user_name)['MFADevices']]
    policy_names = \
        [x
         for x in client.list_user_policies(
             UserName=user_name)['PolicyNames']]
    policy_arns = \
        [x['PolicyArn']
         for x in client.list_attached_user_policies(
             UserName=user_name)['AttachedPolicies']]
    group_names = \
        [x['GroupName']
         for x in client.list_groups_for_user(
             UserName=user_name)['Groups']]

    if dry_run:
        print('aws iam delete-login-profile --user-name {}'.format(user_name))
        print('aws iam list-access-keys --user-name {}'.format(user_name))
        for access_key_id in access_key_ids:
            print('aws iam delete-access-key --access-key-id {}'.format(
                access_key_id))
        print('aws iam list-signing-certificates --user-name {}'.format(
            user_name))
        for certificate_id in certificate_ids:
            print('aws iam delete-signing-certificate --certificate-id {}'.
                  format(certificate_id))
        print('aws iam list-ssh-public-keys --user-name {}'.format(user_name))
        for ssh_public_key_id in ssh_public_key_ids:
            print(
                'aws iam delete-ssh-public-key --user-name --ssh-public-key-id {}'
                .format(user_name, ssh_public_key_id))
        print(
            'aws iam list-service-specific-credentials --user-name {}'.format(
                user_name))
        for service_specific_credential_id in service_specific_credential_ids:
            print(
                'aws iam delete-service-specific-credential --service-specific-credential-id {}'
                .format(service_specific_credential_id))
        print('aws iam list-mfa-devices --user-name {}'.format(user_name))
        for serial_number in serial_numbers:
            print(
                'aws iam deactivate-mfa-device --user-name {} --serial-number {}'
                .format(user_name, serial_number))
            print(
                'aws iam delete-virtual-mfa-device --serial-number {}'.format(
                    serial_number))
        print('aws iam list-user-policy --user-name {}'.format(user_name))
        for policy_name in policy_names:
            print('aws iam delete-user-policy --user-name {} --policy-name {}'.
                  format(user_name, policy_name))
        print('aws iam list-attached-user-policies --user-name {}'.format(
            user_name))
        for policy_arn in policy_arns:
            print('aws iam detach-user-policy --user-name {} --policy-arn {}'.
                  format(user_name, policy_arn))
        print('aws iam list-groups-for-user --user-name {}'.format(user_name))
        for group_name in group_names:
            print(
                'aws iam remove-user-from-group --user-name {} --group-name {}'
                .format(user_name, group_name))
        print('aws iam delete-user --user-name {}'.format(user_name))

    else:
        client.delete_login_profile(UserName=user_name)
        for access_key_id in access_key_ids:
            client.delete_access_key(AccessKeyId=access_key_id)
        for certificate_id in certificate_ids:
            client.delete_signing_certificate(CertificateId=certificate_id)
        for ssh_public_key_id in ssh_public_key_ids:
            client.delete_ssh_public_key(SSHPublicKeyId=ssh_public_key_id)
        for service_specific_credential_id in service_specific_credential_ids:
            client.delete_service_specific_credential(
                ServiceSpecificCredentialId=service_specific_credential_id)
        for serial_number in serial_numbers:
            client.deactivate_mfa_device(UserName=user_name,
                                         SerialNumber=serial_number)
            client.delete_virtual_mfa_device(SerialNumber=serial_number)
        for policy_name in policy_names:
            client.delete_user_policy(UserName=user_name,
                                      PolicyName=policy_name)
        for policy_arn in policy_arns:
            client.detach_user_policy(UserName=user_name, PolicyArn=policy_arn)
        for group_name in group_names:
            client.remove_user_from_group(UserName=user_name,
                                          GroupName=group_name)
        client.delete_user(UserName=user_name)


if __name__ == '__main__':
    main()
