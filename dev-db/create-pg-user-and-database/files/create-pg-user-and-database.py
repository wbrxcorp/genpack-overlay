#!/usr/bin/python3
# -*- coding: utf-8 -*-
import subprocess,argparse

import psycopg # dev-python/psycopg
from psycopg import sql

def setup_db(username, dbname, password = None, db_params=None) -> bool:
    """
    PostgreSQLのユーザーとデータベースを作成する関数
    :param username: 作成するユーザー名
    :param dbname: 作成するデータベース名
    :param password: ユーザーのパスワード（オプション）
    :param db_params: データベース接続パラメータ（オプション）
    :return: データベースが新規作成された場合はTrue、既存の場合はFalse
    """
    if db_params is None:
        db_params = {
            "dbname": "postgres",
            "user": "postgres"
        }
    
    db_params["autocommit"] = True  # 自動コミットを有効にする

    database_created = False

    try:
        # 接続（withで自動クローズ）
        with psycopg.connect(**db_params) as conn:
            # カーソル（withで自動クローズ）
            with conn.cursor() as cur:
                # ユーザー作成
                cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (username,))
                if not cur.fetchone():
                    if password:
                        cur.execute(sql.SQL("CREATE ROLE {user} LOGIN PASSWORD {password}").format(
                            user=sql.Identifier(username),
                            password=sql.Literal(password)
                        ))
                    else:
                        cur.execute(sql.SQL("CREATE ROLE {} LOGIN").format(sql.Identifier(username)))
                    print(f"User '{username}' created.")
                else:
                    print(f"User '{username}' already exists.")

                # データベース作成（オーナー指定）
                cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
                if not cur.fetchone():
                    cur.execute(sql.SQL("CREATE DATABASE {} OWNER {}").format(sql.Identifier(dbname), sql.Identifier(username)))
                    print(f"Database '{dbname}' created with owner '{username}'.")
                    database_created = True
                else:
                    print(f"Database '{dbname}' already exists.")

    except Exception as e:
        print(f"Error: {e}")
        exit(1)
    return database_created

def run_command(command):
    """
    指定されたコマンドを実行する関数
    :param command: 実行するコマンド
    """
    try:
        subprocess.run(command, check=True)
        print(f"Command '{' '.join(command)}' executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing command '{' '.join(command)}': {e}")
        exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a PostgreSQL user and database.")
    parser.add_argument("username", help="The PostgreSQL username to create.")
    parser.add_argument("dbname", help="The PostgreSQL database name to create.")
    parser.add_argument("init_command", nargs='*', default=None, help="Optional commands to run after database creation.")
    parser.add_argument("--password", help="The password for the PostgreSQL user.", default=None)
    args = parser.parse_args()
    database_created = setup_db(args.username, args.dbname, args.password)
    if args.init_command is not None and len(args.init_command) > 0 and database_created:
        print("Running initialization command...")
        run_command(args.init_command)
