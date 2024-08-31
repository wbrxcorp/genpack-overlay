import os,re

def get_proc_cmdline():
    with open("/proc/cmdline") as f:
        return f.read().strip()

def installer_cmdline_exists(cmdline):
    return re.search(rf"(?<!\w)walbrix.installer=\S+(?!\w)", cmdline) is not None

def configure(ini):
    kernel_cmdline = get_proc_cmdline()
    dropin_dir = "/etc/systemd/system/wbui.service.d"
    dropin = os.path.join(dropin_dir, "installer.conf")
    if installer_cmdline_exists(kernel_cmdline):
        os.makedirs(dropin_dir, exist_ok=True)
        with open(dropin, "w") as f:
            f.write("[Service]\nExecStart=\nExecStart=/usr/bin/wbui installer\n")
    else:
        if os.path.exists(dropin):
            os.remove(dropin)

if __name__ == "__main__":
    print(installer_cmdline_exists("hoge walbrix.installer=1"))
