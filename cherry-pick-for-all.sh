#!/bin/bash

# 获取当前分支名称
current_branch=$(git rev-parse --abbrev-ref HEAD)

# 获取当前分支最新提交的 commit
latest_commit=$(git rev-parse HEAD)

# 获取所有分支列表
branches=$(git branch --format='%(refname:short)')

# 遍历每个分支
for branch in $branches
do
  # 排除当前分支
  if [[ $branch != $current_branch ]]; then
    # 切换到目标分支
    git checkout $branch
    
    # 应用最新提交的 commit
    git cherry-pick $latest_commit
  fi
done

# 切换回当前分支
git checkout $current_branch
