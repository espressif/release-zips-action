# This Justfile contains rules/targets/scripts/commands that are used when
# developing. Unlike a Makefile, running `just <cmd>` will always invoke
# that command. For more information, see https://github.com/casey/just

# ----------------------------------------------
# Allow passing arguments through to recipes
set positional-arguments

# Define ANSI color codes for terminal output
color_cyan := "\\033[36m"
color_blue := "\\033[34m"
color_red := "\\033[31m"
color_reset := "\\033[0m"

# Just help menu (type `just` to see the list of available commands)
[private]
@default:
    just --list

# Select just command interactively (only recipes without arguments)
[private]
@s:
    just --choose 2> /dev/null || \
        [ $? -eq 130 ] \
            && exit 0 \
        ; exit $?

# .Edit this Justfile
@edit-just:
    $EDITOR ./Justfile

# Install development environment
@env-install:
    pip install --require-virtualenv --upgrade pip
    pip install --require-virtualenv -e '.[dev]'
    pre-commit install

# Remove caches, builds, reports and other generated files
@env-clean:
    echo "⚠️  WARNING: This will {{color_red}}DELETE local builds, caches, reports and logs{{color_reset}} ⚠️"
    echo "\nType {{color_cyan}}'yes'{{color_reset}} to confirm if you want to proceed."
    read -r confirm && [[ "$confirm" == "yes" || "$confirm" == "YES" ]] \
        && rm -rf \
            dist \
            build \
            *.egg-info \
            **/__pycache__/ \
            .pytest_cache \
            .mypy_cache \
            .coverage* \
            .ruff_cache \
        || echo "Abort ..."
