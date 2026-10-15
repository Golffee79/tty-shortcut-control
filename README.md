# TTY Shortcut Control

A compact GTK app to enable or disable **Ctrl + Alt + F1** switching to TTY1, with English and Thai labels and automatic saving.

แอปขนาดเล็กสำหรับเปิด–ปิดการสลับไปหน้าคอนโซล **TTY1** ด้วย **Ctrl + Alt + F1** มีภาษาไทยและอังกฤษ พร้อมบันทึกค่าอัตโนมัติ

![TTY Shortcut Control screenshot](docs/screenshot.png)

## Install with APT / ติดตั้งผ่าน APT

Add this third-party repository once on each machine, then install by package name. This project is not part of the official Linux Mint / Debian repositories.

เพิ่มแหล่งแพ็กเกจครั้งแรกในแต่ละเครื่อง จากนั้นติดตั้งและอัปเดตผ่าน APT ได้ตามปกติ

```bash
sudo apt update
sudo apt install curl ca-certificates
sudo install -d -m 755 /etc/apt/keyrings
curl -fsSL https://raw.githubusercontent.com/Golffee79/tty-shortcut-control/main/apt/keyring.gpg -o /tmp/tty-shortcut-control-keyring.gpg
sudo install -m 644 /tmp/tty-shortcut-control-keyring.gpg /etc/apt/keyrings/tty-shortcut-control.gpg
echo 'deb [signed-by=/etc/apt/keyrings/tty-shortcut-control.gpg] https://raw.githubusercontent.com/Golffee79/tty-shortcut-control/main/apt ./' | sudo tee /etc/apt/sources.list.d/tty-shortcut-control.list
sudo apt update
sudo apt install tty-shortcut-control
```

Launch **TTY Shortcut Control** from the applications menu, or run `tty-shortcut-control`. Run the app as your normal user, without sudo.

เปิดจากเมนูแอป หรือพิมพ์ `tty-shortcut-control` โดยไม่ใช้ sudo

Updates / อัปเดต:

```bash
sudo apt update
sudo apt install --only-upgrade tty-shortcut-control
```

## Requirements / สิ่งที่ต้องมี

- Linux with an **X11** desktop session; Wayland is not supported.
- Python 3, PyGObject, GTK 3 and xmodmap (installed automatically by APT).
- Built and checked on **LMDE 7 (Linux Mint Debian Edition)**. Other desktop environments have not been tested.
- แอปตรวจรหัสปุ่ม F1 และสำรองค่าของเครื่องนั้นก่อนปิดคีย์ลัด รองรับเฉพาะ X11

The original mapping is saved at `~/.config/tty-shortcut-control/original-f1.txt`.

## Usage / วิธีใช้

| Toggle / สวิตช์ | Behavior / การทำงาน |
| --- | --- |
| **On / เปิดใช้งาน** | Ctrl + Alt + F1 switches to TTY1 / ใช้คีย์ลัดสลับไปหน้าคอนโซลได้ |
| **Off / ปิดใช้งาน** | Stops this shortcut from switching to TTY1 / ปิดการสลับหน้าจอด้วยคีย์ลัดนี้ |

Changes take effect immediately. Disabling creates a per-user autostart entry to reapply the setting after login. Enabling restores the saved F1 mapping and removes the entry. Other TTY shortcuts and the normal F1 key remain available.

เปลี่ยนค่าแล้วมีผลทันที ไม่ต้องกด Save เมื่อปิดคีย์ลัด แอปจะจำค่าหลังล็อกอิน ปุ่ม F1 ปกติและคีย์ลัด TTY ปุ่มอื่นยังใช้งานได้

Desktop keyboard-layout changes can reset the mapping during a session. If that happens, reopen the app and disable the shortcut again.

## Run from source / เปิดจากซอร์สโค้ด

```bash
sudo apt install python3 python3-gi gir1.2-gtk-3.0 x11-xserver-utils git
git clone https://github.com/Golffee79/tty-shortcut-control.git
cd tty-shortcut-control
/usr/bin/python3 tty-shortcut-control.py
```

Keep the script at the same path while automatic disabling is enabled.

## Moving from the old manual installation / เปลี่ยนจากแอปเก่า

Turn the old app's toggle **On** and close it before switching to the package. If the applications menu still opens the old version, remove its launcher:

```bash
rm -f ~/.local/share/applications/tty-shortcut-control.desktop
```

เปิดสวิตช์ On ในแอปเก่าแล้วปิดหน้าต่างก่อนใช้แพ็กเกจ หากเมนูยังเปิดแอปเก่า ให้ลบ launcher เก่าด้วยคำสั่งข้างต้น

## Restore or uninstall / คืนค่าและถอนการติดตั้ง

First turn the toggle **On** to restore the original mapping and remove the autostart entry, then uninstall:

```bash
sudo apt remove tty-shortcut-control
```

If you cannot open the app, remove the autostart entry, then log out and back in to restore session defaults:

```bash
rm -f ~/.config/autostart/tty-shortcut-control.desktop
```

ก่อนลบแอป ให้เปิดสวิตช์ **On** เพื่อคืนค่า หากเปิดแอปไม่ได้ ให้ลบรายการเริ่มอัตโนมัติ แล้วล็อกเอาต์และเข้าใหม่

## Build a release / สร้างแพ็กเกจ

Install `dpkg-dev`, `apt-utils`, and `gnupg`. Use a dedicated private signing key directory outside this repository:

```bash
GNUPGHOME=/path/to/private-signing-key scripts/build-release.sh 0.2.0
```

The script builds a .deb, package indexes and signed APT metadata in `apt/`. Commit these public artifacts to publish an update. Keep the private signing key outside the repository.
