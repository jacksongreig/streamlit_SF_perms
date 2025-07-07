from github import Github
from datetime import datetime

def raise_github_pr(filename: str, file_contents: str, token: str, repo_name: str) -> str:
    """
    Creates or updates a file in a GitHub repo and raises a PR.
    """
    g = Github(token)
    repo = g.get_repo(repo_name)
    base_branch = repo.default_branch

    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    clean_filename = filename.replace("/", "_").replace(".yaml", "")
    branch_name = f"feature/{clean_filename}_{timestamp}"

    base = repo.get_branch(base_branch)
    repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base.commit.sha)

    try:
        existing_file = repo.get_contents(filename, ref=branch_name)
        repo.update_file(
            path=filename,
            message=f"update: {filename}",
            content=file_contents,
            sha=existing_file.sha,
            branch=branch_name
        )
    except Exception:
        repo.create_file(
            path=filename,
            message=f"add: {filename}",
            content=file_contents,
            branch=branch_name
        )

    pr = repo.create_pull(
        title=f"feat: add or update {filename}",
        body="Auto-generated from the Snowflake IaC Assistant.",
        head=branch_name,
        base=base_branch
    )

    return pr.html_url