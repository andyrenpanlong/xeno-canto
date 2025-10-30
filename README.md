# Xeno-canto 鸟类数据爬虫
https://xeno-canto.org//explore//api -- 官网api使用说明
这是一个用于采集 [xeno-canto.org](https://xeno-canto.org/) 鸟类录音数据的Python爬虫工具。

## 功能特点

- 支持按鸟类名称搜索录音数据
- 支持批量采集多种鸟类数据
- 自动处理分页，获取完整数据
- 支持导出为CSV和JSON格式
- 包含详细的录音元数据（位置、时间、设备等）
- 友好的错误处理和进度显示

## 安装依赖

```bash
pip install -r requirements.txt
```

## 快速开始

### 基本使用

```python
from xeno_canto_scraper import XenoCantoScraper

# 创建爬虫实例（使用API密钥）
api_key = "your_api_key_here"
scraper = XenoCantoScraper(api_key=api_key)

# 搜索知更鸟的录音
recordings = scraper.get_all_recordings("Robin", max_pages=5)

# 保存数据
scraper.save_to_csv(recordings, "robin_data.csv")
scraper.save_to_json(recordings, "robin_data.json")
```

### 下载录音文件

```python
# 获取数据并下载录音文件
recordings = scraper.get_recordings_with_download(
    bird_name="Turdus migratorius",
    max_pages=2,
    max_downloads=5,
    download_dir="recordings/robin"
)

# 或者单独下载
scraper.download_recordings_batch(recordings, "my_recordings", max_downloads=10)
```

### 批量采集

```python
# 批量搜索多种鸟类
bird_names = [
    "Passer domesticus",    # 家麻雀
    "Turdus migratorius",   # 美洲知更鸟
    "Corvus brachyrhynchos" # 美洲乌鸦
]

scraper.batch_search(bird_names, output_dir="bird_collection")
```

## 运行示例

```bash
# 运行主测试程序
python xeno_canto_scraper.py

# 运行使用示例
python example_usage.py

# 运行录音下载示例
python download_example.py

# 运行简单使用示例
python simple_usage.py
```

## 数据字段说明

采集的数据包含以下主要字段：

- `id`: 录音ID
- `gen`: 属名
- `sp`: 种名  
- `en`: 英文名
- `cnt`: 国家
- `loc`: 具体地点
- `lat/lng`: 经纬度
- `date/time`: 录音日期时间
- `rec`: 录音者
- `type`: 声音类型（song, call等）
- `q`: 质量评级
- `url`: 录音页面URL
- `file`: 音频文件URL

## 搜索技巧

### 按物种搜索
```python
# 使用学名搜索更精确
recordings = scraper.get_all_recordings("Turdus migratorius")

# 使用英文名搜索
recordings = scraper.get_all_recordings("American Robin")
```

### 高级搜索参数
可以在搜索时使用xeno-canto的高级参数：

- `cnt:china` - 搜索中国的录音
- `q:A` - 只搜索A级质量的录音
- `type:song` - 只搜索鸣唱类型
- `year:2023` - 搜索2023年的录音

## 注意事项

1. 请合理使用，避免过于频繁的请求
2. 代码中已加入适当的延时机制
3. 大量数据采集时建议分批进行
4. 遵守xeno-canto的使用条款

## 输出格式

- CSV格式：适合在Excel等表格软件中查看
- JSON格式：适合程序进一步处理
- 每种鸟类会生成单独的文件
- 批量采集会生成汇总统计文件
