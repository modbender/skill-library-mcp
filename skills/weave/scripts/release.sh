#!/usr/bin/env bash
set -euo pipefail

print_usage() {
  cat <<'EOF'
Usage:
  bash skills/weave/scripts/release.sh [options] <version> [changelog]

Examples:
  bash skills/weave/scripts/release.sh 0.1.1
  bash skills/weave/scripts/release.sh --create-git-tag 0.1.1
  bash skills/weave/scripts/release.sh --publish-clawhub 0.1.1 "Security-hardening release"
  bash skills/weave/scripts/release.sh --create-git-tag --publish-clawhub 0.1.1
  bash skills/weave/scripts/release.sh --run-quick-validate --skill-path-rel skills/weave 0.1.1

Options:
  --skill-path-rel <path>   Repo-relative skill path (default: skills/weave)
  --create-git-tag          Create local annotated git tag
  --no-create-git-tag       Explicitly disable tag creation
  --tag-prefix <prefix>     Git tag prefix (default: v)
  --publish-clawhub         Publish after checks
  --no-publish-clawhub      Explicitly disable publish
  --check-skills-sh         Run skills.sh listing verification (default: on)
  --no-check-skills-sh      Skip skills.sh listing verification
  --skills-install-smoke    Include skills.sh install smoke check
  --run-quick-validate      Run quick_validate.py when available
  --no-run-quick-validate   Explicitly disable quick validation
  -h, --help                Show this help message

Environment variables:
  SKILL_PATH_REL      Backward-compatible default for --skill-path-rel
  CREATE_GIT_TAG      Backward-compatible default for --create-git-tag
  TAG_PREFIX          Backward-compatible default for --tag-prefix
  PUBLISH_CLAWHUB     Backward-compatible default for --publish-clawhub
  CHECK_SKILLS_SH     Backward-compatible default for --check-skills-sh (default: 1)
  RUN_SKILLS_INSTALL_CHECK Backward-compatible default for --skills-install-smoke (default: 0)
  RUN_QUICK_VALIDATE  Backward-compatible default for --run-quick-validate
EOF
}

skill_path_rel="${SKILL_PATH_REL:-skills/weave}"
create_git_tag="${CREATE_GIT_TAG:-0}"
publish_clawhub="${PUBLISH_CLAWHUB:-0}"
check_skills_sh="${CHECK_SKILLS_SH:-1}"
run_skills_install_check="${RUN_SKILLS_INSTALL_CHECK:-0}"
run_quick_validate="${RUN_QUICK_VALIDATE:-0}"
tag_prefix="${TAG_PREFIX:-v}"

positionals=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      print_usage
      exit 0
      ;;
    --skill-path-rel)
      if [[ $# -lt 2 ]]; then
        echo "Error: --skill-path-rel requires a value." >&2
        exit 1
      fi
      skill_path_rel="$2"
      shift 2
      ;;
    --create-git-tag)
      create_git_tag=1
      shift
      ;;
    --no-create-git-tag)
      create_git_tag=0
      shift
      ;;
    --tag-prefix)
      if [[ $# -lt 2 ]]; then
        echo "Error: --tag-prefix requires a value." >&2
        exit 1
      fi
      tag_prefix="$2"
      shift 2
      ;;
    --publish-clawhub)
      publish_clawhub=1
      shift
      ;;
    --no-publish-clawhub)
      publish_clawhub=0
      shift
      ;;
    --check-skills-sh)
      check_skills_sh=1
      shift
      ;;
    --no-check-skills-sh)
      check_skills_sh=0
      shift
      ;;
    --skills-install-smoke)
      run_skills_install_check=1
      shift
      ;;
    --run-quick-validate)
      run_quick_validate=1
      shift
      ;;
    --no-run-quick-validate)
      run_quick_validate=0
      shift
      ;;
    --)
      shift
      while [[ $# -gt 0 ]]; do
        positionals+=("$1")
        shift
      done
      ;;
    -*)
      echo "Error: unknown option: $1" >&2
      print_usage
      exit 1
      ;;
    *)
      positionals+=("$1")
      shift
      ;;
  esac
done

if [[ ${#positionals[@]} -lt 1 || ${#positionals[@]} -gt 2 ]]; then
  print_usage
  exit 1
fi

version="${positionals[0]}"
default_changelog="weave skill ${version}: security-hardening install guidance, release automation scripts, and compliance checks."
changelog="${positionals[1]:-${default_changelog}}"

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "${script_dir}/../../.." && pwd)"

if [[ ! "${version}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Error: version must be semver (e.g. 0.1.1)." >&2
  exit 1
fi

(
  cd "${repo_root}"

  echo "Step 1/5: Security checks"
  bash "${skill_path_rel}/scripts/security-check.sh" "${skill_path_rel}"

  if [[ "${run_quick_validate}" == "1" ]]; then
    echo "Step 2/5: Quick validate (optional)"
    validator="${HOME}/.codex/skills/.system/skill-creator/scripts/quick_validate.py"
    if [[ -f "${validator}" ]]; then
      if python3 -c 'import yaml' >/dev/null 2>&1; then
        python3 "${validator}" "${skill_path_rel}"
      else
        echo "Skipping quick_validate.py: PyYAML not available."
      fi
    else
      echo "Skipping quick_validate.py: validator script not found."
    fi
  else
    echo "Step 2/5: Quick validate skipped (--run-quick-validate not set)"
  fi

  if [[ "${create_git_tag}" == "1" ]]; then
    echo "Step 3/5: Create local git tag"
    tag_name="${tag_prefix}${version}"
    if git rev-parse -q --verify "refs/tags/${tag_name}" >/dev/null; then
      echo "Error: tag already exists: ${tag_name}" >&2
      exit 1
    fi
    git tag -a "${tag_name}" -m "weave skill ${version}"
    echo "Created local tag: ${tag_name}"
    echo "Push with: git push origin ${tag_name}"
  else
    echo "Step 3/5: Git tag skipped (--create-git-tag not set)"
  fi

  if [[ "${check_skills_sh}" == "1" ]]; then
    echo "Step 4/5: skills.sh listing verification"
    if [[ "${run_skills_install_check}" == "1" ]]; then
      RUN_INSTALL_CHECK=1 bash "${skill_path_rel}/scripts/check-skills-sh.sh"
    else
      bash "${skill_path_rel}/scripts/check-skills-sh.sh"
    fi
  else
    echo "Step 4/5: skills.sh verification skipped (--no-check-skills-sh set)"
  fi

  if [[ "${publish_clawhub}" == "1" ]]; then
    echo "Step 5/5: Publish to Clawhub"
    bash "${skill_path_rel}/scripts/publish-clawhub.sh" "${version}" "${changelog}"
  else
    echo "Step 5/5: Clawhub publish skipped (--publish-clawhub not set)"
    echo "Publish with: bash ${skill_path_rel}/scripts/publish-clawhub.sh ${version} \"${changelog}\""
  fi
)
