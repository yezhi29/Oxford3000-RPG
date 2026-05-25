# Oxford 5000 RPG Safe Plugin 安全插件版

这个包是“插件”，不是完整项目。它不会包含 `characters/`，不会覆盖你的世界观文件，也不会覆盖你的 `index.html`。

## 包内文件

- `vocabulary/oxford5000_extra.csv`：从 American_Oxford_5000.pdf 抽取的全量词库，共 1990 条。
- `tools/vocab_trainer.py`：每日抽 8 个词、生成今日任务、复习。
- `tools/import_enriched_json.py`：以后导入中文释义、例句、搭配、角色场景。
- `batches/enrichment_batches.jsonl`：按 40 个词一批，方便你发给 ChatGPT 分批补卡片内容。
- `vocab_cards.html`：词汇卡网页，不覆盖原来的 `index.html`。

## 安装方法

把本包解压到你的项目根目录 `Oxford3000-RPG/`，只会新增或覆盖上面这些文件。

建议先备份你自己的 `vocabulary/oxford5000_extra.csv`。

## 运行

```bash
python tools/vocab_trainer.py init
python tools/vocab_trainer.py new
python -m http.server 8000
```

浏览器打开：

```text
http://localhost:8000/vocab_cards.html
```

## 注意

这个安全版不会动：

- `characters/`
- `story/universe.md`
- `story/character_learning_matrix.md`
- `index.html`
- `README.md`
- 你之前写的世界观、人设、剧情文件
