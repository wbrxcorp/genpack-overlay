# このシステムは genpack の artifact です

ssh などでログインしたあなた（エージェント）宛ての手引きです。
この文書は `/.genpack/genpack.md` にあります。

ここは汎用に組み上げられた Linux サーバーではなく、**genpack** というツールチェーンが
設計図からビルドした **不変 (immutable) システムイメージ** です。普通の Linux だと思って
操作すると、多くの操作は失敗するか、成功しても意味を持ちません。
まずこの文書で世界観を揃えてから動いてください。

## 1. 何がどう作られて、今どう起動しているか

- 設計図 `genpack.json5`（packages / use / services / users …）から Gentoo stage3 + Portage でビルド
- 成果物は **SquashFS イメージ**。読み取り専用で mount され、その上に overlayfs で今の `/` が作られている
- 起動時は PID 1 として `genpack-init` が `system.ini` を読んで構成を適用し、その後 `exec /sbin/init` で systemd に制御を渡す

```
/                  overlayfs  (lower = SquashFS 読み取り専用 / upper = 書き込み層)
/run/initramfs/ro  SquashFS そのもの (lower 層)
/run/initramfs/rw  upper 層の実体 (データディスク・virtiofs・なければ tmpfs)
/run/initramfs/boot FAT32 ブートパーティション (system.ini, system.img)  # VM 構成では無い
```

`/run/initramfs/` 以下は起動後もマウントされたままです
（genpack-init が PID 1 としてそこにある system.ini を読むため、消えていません）。

## 2. 書き込みが永続するかは構成で決まる

| 構成 | upper 層 | 再起動すると |
|---|---|---|
| データパーティション（データディスク / virtiofs）あり | Btrfs 等 | 変更は残る |
| ない（トランジェントモード） | tmpfs | **すべて消え、SquashFS の素の状態に戻る** |

確認コマンド:

```bash
findmnt -no SOURCE,FSTYPE /              # overlay であること
findmnt -no FSTYPE /run/initramfs/rw     # tmpfs ならトランジェントモード
findmnt -no OPTIONS /usr                 # ro が立っているか (exec-guard)
lsblk                                    # ブート/データパーティションの見た目
```

トランジェントモードでは、今セッションで書き込んだものは再起動で消えます。
調査の成果はローカルファイルに溜め込まずユーザに報告し、永続化が本当に必要なものは
転送方法（scp 等）をユーザと相談してください。

## 3. 設定変更は system.ini に対して書く

genpack は構成を `/etc` 以下に散在させず、**`system.ini`** に集約します。
genpack-init は **毎回の起動時に** これを読み込んで構成を適用するので、
効かせ方は「system.ini を編集して **再起動**」です。

```bash
/run/initramfs/boot/system.ini   # ディスクインストール構成 (FAT32 ブートパーティション)
/run/initramfs/rw/system.ini     # ブートパーティションを介さない構成で、データディスクに置いた場合
```

VM 構成（`vm` コマンド）には FAT32 ブートパーティションが存在しません。
system.ini はそもそも無いことが多く、設定はホスト側の `vm.ini` から QEMU fw_cfg 経由で注入されます
（`opt/timezone`, `opt/lang`, `opt/ssh-public-key` など）。SSH 公開鍵は root と
1000 番台の一般ユーザーの `authorized_keys` に配られます。

### `/etc` を直接編集した場合の結末は、構成と項目で決まる

| 構成 | `/etc` 以下の編集 |
|---|---|
| トランジェント（tmpfs） | 項目を問わず**再起動で消える** |
| 永続（データディスク） | 再起動を越えて残る |

ただし永続構成でも、**genpack-init のスクリプト（`/usr/lib/genpack-init/*.py`）が毎回書き込む項目**
（`timezone`, `locale`, `ssh_pubkey` による authorized_keys, デフォルトネットワーク、`exec_guard` など）
は system.ini 側が正です。`/etc` に書き込んだ同じ項目は次回起動時に再適用・上書きされます。

genpack-init が触らないアプリケーション独自の設定
（例: `/etc/nginx/sites.d/`, `/etc/php/`, `/etc/redmine/` など）は `/etc` に書いて構いません。
永続構成ならそのまま残ります。

system.ini の既知のキー: `timezone`, `locale`, `ssh_pubkey`, `debug`, `exec_guard`。
`[section]` を足すと artifact 自身の初期化スクリプトが読み取ります。

## 4. ここに Portage はない。更新はイメージの差し替え

- `emerge` / `eix` / `revdep-rebuild` は入っていません。
  インストール DB である `/var/db/pkg` も Portage ツリーの `/var/db/repos` も
  ランタイムイメージには含まれません
- `import portage` が一部モジュールについて動くのは
  `genpack-glsa-check` がバージョン比較をするためだけに残されているからです
- OS の更新は「今を emerge で直す」のではなく、**新しいイメージをビルドしてアトミックに差し替える**
  （`system` → `system.cur` → `system.old`）。ロールバックは `system.old`
- 足りないソフトウェアは `genpack.json5` の `packages` に追加して再ビルドする話です。
  **それを決めるのはユーザ側**であり、実行中に作り込むものではありません
- 開発用イメージ（`devel: true` 構成）では man ページ・ドキュメント・ヘッダ等も含みます

### 更新できるのはどこからか（デプロイ形態で違う）

| 構成 | システムイメージの置き場所 | イメージ更新 |
|---|---|---|
| ディスクインストール | ブートパーティション (FAT32) の `system.img`、大きなイメージはデータパーティションの `system` | 稼働中システムの中から `genpack-install <image>` によるセルフアップデートが可能。system.ini も同じ FAT パーティションにあるので、起動しない状態でも他の OS から編集できる |
| VM（`vm` コマンド） | **読み取り専用の virtio-blk デバイス** (`/dev/vda`) として接続された SquashFS | ゲスト内にイメージを置ける書き込み領域がないため**セルフアップデートは成立しない**（`genpack-install` は `No installed system image found.`）。更新はホスト側の作業: `/var/vm/<name>/system` の交換、`vm run <new.squashfs>` の差し替え、`vm.ini` の変更 |

どちらの構成でも `genpack-install` / `genpack-mkiso` は通常イメージに同梱されていません
（セルフアップデートを想定した artifact だけが持ちます）。

## 5. exec-guard が効いていることがある

有効なアーティファクトでは以下が強制されています。

- `/usr` が **read-only bind mount**。`/usr` への書き込みが失敗するのは意図的な保護です
- upper 層に持ち込んだ **ELF バイナリの実行**・**共有ライブラリの dlopen** は `EPERM` で拒否され、
  audit に `key=exec_guard_deny` として記録されます
- シェルスクリプトや Python をインタープリタ経由で実行することは制限されません
- セルフアップデート、npm/pip のネイティブ拡張、バイナリプラグインのダウンロード実行は
  exec-guard と原理的に相容れません（そのソフトウェアはイメージ側にビルドして入れるべきものです）

確認:

```bash
ls /sys/fs/bpf/exec_guard/ 2>/dev/null
grep -i exec_guard /var/log/genpack-init.log
ausearch -k exec_guard_deny --input-logs -ts boot
```

`ausearch` は stdin がパイプだと標準入力を読もうとして `<no matches>` になるので、
`ssh host 'ausearch ...'` のような非対話実行では `--input-logs` を付けてください。
無効化は system.ini の `exec_guard = false`（次回起動から適用）。

## 6. 起動と終了

- initramfs は `dracut-genpack`、PID 1 は `genpack-init` → `exec systemd`
- 終了は `reboot` / `poweroff` を普通に使う。initramfs に制御が戻り
  `genpack-shutdown` が overlayfs と SquashFS を安全に unmount します
- 電源を落とす等の unclean shutdown だとブートパーティションの `boottime.txt` が残痕として残り、
  次回起動の GRUB タイムアウトが延びます（異常のしるし）
- 起動時の構成ログ: `/var/log/genpack-init.log`、`journalctl -b`

## 7. 自分の素性は `/.genpack/` にある

| ファイル | 内容 |
|---|---|
| `arch` / `artifact` / `variant` | アーキテクチャ、アーティファクト名、バリアント名 |
| `commit-id` | アーティファクト定義の git rev（設定時のみ） |
| `packages` | このイメージに入るパッケージ一覧（DESCRIPTION / USE / LICENSE / NEEDED_BY 付き） |
| `timestamp.commit` | ビルドに使われた Portage ツリーの時刻 |
| `banner` | 起動時に表示されるバナー |
| `genpack.md` | この文書 |

脆弱性検査: `genpack-glsa-check`（`/.genpack/packages` を GLSA と突き合わせる。
マスクは `/var/lib/genpack/glsa-check/mask/<GLSA-ID>` に ID 名前のファイルを置く）

## 8. やりがちな誤操作

| 操作 | 結末 |
|---|---|
| `emerge` / `eix` で直そうとする | コマンドがない。そもそも更新の仕組みが違う |
| `/etc` 編集で genpack-init 管理項目を変えようとする | 次回起動で system.ini 側が再適用する。system.ini + 再起動が正 |
| VM ゲスト内でイメージ更新 (`genpack-install`) を試す | 差し替え先の書き込み領域がない。ホスト側の作業 |
| `/usr` に書き込もうとする | read-only で失敗する（exec-guard の保護） |
| 落ちてきた ELF を `chmod +x` して実行 | `EPERM`、audit に `exec_guard_deny` |
| tmpfs 上に調査ノートを積み上げる | 再起動で消える |
| `dd` / `parted` でディスクを触る | ブート (FAT32) / データ (Btrfs) レイアウトと UUID 参照が壊れて起動しない |
| `system.img` / `system.ini` を上書き・削除する | 起動不能。ロールバックは `system.old` |

## 9. 迷ったとき

足りないソフトウェアの追加、恒久的な設定変更、OS の更新 —
これらはすべて **ビルド側の話** です。稼働中に無理に作り込まずユーザに相談してください。
アーティファクトのリポジトリと `genpack.json5` を編集できるのはユーザ側です。

genpack 自体の設計詳細（ビルド機構、profile 階層、system.ini の全キー、`vm` の機能、
exec-guard の実装）はビルドホスト側の `genpack/docs/*.md` にあり、
このイメージには同梱されていません。

どうしても読みたければ、文書は公開リポジトリにあります:

- [wbrxcorp/genpack](https://github.com/wbrxcorp/genpack) — `docs/*.md`（`introduction.md`, `cli.md`, `json5.md`, `boot-sequence.md`, `genpack-init-scripts.md`, `exec-guard.md` など）と `adr/*.md`
- [wbrxcorp/genpack-overlay](https://github.com/wbrxcorp/genpack-overlay) — このイメージのパッケージ定義とプロファイル階層
- [wbrxcorp/genpack-init](https://github.com/wbrxcorp/genpack-init) / [wbrxcorp/genpack-install](https://github.com/wbrxcorp/genpack-install) / [shimarin/vm](https://github.com/shimarin/vm)

クローンして読むこと自体はこのイメージ上で制限されません（exec-guard が止めるのは
upper 層に持ち込んだ ELF の実行までです）。ただしビルド作業自体はビルドホスト側で
行うのが筋です。不明点はまずユーザに聞いてください。
