# SNPファイル処理・グラフ作成Windowsアプリケーション

## プロジェクト概要

エクスプローラーからSNP（Single Nucleotide Polymorphism）ファイルをインポートし、データを解析してグラフを作成するWindowsデスクトップアプリケーション。

## 技術スタック選択肢と推奨構成

### 1. 推奨構成：Python + Tkinter/PyQt + Matplotlib

**メリット:**

- SNPファイル処理に最適なライブラリが豊富（pandas, numpy, scikit-learn）
- グラフ作成ライブラリが充実（matplotlib, plotly, seaborn）
- バイオインフォマティクス専用ライブラリ（BioPython）が利用可能
- 開発が高速で、プロトタイピングに最適

**技術構成:**

- **フロントエンド**: Tkinter（標準）またはPyQt5/6（高機能UI）
- **データ処理**: pandas, numpy
- **グラフィング**: matplotlib, seaborn, plotly
- **SNP解析**: BioPython, scikit-learn
- **ファイル処理**: pathlib, os
- **配布**: PyInstaller（.exeファイル化）

### 2. 代替案：Electron + Node.js

**メリット:**

- モダンなWebUI技術が使用可能
- クロスプラットフォーム対応
- リッチなUI/UXが作成可能

**デメリット:**

- バイオインフォマティクス処理ライブラリが限定的
- ファイル容量が大きくなる

### 3. 代替案：C# WPF/.NET

**メリット:**

- Windows向けに最適化
- 高性能なUI
- Visual Studioでの開発効率

**デメリット:**

- SNP解析ライブラリが限定的
- 学習コストが高い

## アプリケーション設計

### アーキテクチャ概要

```txt
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   GUI Layer     │────│  Logic Layer     │────│  Data Layer     │
│  (Tkinter/PyQt) │    │ (Processing)     │    │ (File I/O)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
        │                       │                      │
        │              ┌────────────────┐              │
        └──────────────│  Graph Engine  │──────────────┘
                       │  (Matplotlib)  │
                       └────────────────┘
```

### ディレクトリ構造

```txt
data-processing-app/
├── src/
│   ├── main.py              # メインアプリケーション
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── main_window.py   # メインウィンドウ
│   │   ├── file_dialog.py   # ファイル選択ダイアログ
│   │   └── graph_viewer.py  # グラフ表示ウィンドウ
│   ├── data/
│   │   ├── __init__.py
│   │   ├── snp_loader.py    # SNPファイル読み込み
│   │   ├── data_processor.py# データ前処理
│   │   └── validator.py     # データバリデーション
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── statistics.py    # 統計解析
│   │   ├── clustering.py    # クラスタリング
│   │   └── pca.py          # 主成分分析
│   ├── visualization/
│   │   ├── __init__.py
│   │   ├── plot_manager.py  # グラフ管理
│   │   ├── scatter_plot.py  # 散布図
│   │   ├── histogram.py     # ヒストグラム
│   │   └── heatmap.py      # ヒートマップ
│   └── utils/
│       ├── __init__.py
│       ├── config.py        # 設定管理
│       └── logger.py        # ログ管理
├── tests/
│   ├── test_snp_loader.py
│   ├── test_data_processor.py
│   └── test_visualization.py
├── data/
│   └── sample_files/        # サンプルSNPファイル
├── docs/
│   ├── user_manual.md
│   └── api_reference.md
├── requirements.txt
├── setup.py
├── config.ini
└── README.md
```

## 主要機能設計

### 1. ファイルインポート機能

**対応ファイル形式:**

- `.vcf` (Variant Call Format)
- `.bed` (Browser Extensible Data)
- `.ped` (PLINK PED format)
- `.csv` (カスタムSNPフォーマット)
- `.txt` (タブ区切り形式)

**機能:**

- ドラッグ&ドロップ対応
- 複数ファイル同時インポート
- ファイル形式自動検出
- プレビュー機能

### 2. データ処理機能

**前処理:**

- 欠損値処理
- 品質フィルタリング
- アレル頻度計算
- ハーディ・ワインベルグ平衡検定

**解析機能:**

- 基本統計量計算
- 主成分分析（PCA）
- クラスタリング（K-means, 階層クラスタリング）
- 連鎖不平衡解析

### 3. グラフ作成機能

**対応グラフタイプ:**

- 散布図（PCA結果表示）
- ヒストグラム（アレル頻度分布）
- ヒートマップ（連鎖不平衡）
- Manhattan plot（GWAS結果）
- QQプロット（統計検定結果）

**グラフ機能:**

- インタラクティブ操作
- ズーム・パン
- データポイント詳細表示
- 画像エクスポート（PNG, PDF, SVG）

### 4. UI/UX設計

**メインウィンドウ構成:**

```txt
┌─────────────────────────────────────────────────────────────┐
│ File  Edit  View  Analysis  Graph  Help            [_][□][X]│
├─────────────────────────────────────────────────────────────┤
│ [Import] [Save] [Export]  | [PCA] [Cluster] [Stats]         │
├─────────────┬───────────────────────────────────────────────┤
│             │                                               │
│  File List  │           Graph Display Area                  │
│             │                                               │
│ ○ file1.vcf │                                               │
│ ○ file2.bed │                                               │
│ ○ file3.ped │                                               │
│             │                                               │
│             │                                               │
├─────────────┼───────────────────────────────────────────────┤
│ Properties  │               Analysis Results                │
│             │                                               │
│ Samples: 100│                                               │
│ SNPs: 50000 │                                               │
│ Missing: 2% │                                               │
└─────────────┴───────────────────────────────────────────────┘
```

## 開発フェーズ

### Phase 1: 基盤開発

1. 基本プロジェクト構造作成
2. ファイル読み込み機能実装
3. 基本UI作成

### Phase 2: データ処理

1. SNPファイルパーサー実装
2. データバリデーション機能
3. 基本統計処理

### Phase 3: 可視化機能

1. 基本グラフ機能実装
2. インタラクティブ機能追加
3. エクスポート機能

### Phase 4: 高度な解析

1. PCA実装
2. クラスタリング機能
3. 詳細統計解析

### Phase 5: 配布・最適化

1. パッケージング（PyInstaller）
2. パフォーマンス最適化
3. ドキュメント整備

## 技術的考慮事項

### パフォーマンス

- 大容量SNPファイル（>1GB）対応
- メモリ効率的な処理（chunk processing）
- 並列処理対応（multiprocessing）

### セキュリティ

- ファイル入力バリデーション
- 安全なファイル処理
- エラーハンドリング

### 拡張性

- プラグイン機能
- カスタムファイル形式対応
- 新しいグラフタイプ追加

## 必要なPythonパッケージ

```txt
# GUI
tkinter (標準ライブラリ) または PyQt5/6

# データ処理
pandas>=1.5.0
numpy>=1.21.0
scipy>=1.8.0

# バイオインフォマティクス
biopython>=1.79
pysam>=0.19.0

# 可視化
matplotlib>=3.5.0
seaborn>=0.11.0
plotly>=5.0.0

# 解析
scikit-learn>=1.1.0
statsmodels>=0.13.0

# ユーティリティ
pathlib
configparser
logging

# 配布
pyinstaller>=5.0.0
```

## 次のステップ

1. Python環境セットアップ
2. 基本プロジェクト構造作成
3. 要件に応じたライブラリ選択と依存関係管理
4. サンプルSNPファイルの準備
5. プロトタイプ開発開始

このアプリケーションは、研究用途でのSNPデータ解析を効率化し、直感的なグラフィカルインターフェースを通じて複雑なバイオインフォマティクス解析を可能にすることを目指しています。
