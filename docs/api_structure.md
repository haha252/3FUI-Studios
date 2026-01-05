# 3FUI Studios API 数据结构文档

本文档详细说明了构建脚本生成的 JSON 文件结构，用于指导前端开发和第三方集成。所有生成的文件均位于 `public/api/` 目录下。

## 1. 入口文件 (`index.json`)

**路径**: `/api/index.json`
**用途**: 网站配置元数据和主要 API 入口点。

```json
{
  "site_name": "3FUI-Studios",
  "total_items": 100,           // 总项目数
  "total_pages": 5,             // 总页数
  "items_per_page": 200,        // 每页项目数
  "first_page_url": "/api/pages/1.json", // 第一页数据路径
  "tags_url": "/api/tags.json",          // Tags 索引路径
  "all_projects_url": "/api/all.json"    // 全量极简索引路径
}
```

---

## 2. 全量索引 (`all.json`)

**路径**: `/api/all.json`
**用途**: 提供极其精简的所有项目列表，用于前端快速加载和本地搜索（仅标题/作者）。
**注意**: 为了性能，此文件**不包含** Tags、描述或下载链接。

```json
[
  {
    "id": "2026/example_project", // 项目唯一 ID
    "basic": {
      "title": "项目标题"          // 仅包含标题
    },
    "meta": {
      "author": "发布者名称"       // 仅包含发布者
    }
  }
]
```

---

## 3. Tags 索引 (`tags.json`)

**路径**: `/api/tags.json`
**用途**: 提供 Tag 分类结构、统计信息以及 Tag 名称到文件名的映射表。

```json
{
  "categories": [
    {
      "name": "规格",
      "tags": ["1080p", "4K"] // 该分类下的推荐 Tag
    }
  ],
  "stats": {
    "1080p": 50,  // 该 Tag 下的项目数量
    "AV1": 20
  },
  "map": {
    // Tag 名称 -> 哈希文件名 (MD5)
    "1080p": "5d41402abc4b2a76b9719d911017c592.json",
    "AV1": "c4ca4238a0b923820dcc509a6f75849b.json"
  }
}
```

---

## 4. 独立 Tag 数据文件

**路径**: `/api/tags/{hash}.json`
**用途**: 当用户点击某个 Tag 时加载，包含该 Tag 下所有项目的列表。
**特点**: 相比 `all.json`，此文件**包含 Tags** 信息，用于前端展示 Tag 标签。

```json
[
  {
    "id": "2026/example_project",
    "basic": {
      "title": "项目标题",
      "tags": ["1080p", "AV1"] // 包含 Tags
    },
    "meta": {
      "author": "发布者名称"
    }
  }
]
```

---

## 5. 项目详情文件

**路径**: `/api/details/{id}.json` (注意：文件名中的 `/` 对应目录结构，例如 `api/details/2026/example.json`)
**用途**: 项目的完整信息，仅在用户展开详情时加载。

```json
{
  "id": "2026/example_project",
  "basic": {
    "title": "完整标题",
    "description": "详细描述...", // 支持换行
    "tags": ["Tag1", "Tag2"]
  },
  "meta": {
    "author": "发布者",
    "date": "2026-01-01"
  },
  "source": {
    "url": "https://...",
    "description": "来源描述"
  },
  "download": {
    "url": "https://..."
  }
}
```

## 6. 分页文件 (`pages/*.json`)

**路径**: `/api/pages/{n}.json`
**用途**: 传统分页浏览模式使用。

```json
{
  "page": 1,
  "total_pages": 5,
  "total_items": 100,
  "items": [
    {
      "id": "...",
      "basic": {
        "title": "...",
        "tags": ["..."] // 分页数据包含 Tags
      },
      "meta": { "author": "..." }
    }
  ]
}
```

---

## 结构设计总结

1.  **极简主义 (`all.json`)**: 仅保留搜索必须字段（ID、标题、作者），移除 Tags 和描述，最大化减少首屏数据量。
2.  **按需加载 (`details/`)**: 详情内容（通常体积最大）仅在交互时加载。
3.  **独立索引 (`tags/`)**: Tags 数据独立存储，避免在主索引中重复冗余，同时支持精确筛选。
