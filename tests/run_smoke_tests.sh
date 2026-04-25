#!/usr/bin/env bash
#
# Smoke-test the structural validator against the example recon outputs.
# Run from the repo root or from tests/. Exits non-zero if any check fails.

set -euo pipefail

# Resolve repo root regardless of where the script is invoked from
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${script_dir}/.." && pwd)"
cd "${repo_root}"

failed=0

check() {
    local file="$1"
    shift
    if ! python3 tests/check_recon_structure.py "${file}" "$@"; then
        failed=1
    fi
}

check "examples/explore-example.md" --mode explore
check "examples/focus-example.md" --mode focus

# Validator contract tests — assert the validator catches malformed inputs,
# not just that the example files happen to pass.
if ! python3 tests/test_validator_contract.py; then
    failed=1
fi

if [[ $failed -eq 1 ]]; then
    echo
    echo "Smoke tests failed. Either the example files no longer match the structural contract, or the validator's contract has regressed."
    exit 1
fi

echo
echo "All smoke tests passed."
