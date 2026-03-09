# Security Response Note

## Incident summary

A real `.env` file with secret values was previously present in the working tree of this repository.

This repository now ships only `.env.example`, and the real `.env` file has been removed from the current tree.

## Important operational note

Removing the file from the current tree is not sufficient if the repository history has already been shared or published.

If the tracked secret was ever pushed to a remote, the maintainer should assume it may have been exposed.

## Maintainer actions

1. Revoke or rotate the affected key manually with the upstream provider.
2. Review remote Git history and any forks or mirrors that may still contain the secret.
3. Consider history rewriting or secret-scanning remediation if the repository has already been published.
4. Replace local usage with `.env.example` plus fresh credentials.
5. Re-run public-safety checks before the next release.

## What this note does not claim

- It does not claim that rotation has already happened.
- It does not claim that history has already been cleaned.
- It does not print or preserve the original secret.
