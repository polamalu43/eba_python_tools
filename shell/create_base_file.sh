usage() {
    echo "Usage: $0 -f <filename_without_extension>"
    exit 1
}

# 引数の解析
while getopts "f:" opt; do
    case "$opt" in
        f) FILENAME="$OPTARG";;
        *) usage;;
    esac
done

# FILENAMEが設定されていない場合、エラーを表示
if [ -z "$FILENAME" ]; then
    usage
fi

# プロジェクトのルートディレクトリを定義
ROOT_DIR=$(dirname "$(dirname "$(realpath "$0")")")/src

# 対象のディレクトリリスト
TARGET_DIRS=("models" "views" "services" "repository")

# 各ディレクトリにファイルを作成
for dir in "${TARGET_DIRS[@]}"; do
    TARGET_PATH="$ROOT_DIR/$dir"
    if [ -d "$TARGET_PATH" ]; then
        touch "$TARGET_PATH/$FILENAME.py"
        echo "Created $TARGET_PATH/$FILENAME.py"
    else
        echo "Directory $TARGET_PATH does not exist, skipping..."
    fi
done
