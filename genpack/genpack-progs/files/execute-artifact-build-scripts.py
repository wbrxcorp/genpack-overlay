#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys,os,subprocess

def determine_interpreter(script):
    if os.access(script, os.X_OK): return None
    #else
    if script.endswith(".sh"): return "/bin/sh"
    #else
    if script.endswith(".py"): return "/usr/bin/python"
    raise ValueError(f"Script is not executable: {script}")

def main():
    build_script = "/build"
    if os.path.isfile(build_script):
        if os.access(build_script, os.X_OK):
            print(f"Executing build script: {build_script}")
            subprocess.check_call([build_script])
        else:
            raise ValueError(f"Build script is not executable: {build_script}")

    build_script_d = "/build.d"
    if not os.path.exists(build_script_d): return
    #else
    # os.listdir returns filenames in arbitrary order, usually ASCII order on most filesystems,
    # but it is not guaranteed by Python. If you want ASCII order, sort explicitly:
    user_subdirs = []

    for script in sorted(os.listdir(build_script_d)):
        script_path = os.path.join(build_script_d, script)
        if os.path.isfile(script_path):
            interpreter = determine_interpreter(script_path)
            print(f"Executing build script: /build.d/{script}")
            subprocess.check_call([os.path.join("/build.d", script)] if interpreter is None else [interpreter, os.path.join("/build.d", script)])
        elif os.path.isdir(script_path):
            user_subdirs.append(script)
            print(f"Found user subdirectory in build.d: {script_path}")
    
    for subdir in user_subdirs:
        subdir_path = os.path.join(build_script_d, subdir)
        for script in sorted(os.listdir(subdir_path)):
            script_path = os.path.join(subdir_path, script)
            if not os.path.isfile(script_path):
                print(f"Skipping non-file in /build.d/{subdir}: {script}")
                continue
            #else
            print(f"Executing build script in user subdirectory: /build.d/{subdir}/{script} as user {subdir}")
            interpreter = determine_interpreter(script_path)
            subprocess.check_call([os.path.join("/build.d", subdir, script)] if interpreter is None else [interpreter, os.path.join("/build.d", subdir, script)], user=subdir)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error executing build scripts: {e}", file=sys.stderr)
        exit(1)