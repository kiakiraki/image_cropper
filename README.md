# Image crop tool

指定ディレクトリ内の画像の任意領域をまとめてCropする雑なスクリプト

(スクリーンショットの加工などに)

## Requirements

* Python>=3.6
* click
* cv2
* numpy
* tqdm
* yaml

## How to use

### コンフィグファイルの記述

以下の要領でコンフィグファイルを記述する

```yaml
- target_path: /path/to/target/dir
  output_path: /path/to/output/dir
  ext: jpg
  output_header: crop  # 出力ファイル名の先頭に付けるヘッダ
  bbox:  # xmin, ymin, xmax, ymax の順
    - 
      - 23
      - 177
      - 684
      - 675
```


### スクリプトの実行

`-c` オプションでコンフィグファイルを指定し実行する

```
python crop_image.py -c {path/to/config.yml}
```
