#include <sys/mount.h>
#include <sys/reboot.h>
#include <linux/reboot.h>

#include <unistd.h>

#include <iostream>
#include <cstdlib>
#include <filesystem>
#include <vector>
#include <map>
#include <fstream>
#include <algorithm>

static bool debug = false;

static std::string decode_proc_mounts_field(std::string_view s) {
    std::string out;
    out.reserve(s.size());
    for (size_t i = 0; i < s.size(); ) {
        if (s[i] == '\\' && i + 3 < s.size()
            && s[i+1] >= '0' && s[i+1] <= '7'
            && s[i+2] >= '0' && s[i+2] <= '7'
            && s[i+3] >= '0' && s[i+3] <= '7') {
            int v = (s[i+1]-'0')*64 + (s[i+2]-'0')*8 + (s[i+3]-'0');
            out.push_back(static_cast<char>(v));
            i += 4;
        } else {
            out.push_back(s[i++]);
        }
    }
    return out;
}

std::filesystem::path parse_mount_point_from_proc_mounts_line(const std::string& line) {
    // フィールド区切りは空白/タブ（中の空白は \040 等でエスケープ済みなので分割は安全）
    auto is_blank = [](char c){ return c == ' ' || c == '\t'; };

    std::vector<std::string_view> fields;
    fields.reserve(6);

    std::string_view sv = line;
    size_t i = 0;
    while (i < sv.size()) {
        // 区切りをスキップ
        while (i < sv.size() && is_blank(sv[i])) ++i;
        if (i >= sv.size()) break;
        // トークン開始
        size_t j = i;
        while (j < sv.size() && !is_blank(sv[j])) ++j;
        fields.emplace_back(sv.substr(i, j - i));
        i = j;
        if (fields.size() >= 6) break; // mounts形式は少なくとも6フィールド
    }

    if (fields.size() < 2) {
        throw std::runtime_error("Malformed /proc/mounts line: not enough fields");
    }

    std::string decoded = decode_proc_mounts_field(fields[1]);
    return std::filesystem::path(decoded);
}

bool unmount_all_filesystems_under_oldroot() {
    std::cout << "Unmounting all filesystems under old root..." << std::endl;
    // Read /proc/mounts
    std::vector<std::filesystem::path> mount_points;
    try {
        std::ifstream mounts("/proc/mounts");
        std::string line;
        while (std::getline(mounts, line)) {
            std::istringstream iss(line);
            std::filesystem::path mp = parse_mount_point_from_proc_mounts_line(line);
            if (mp.string().find("/oldroot/") == 0) {
                mount_points.push_back(mp);
            }
        }
    }
    catch (const std::exception& e) {
        std::cerr << "Error reading /proc/mounts: " << e.what() << std::endl;
        return false;
    }
    // sort in reverse order to unmount children before parents
    std::sort(mount_points.rbegin(), mount_points.rend());
    std::vector<std::filesystem::path> unmounted_mountpoints;
    for (const auto& mp : mount_points) {
        if (umount(mp.c_str()) == 0) {
            unmounted_mountpoints.push_back(mp);
        } else {
            std::cerr << "Failed to unmount: " << mp << std::endl;
        }
    }

    if (debug) {
        std::cout << "Unmounted mountpoints: " << std::endl;
        for (const auto& mp : unmounted_mountpoints) {
            std::cout << "  " << mp ;
        }
        std::cout << std::endl;
    }

    if (umount("/oldroot") != 0) {
        std::cerr << "Failed to unmount /oldroot" << std::endl;
        return false;
    }

    //else
    std::cout << "Unmounted /oldroot" << std::endl;
    return true;
}

int main(int argc, char* argv[])
{
    if (argc < 2) {
        std::cerr << "No enough arguments provided." << std::endl;
        return EXIT_FAILURE;
    }

    debug = std::filesystem::exists("/shutdown.debug");

    if (geteuid() != 0) {
        std::cerr << "This program must be run as root." << std::endl;
        return EXIT_FAILURE;
    }

    if (!std::filesystem::is_directory("/oldroot")) {
        std::cerr << "/oldroot does not exist or is not a directory." << std::endl;
        return EXIT_FAILURE;
    }

    // move mount /oldroot/run/initramfs/{rw|boot} to /rw_moved. This is mandatory to unmount /oldroot/run
    if (std::filesystem::is_directory("/oldroot/run/initramfs/rw")) {
        std::filesystem::create_directories("/rw_moved");
        if (mount("/oldroot/run/initramfs/rw", "/rw_moved", "", MS_MOVE, nullptr) == 0) {
            if (debug) {
                std::cout << "Moved /oldroot/run/initramfs/rw to /rw_moved" << std::endl;
            }
        } else {
            std::cerr << "Failed to move /oldroot/run/initramfs/rw to /rw_moved" << std::endl;
        }
    }

    if (std::filesystem::is_directory("/oldroot/run/initramfs/boot")) {
        std::filesystem::create_directories("/boot_moved");
        if (mount("/oldroot/run/initramfs/boot", "/boot_moved", "", MS_MOVE, nullptr) == 0) {
            if (debug) {
                std::cout << "Moved /oldroot/run/initramfs/boot to /boot_moved" << std::endl;
            }
        } else {
            std::cerr << "Failed to move /oldroot/run/initramfs/boot to /boot_moved" << std::endl;
        }
    }

    std::vector<std::filesystem::path> mount_points_to_unmount = {
        "/ro","/rw","/boot"
    };

    for (const auto& mp : mount_points_to_unmount) {
        if (std::filesystem::is_directory(mp)) {
            if (umount(mp.c_str()) == 0) {
                std::cout << "Unmounted " << mp << std::endl;
            } else {
                std::cerr << "Failed to unmount " << mp << std::endl;
            }
        }
    }

    unmount_all_filesystems_under_oldroot();

    if (std::filesystem::is_directory("/rw_moved")) {
        if (umount("/rw_moved") == 0) {
            std::cout << "Unmounted /rw_moved" << std::endl;
        } else {
            std::cerr << "Failed to unmount /rw_moved" << std::endl;
        }
    }

    if (std::filesystem::is_directory("/boot_moved")) {
        if (std::filesystem::exists("/boot_moved/boottime.txt")) {
            if (debug) {
                std::cout << "Removing /boot_moved/boottime.txt" << std::endl;
            }
            // remount as rw to remove boottime.txt
            if (mount(nullptr, "/boot_moved", "", MS_REMOUNT, nullptr) != 0) {
                std::cerr << "Failed to remount /boot_moved as rw" << std::endl;
            }
            std::filesystem::remove("/boot_moved/boottime.txt");
        }
        if (umount("/boot_moved") == 0) {
            std::cout << "Unmounted /boot_moved" << std::endl;
        } else {
            std::cerr << "Failed to unmount /boot_moved" << std::endl;
        }
    }

    if (debug) {
        std::cout << "Remaining mounts are:" << std::endl;
        std::ifstream mounts("/proc/mounts");
        std::string line;
        while (std::getline(mounts, line)) {
            std::cout << line << std::endl;
        }
    }

    std::map<std::string, int> command_map = {
        {"reboot", LINUX_REBOOT_CMD_RESTART},
        {"poweroff", LINUX_REBOOT_CMD_POWER_OFF}
    };

    auto it = command_map.find(argv[1]);
    if (it != command_map.end()) {
        std::cout << "Executing command: " << it->first << "..." << std::endl;
        std::cout << std::flush;
        std::cerr << std::flush;
        if (debug) {
            std::cout << "Debug mode: skipping actual " << it->first << std::endl;
            sleep(10000);
            return EXIT_SUCCESS;
        }
        //else
        reboot(it->second);
    }
    // else
    std::cerr << "Unknown command: " << argv[1] << std::endl;

    // flush stdout/stderr
    std::cout << std::flush;
    std::cerr << std::flush;
    return EXIT_FAILURE;
}
