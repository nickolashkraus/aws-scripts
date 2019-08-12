# -*- coding: utf-8 -*-
"""
Utility for auditing IAM users and groups.
"""

import boto3
import click

import logging

from datetime import datetime

# configure Logger instance
logger = logging.getLogger()
f = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh = logging.FileHandler('logs.txt')
fh.setLevel(logging.WARNING)
fh.setFormatter(f)
logger.addHandler(fh)

KEYS_TO_REMOVE = ['IsTruncated', 'Marker', 'ResponseMetadata']


class Base:
    def __init__(self, **kwargs) -> None:
        self.__dict__.update(kwargs)

    def __repr__(self):
        return str(self._to_dict())

    def _to_dict(self):
        ret = {}
        for k, v in self.__dict__.items():
            if not v:
                ret[k] = v
            elif isinstance(v, Base):
                ret[k] = v._to_dict()
            elif isinstance(v, dict):
                ret[k] = dict(v)
            elif isinstance(v, list):
                ret[k] = []
                for i in v:
                    if not v:
                        ret[k].append(i)
                    elif isinstance(i, Base):
                        ret[k].append(i._to_dict())
                    elif isinstance(v, dict):
                        ret[k].append(dict(i))
                    else:
                        ret[k].append(i)
            else:
                ret[k] = v
        return ret


class User(Base):
    def __init__(self, **kwargs) -> None:
        super(User, self).__init__(**kwargs)

    @classmethod
    def get_user(cls, user_name: str) -> dict:
        """
        Retrieves information about the IAM user and returns a User object.

        Information includes the following:
          - User Name (UserName)
          - User ID (UserId)
          - ARN (Arn)
          - Create Date (CreateDate)
          - Access Key Last Used (AccessKeyLastUsed)
          - Attached Policies (AttachedPolicies)
              - Policy ARN (PolicyArn)
              - Policy Name (PolicyName)
          - Policies (PolicyNames)
          - Groups (Groups)
             - Group Name (GroupName)
             - ARN (Arn)
             - Create Date (CreateDate)
        """
        user = {'UserName': user_name}
        resp = {}

        client = boto3.client('iam')
        resp = client.get_user(UserName=user_name)
        user.update({'UserId': resp['User']['UserId']})
        user.update({'Arn': resp['User']['Arn']})
        user.update({'CreateDate': resp['User']['CreateDate']})

        try:
            resp = client.get_access_key_last_used(AccessKeyId=user['UserId'])
            user.update({
                'AccessKeyLastUsed':
                resp['AccessKeyLastUsed']['LastUsedDate']
            })
        except Exception as e:
            logger.warning(e)

        attached_policies = []
        resp = client.list_attached_user_policies(UserName=user_name)
        for attached_policy in resp['AttachedPolicies']:
            attached_policies.append(AttachedPolicy(**attached_policy))
        user.update({'AttachedPolicies': attached_policies})

        policies = []
        resp = client.list_user_policies(UserName=user_name)
        for policy in resp['PolicyNames']:
            policies.append(policy)
        user.update({'Policies': policies})

        groups = []
        resp = client.list_groups_for_user(UserName=user_name)
        for group in resp['Groups']:
            groups.append(group['GroupName'])
        user.update({'Groups': groups})

        return cls(**user)

    @staticmethod
    def remove_keys(d: dict, keys: list) -> dict:
        """
        Remove keys (keys) from dictionary (d).
        """
        ret = {}
        for k, v in d.items():
            if k in keys:
                continue
            elif isinstance(v, dict):
                ret[k] = User.remove_keys(v, keys)
            else:
                ret[k] = v
        return ret

    @staticmethod
    def strftime(d: dict) -> str:
        """
        Convert datetime objects to strings for dictionary (d).
        """
        for k, v in d.items():
            if isinstance(v, dict):
                d[k] = User.strftime(v)
            elif isinstance(v, datetime):
                d[k] = d[k].strftime('%Y-%m-%dT%H:%M:%SZ')
        return d


class AttachedPolicy(Base):
    def __init__(self, **kwargs) -> None:
        super(AttachedPolicy, self).__init__(**kwargs)


class Group(Base):
    def __init__(self, **kwargs) -> None:
        super(Group, self).__init__(**kwargs)

    @classmethod
    def get_group(cls, group_name: str) -> dict:
        """
        Retrieves information about the IAM group and returns a Group object.

        Information includes the following:
          - Group Name (GroupName)
          - ARN (Arn)
          - Create Date (CreateDate)
          - Attached Policies (AttachedPolicies)
              - Policy Arn
              - Policy Name
          - Policies (PolicyNames)
          - Users (Users)
             - User Name (UserName)
        """
        group = {'GroupName': group_name}
        resp = {}

        client = boto3.client('iam')
        resp = client.get_group(GroupName=group_name)
        group.update({'Arn': resp['Group']['Arn']})
        group.update({'CreateDate': resp['Group']['CreateDate']})

        users = []
        for user in resp['Users']:
            users.append(user['UserName'])
        group.update({'Users': users})

        attached_policies = []
        resp = client.list_attached_group_policies(GroupName=group_name)
        for attached_policy in resp['AttachedPolicies']:
            attached_policies.append(AttachedPolicy(**attached_policy))
        group.update({'AttachedPolicies': attached_policies})

        policies = []
        resp = client.list_group_policies(GroupName=group_name)
        for policy in resp['PolicyNames']:
            policies.append(policy)
        group.update({'Policies': policies})

        return cls(**group)


@click.command()
@click.option('--user-name', default=None, help='Name of the user.')
@click.option('--group-name', default=None, help='Name of the group.')
def main(user_name: str, group_name: str) -> None:
    if user_name:
        user = User.get_user(user_name)
        print(user)

    if group_name:
        group = Group.get_group(group_name)
        print(group)


if __name__ == '__main__':
    main()
