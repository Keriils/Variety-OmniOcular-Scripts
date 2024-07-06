import os
import zipfile
import shutil
import subprocess


""" 打包release的脚本 根据Git标签或者最新提交的哈希值作为版本号 """


def get_latest_git_tag_or_commit():
    """
    获取最近的Git标签或最新提交的哈希值作为版本号。
    """
    try:
        tag = subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"], stderr=subprocess.STDOUT).decode("utf-8").strip()
        return f"v{tag}" if tag else None
    except subprocess.CalledProcessError:
        pass
    
    commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("utf-8").strip()[:7]
    return f"v{commit_hash}"

def copy_resources(src_dir, dst_dir):
    if os.path.isdir(src_dir):
        shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)

def package_directory_into_zip(source_dir, target_zip_path, temp_base):
    with zipfile.ZipFile(target_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(temp_base):
            for file in files:
                arcname = os.path.relpath(os.path.join(root, file), temp_base)
                zipf.write(os.path.join(root, file), arcname=arcname)

def prepare_temp_and_copy_content(resource_dir, scripts_subdir, temp_base):
    omniocular_src = os.path.join(resource_dir, "OmniOcular")
    public_resource_src = os.path.join(resource_dir, "Public_Resource")
    
    # 复制OmniOcular文件夹
    omniocular_dst = os.path.join(temp_base, "OmniOcular")
    copy_resources(omniocular_src, omniocular_dst)
    
    # 复制公共文件
    if os.path.isdir(public_resource_src):
        for item in os.listdir(public_resource_src):
            src_item = os.path.join(public_resource_src, item)
            dst_item = os.path.join(temp_base, item)
            if os.path.isdir(src_item):
                shutil.copytree(src_item, dst_item, dirs_exist_ok=True)
            else:
                shutil.copy2(src_item, dst_item)
                
    # 复制脚本文件到OmniOcular目录
    for file in os.listdir(scripts_subdir):
        src_file = os.path.join(scripts_subdir, file)
        shutil.copy2(src_file, os.path.join(omniocular_dst, os.path.basename(src_file)))

def pack_subdirectories(resource_dir, scripts_dir, output_dir):
    version = get_latest_git_tag_or_commit()
    if not version:
        print("Failed to determine the version.")
        return
    
    versioned_output_dir = os.path.join(output_dir, version)
    os.makedirs(versioned_output_dir, exist_ok=True)
    
    for dir_name in os.listdir(scripts_dir):
        full_sub_dir_path = os.path.join(scripts_dir, dir_name)
        if os.path.isdir(full_sub_dir_path):
            temp_base = os.path.join(versioned_output_dir, "temp")
            os.makedirs(temp_base, exist_ok=True)
            
            prepare_temp_and_copy_content(resource_dir, full_sub_dir_path, temp_base)
            
            zip_file_name = f"{dir_name}_{version}.zip"
            zip_file_path = os.path.join(versioned_output_dir, zip_file_name)
            package_directory_into_zip(full_sub_dir_path, zip_file_path, temp_base)
            
            shutil.rmtree(temp_base)
            print(f"Directory '{dir_name}' packaged into '{zip_file_name}'.")

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    resource_directory = os.path.join(current_dir, "..", "Resource")
    scripts_directory = os.path.join(current_dir, "..", "OO_Scripts")
    release_output_directory = os.path.join(current_dir, "..", "ReleaseOut")
    
    pack_subdirectories(resource_directory, scripts_directory, release_output_directory)

if __name__ == "__main__":
    main()