EAPI=8
inherit git-r3

DESCRIPTION="A tool to send messages to Slack"
EGIT_REPO_URI="https://github.com/slackapi/python-slack-sdk.git"
EGIT_BRANCH="main"

LICENSE="MIT"
SLOT="0"
KEYWORDS="amd64 arm64 riscv"
IUSE=""

src_compile() {
    mkdir -p "${T}/build" || die "mkdir failed"
    mv "${S}/slack" "${S}/slack_sdk" "${T}/build/" || die "mv failed"
    cp "${FILESDIR}/slack-send-message.py" "${T}/build/__main__.py" || die "cp failed"
    python -m zipapp "${T}/build" -o "${T}/slack-send-message.pyz" || die "zipapp failed"
    echo '#!/usr/bin/env python3' | cat - "${T}/slack-send-message.pyz" > "${T}/slack-send-message"
}

src_install() {
    exeinto "/usr/bin"
    doexe "${T}/slack-send-message"

    dodir "/etc/slack"
    echo "xoxb-YOUR-BOT-TOKEN-HERE" > "${ED}/etc/slack/bot-token"
    chmod 600 "${ED}/etc/slack/bot-token"
}