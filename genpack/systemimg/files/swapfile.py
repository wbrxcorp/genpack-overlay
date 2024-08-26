import os,shutil,fcntl,math,ctypes,ctypes.util,array,stat,subprocess,logging

libc = ctypes.CDLL(ctypes.util.find_library('c'), use_errno=True)
libc.fallocate.argtypes = (ctypes.c_int, ctypes.c_int, ctypes.c_int64, ctypes.c_int64)

def get_total_memory_in_gib():
    meminfo = os.path.join("/proc/meminfo")
    if not os.path.isfile(meminfo): return None
    with open(meminfo) as f:
        for line in f:
            cols = line.split(None, 3)
            if len(cols) == 3 and cols[0] == "MemTotal:" and cols[2] == "kB":
                return int(cols[1]) // (2**20)
    return None

def closest_power_of_2(n):
    if n & (n-1) == 0: return n
    k = math.floor(math.log2(n))
    power_of_2_1 = 2 ** k
    power_of_2_2 = 2 ** (k+1)
    if abs(n - power_of_2_1) < abs(n - power_of_2_2):
        return power_of_2_1
    else:
        return power_of_2_2

def determine_swapfile_size(rw_dir, memory_in_gib):
    total, used, free = shutil.disk_usage(rw_dir)
    swapfile_size = closest_power_of_2(memory_in_gib) * 2 if memory_in_gib > 0 else 2
    free_gib = free // (2 ** 30)
    logging.info("Free disk space: %d GiB" % free_gib)
    while swapfile_size > (free_gib // 10): # 10% of free space
        swapfile_size //= 2
    return swapfile_size

def _IOR(code,num,size):
    return 2 << 30 | code << 8 | num | size << 16

def _IOW(code,num,size):
    return 1 << 30 | code << 8 | num | size << 16

def create_swapfile(swapfile, swapfile_size):
    FS_IOC_GETFLAGS = _IOR(ord('f'), 1, ctypes.sizeof(ctypes.c_long))
    FS_IOC_SETFLAGS = _IOW(ord('f'), 2, ctypes.sizeof(ctypes.c_long))
    FS_NOCOW_FL = 0x00800000

    try:
        fd = os.open(swapfile, os.O_CREAT|os.O_RDWR, stat.S_IRUSR|stat.S_IWUSR)
    except OSError:
        logging.error("Failed to create swapfile")
        return False
    arg = array.array('L', [0])
    fcntl.ioctl(fd, FS_IOC_GETFLAGS, arg, True)
    arg[0] |= FS_NOCOW_FL
    try:
        fcntl.ioctl(fd, FS_IOC_SETFLAGS, arg, True)
    except OSError:
        pass # fstype without nocow flag support
    os.close(fd)
    fd = os.open(swapfile, os.O_RDWR)
    if libc.fallocate(fd, 0, 0, swapfile_size * (2 ** 30)) < 0:
        os.close(fd)
        os.unlink(swapfile)
        logging.error("Failed to create swapfile")
        return False
    os.close(fd)
    rst = subprocess.call(["/sbin/mkswap", swapfile])
    if rst != 0:
        logging.error("mkswap failed")
        return False
    #else
    return True

def configure(ini):
    swapfile_size = 0
    rw_dir = "/run/initramfs/rw"
    if not os.path.ismount(rw_dir):
        logging.warning("%s if not a mountpoint" % rw_dir)
        return

    # check if rw layer is appropreate to place swapfile
    swapfile_ok = False
    with open("/proc/mounts") as f:
        for line in f:
            if not line.startswith("/dev/"): continue
            cols = line.split(' ', 2)
            if len(cols) >= 2 and cols[1] == os.path.realpath(rw_dir):
                swapfile_ok = True
                break

    if not swapfile_ok: 
        logging.debug("R/W layer type is not appropriate to have a swapfile(tmpfs?)")
        return
    #else
    swapfile = os.path.join(rw_dir, "swapfile")
    if ini.getboolean("_default", "swapfile", fallback=True):
        if not os.path.exists(swapfile): 
            swapfile_size = determine_swapfile_size(rw_dir, get_total_memory_in_gib())
            if swapfile_size > 0:
                logging.info("Swapfile size: %d GiB" % swapfile_size)
                create_swapfile(swapfile, swapfile_size)
            else:
                logging.warning("Swapfile not created due to insufficient disk space.")
    else:
        if os.path.exists(swapfile):
            os.unlink(swapfile)
            logging.info("Swapfile previously used removed")
    
    if os.path.exists(swapfile):
        if subprocess.call(["/sbin/swapon", swapfile]) == 0:
            logging.info("Swapfile activated.")
        else:
            logging.error("Swapfile activation failed.")

if __name__ == "__main__":
    create_swapfile("./swapfile", 1)
