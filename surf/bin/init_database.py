import os
import subprocess


def execute_sql_files(base_dir, database):
    sql_dir = os.path.join(base_dir, 'sql')
    command = f'sudo -u postgres psql -d {database} -f \"{os.path.join(sql_dir, "new_surf_sql.sql")}\"'
    try:
        subprocess.run(command, shell=True, check=True)
        print("database init executed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error executing new_surf_sql.sql: {e}")

    sql_dir = os.path.join(base_dir, 'tables')

    # 检查目录是否存在
    if not os.path.exists(sql_dir):
        print(f"Directory {sql_dir} does not exist.")
        return

    # 遍历并执行所有的.sql文件
    for filename in os.listdir(sql_dir):
        if filename.endswith(".sql"):
            filepath = os.path.join(sql_dir, filename)
            print(f"Executing {filepath}...")

            # 构建并执行命令
            command = f"sudo -u postgres psql -d {database} -f \"{filepath}\""
            try:
                subprocess.run(command, shell=True, check=True)
                print(f"{filename} executed successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Error executing {filename}: {e}")


if __name__ == "__main__":
    # 获取当前脚本的路径
    current_script_dir = os.path.dirname(os.path.abspath(__file__))

    # 获取上级的上级目录
    base_directory = os.path.abspath(os.path.join(current_script_dir, '..', '..'))

    # 指定数据库名称
    db_name = "surf"

    # 执行SQL文件
    execute_sql_files(base_directory, db_name)
