# syntax=docker/dockerfile:1
FROM python:3.13-slim AS base

# Pythonのバッファリング無効化（ログの即時出力）
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# システムパッケージの更新
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# ユーザー作成
RUN adduser --disabled-password --gecos '' melon
ENV HOME=/home/melon
WORKDIR ${HOME}

# uvのインストール（ROOTユーザーで実行）
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 依存関係定義ファイルをコピー（キャッシュ効率化）
COPY --chown=melon:melon pyproject.toml uv.lock ./

# ユーザー切り替え
USER melon

# 依存関係のみ先にインストール（uv.lockから再現可能にインストール）
RUN uv sync --frozen --no-install-project --no-dev

# アプリケーションファイルをコピー
COPY --chown=melon:melon src ./src

# アプリケーション本体をインストール
RUN uv sync --frozen --no-dev

# ヘルスチェック用のシンプルなスクリプト
RUN echo '#!/bin/sh\npgrep -f "python.*dinsights" > /dev/null' > /home/melon/healthcheck.sh && \
    chmod +x /home/melon/healthcheck.sh

# uvの実行環境でPythonを起動
CMD ["uv", "run", "--frozen", "python", "-m", "dinsights"]
