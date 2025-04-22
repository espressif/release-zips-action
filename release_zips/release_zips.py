#!/usr/bin/env python3

import os
import subprocess

from github import Github
from github import GithubException


def main():
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

    print(f'Cloning {git_url} (tag: {tag}) into {directory}...')
    subprocess.run(['git', 'clone', '--recursive', '--branch', tag, git_url, directory], check=True)

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
