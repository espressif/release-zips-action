#!/usr/bin/env python3

import argparse
import os
import shlex
import subprocess

from github import Github
from github import GithubException

# Define an allowlist of allowed git arguments
ALLOWED_GIT_ARGS = ['--shallow-since']


def validate_git_args(extra_args):
    parsed_args = shlex.split(extra_args)
    for arg in parsed_args:
        # Check if the argument starts with an allowed prefix
        if not any(arg.startswith(allowed) for allowed in ALLOWED_GIT_ARGS):
            raise ValueError(f'Invalid git argument: {arg}')
    return parsed_args


def main():
    git_extra_args = os.environ.get("INPUT_GIT_EXTRA_ARGS")
    ref = os.environ.get('GITHUB_REF')
    if not ref:
        raise SystemExit('Not an event based on a push. Workflow configuration is wrong?')

    ref_prefix = 'refs/tags/'
    if not ref.startswith(ref_prefix):
        raise SystemExit(f'Ref {ref} is not a tag. Workflow configuration is wrong?')

    tag = ref.removeprefix(ref_prefix)
    github_actor = os.environ['GITHUB_ACTOR']
    github_token = os.environ['GITHUB_TOKEN']
    github_repo = os.environ['GITHUB_REPOSITORY']

    print('Connecting to GitHub...')
    github = Github(github_token)
    repo = github.get_repo(github_repo)

    if repo.private:
        # Configure Git credentials for private repositories
        subprocess.run(
            ['git', 'config', '--global', 'credential.https://github.com.username', github_actor], check=True
        )
        helper_cmd = '!f() { test "$1" = get && echo "password=$GITHUB_TOKEN"; }; f'
        subprocess.run(['git', 'config', '--global', 'credential.https://github.com.helper', helper_cmd], check=True)

    git_url = f'https://github.com/{github_repo}.git'
    repo_name = github_repo.split('/')[1]
    directory = f'{repo_name}-{tag}'

    clone_cmd = ['git', 'clone', '--recursive', '--branch', tag]
    if git_extra_args:
        try:
            validated_args = validate_git_args(git_extra_args)
            clone_cmd.extend(validated_args)
        except ValueError as e:
            raise SystemExit(str(e)) from e
    clone_cmd.extend([git_url, directory])
    print(f'Cloning {git_url} (tag: {tag}) into {directory}...')
    print(f'Running: {" ".join(clone_cmd)}')
    subprocess.run(clone_cmd, check=True)

    zipfile = f'{directory}.zip'
    print(f'Creating zip archive {zipfile}...')
    subprocess.run(['/usr/bin/7z', 'a', '-mx=9', '-tzip', zipfile, directory], check=True)

    try:
        release = repo.get_release(tag)
        print('Existing release found...')
        if any(asset.name == zipfile for asset in release.get_assets()):
            raise SystemExit(
                f'A release for tag {tag} already exists and has a zip file {zipfile}. Workflow configured wrong?'
            )
    except GithubException:
        print('Creating release...')
        is_prerelease = '-' in tag  # Tags like vX.Y-something are pre-releases
        release_repo_name = os.environ.get('RELEASE_PROJECT_NAME', repo_name)
        name = f'{release_repo_name} {"Pre-release" if is_prerelease else "Release"} {tag}'
        release = repo.create_git_release(tag, name, '(Draft created by Action)', draft=True, prerelease=is_prerelease)

    print('Uploading zipfile to release...')
    release.upload_asset(zipfile)

    print(f'Release URL is {release.html_url}')


if __name__ == '__main__':
    main()
