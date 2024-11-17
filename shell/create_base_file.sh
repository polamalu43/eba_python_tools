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
TARGET_DIRS=("models" "views" "services" "repositories" "templates")

# 各ディレクトリにファイルを作成
for dir in "${TARGET_DIRS[@]}"; do
    TARGET_PATH="$ROOT_DIR/$dir"

    if [ -d "$TARGET_PATH" ]; then
        if [ "$dir" == "templates" ]; then
            # templates内にpagesディレクトリを作成し、その中にHTMLファイルを作成
            PAGE_DIR="$TARGET_PATH/pages"
            mkdir -p "$PAGE_DIR"
            touch "$PAGE_DIR/$FILENAME.html"
            echo "Created $PAGE_DIR/$FILENAME.html"
        else
            # _ini_.py にインポート文を追加する処理
            touch "$TARGET_PATH/$FILENAME.py"
            echo "Created $TARGET_PATH/$FILENAME.py"

            INIT_FILE="$TARGET_PATH/__ini__.py"
            if [ -f "$INIT_FILE" ]; then
                echo "from .$FILENAME import *" >> "$INIT_FILE"
                echo "Added import statement to $INIT_FILE"
            else
                echo "No __ini__.py found in $TARGET_PATH, skipping import update."
            fi
        fi
    else
        echo "Directory $TARGET_PATH does not exist, skipping..."
    fi
done
