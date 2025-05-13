# Release zips

If you need to distribute source zip files containing a recursively cloned working directory of your repo (such as we do for ESP-IDF), then this action can automatically create one and attach it to a draft release whenever a matching tag is pushed.

The difference between this zip file and the automatic zip file that GitHub allows you to download from any tag or release is:

- This zip file is a recursive clone that includes all submodules.
- This zip file is a valid Git working directory

## Creating a Release

If a Release already exists for the given tag, then the zip file is attached to it. Otherwise, a placeholder Draft release is created and the zip file is attached to that.

If the tag contains `-` then a new Draft is marked as Pre-release and this is also mentioned in the title. The naming scheme for a new draft is based on ESP-IDF, and is `$RELEASE_PROJECT_NAME [Pre-release|Release] $TAG`. Both these things can be edited before publishing the new release.

## Inputs

| Name                   | Description                                                                 | Required | Default         |
| ---------------------- | --------------------------------------------------------------------------- | -------- | --------------- |
| `github_token`         | GitHub token to authenticate release and clone operations                   | Yes      | –               |
| `release_project_name` | Project name used in release title                                          | No       | repository name |
| `git_extra_args`       | Extra arguments passed to `git clone` (e.g. `--shallow-since="1 year ago"`) | No       | `""`            |

## Example Workflow yaml file

```yml
name: Create recursive zip file for release

on:
  push:
    tags:
      - v*

jobs:
  release_zips:
    name: Create release zip files
    runs-on: ubuntu-24.04
    steps:
      - name: Create a recursive clone source zip for a Release
        uses: espressif/release-zips-action@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          release_project_name: ESP-IDF
          git_extra_args: --shallow-since="1 year ago"
```

- Note the `tags` filter for `push`, this limits the tag patterns for which a zip file should be created.
- `release_project_name` is the name that will be used in the Draft Release title. The format is: `$RELEASE_PROJECT_NAME [Pre-release|Release] $TAG`
- `github_token` is used to authenticate the GitHub API (for creating releases) and to clone private submodules if
  needed. The token is not stored in the resulting working directory.
- `git_extra_args` is passed to `git clone`, so you can use it to limit the history of the clone. This is useful if you
  have a large repo and want to limit the size of the zip file. For example, `--shallow-since="1 year ago"` will only
  include commits from the last year.
