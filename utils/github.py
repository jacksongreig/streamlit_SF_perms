from github import Github
from datetime import datetime
from snowflake.snowpark.context import get_active_session

def raise_github_pr(filename: str, file_contents: str, token: str, repo_name: str):
    session = get_active_session()
    snowflake_user = session.sql("SELECT CURRENT_USER()").collect()[0][0]

    g = Github(token)
    repo = g.get_repo(repo_name)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    branch_name = f"iac-update-{filename.replace('/', '_').replace('.', '_')}-{timestamp}"
    commit_message = f"update: {filename}"

    default_branch = repo.default_branch
    source = repo.get_branch(default_branch)
    repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=source.commit.sha)

    try:
        contents = repo.get_contents(filename, ref=default_branch)
        repo.update_file(
            path=filename,
            message=commit_message,
            content=file_contents,
            sha=contents.sha,
            branch=branch_name,
        )
    except Exception:
        repo.create_file(
            path=filename,
            message=f"add: {filename}",
            content=file_contents,
            branch=branch_name,
        )

    pr = repo.create_pull(
        title=f"[IaC] Update: {filename}",
        body=f"Generated by Snowflake user: `{snowflake_user}` via the IaC Assistant.",
        head=branch_name,
        base=default_branch,
    )
    return pr.html_url
