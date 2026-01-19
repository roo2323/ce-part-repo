# Claude Code Plugin 제작 및 배포 가이드

> 자신만의 Skill을 만들어 GitHub에 올리고, 다른 사람들과 공유하는 방법

---

## 1. Plugin 구조 이해

### 1.1 기본 구조 (단일 Plugin)
```
my-plugin/
├── .claude-plugin/
│   └── plugin.json          # Plugin 매니페스트 (필수)
└── skills/
    └── my-skill/
        └── SKILL.md         # Skill 정의 (필수)
```

### 1.2 Marketplace 구조 (여러 Plugin 배포)
```
my-marketplace/
├── .claude-plugin/
│   └── marketplace.json     # Marketplace 매니페스트
└── my-plugin/
    ├── .claude-plugin/
    │   └── plugin.json
    └── skills/
        └── my-skill/
            └── SKILL.md
```

---

## 2. Skill 만들기

### 2.1 SKILL.md 형식
```yaml
---
name: my-skill
description: 이 skill이 무엇을 하는지 설명. 어떤 상황에서 사용하는지 키워드 포함.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
---

# Skill 제목

## 개요
이 skill이 하는 일을 설명합니다.

## 사용 방법
1. 첫 번째 단계
2. 두 번째 단계

## 예시
구체적인 사용 예시를 제공합니다.
```

### 2.2 Frontmatter 옵션
| 필드 | 필수 | 설명 |
|------|------|------|
| `name` | O | skill 식별자 (소문자, 하이픈) |
| `description` | O | skill 설명 (최대 1024자) |
| `allowed-tools` | X | 사용 가능한 도구 제한 |
| `model` | X | 특정 모델 지정 |
| `user-invocable` | X | false로 설정 시 /메뉴에서 숨김 |

---

## 3. Plugin 매니페스트 작성

### 3.1 plugin.json
```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "Plugin 설명",
  "author": {
    "name": "your-name",
    "email": "your@email.com"
  },
  "homepage": "https://github.com/username/repo",
  "repository": "https://github.com/username/repo",
  "license": "MIT",
  "keywords": ["keyword1", "keyword2"],
  "skills": "./skills/"
}
```

### 3.2 marketplace.json (여러 Plugin 배포 시)
```json
{
  "name": "my-marketplace",
  "owner": {
    "name": "your-name",
    "email": "your@email.com"
  },
  "plugins": [
    {
      "name": "plugin-name",
      "source": "./plugin-directory",
      "description": "Plugin 설명",
      "version": "1.0.0",
      "author": {
        "name": "your-name"
      }
    }
  ]
}
```

**중요**: `marketplace.json`의 plugin `name`과 해당 plugin의 `plugin.json` 내 `name`이 **반드시 일치**해야 합니다.

---

## 4. GitHub에 업로드

```bash
# Git 초기화
git init
git add .
git commit -m "Initial commit: Add plugin structure"

# GitHub 원격 저장소 연결
git remote add origin https://github.com/username/my-plugin.git
git push -u origin main
```

---

## 5. Plugin 사용 방법 (3가지)

### 방법 1: Marketplace를 통한 설치 (공개 배포용)

**배포자:**
```
my-marketplace/
├── .claude-plugin/
│   └── marketplace.json
└── my-plugin/
    ├── .claude-plugin/
    │   └── plugin.json
    └── skills/
```

**사용자:**
```bash
# 1단계: Marketplace 추가
/plugin marketplace add username/repo-name

# 2단계: Plugin 설치
/plugin install plugin-name@marketplace-name
```

### 방법 2: 로컬에 직접 복사 (빠른 사용)

```bash
# 프로젝트별 설치
mkdir -p .claude/skills/my-skill
curl -o .claude/skills/my-skill/SKILL.md \
  https://raw.githubusercontent.com/username/repo/main/skills/my-skill/SKILL.md

# 또는 전역 설치 (모든 프로젝트에서 사용)
mkdir -p ~/.claude/skills/my-skill
# SKILL.md 파일 복사
```

### 방법 3: CLI에서 경로 지정 (개발/테스트용)

```bash
# Plugin 디렉토리를 직접 지정하여 Claude Code 실행
claude --plugin-dir ./my-plugin
```

---

## 6. 실제 예시: ce-part-repo

### 디렉토리 구조
```
ce-part-repo/
├── .claude-plugin/
│   ├── plugin.json           # 루트 plugin (선택)
│   └── marketplace.json      # Marketplace 정의
├── solocheck-skills/
│   ├── .claude-plugin/
│   │   └── plugin.json       # 실제 plugin 매니페스트
│   └── skills/
│       ├── fastapi-router/
│       │   └── SKILL.md
│       ├── pytest-unit/
│       │   └── SKILL.md
│       └── ... (28개 skills)
├── agents/                   # 참고용 원본 문서
├── CLAUDE.md
├── SPEC.md
└── PROMPT_PLAN.md
```

### 설치 방법
```bash
# Marketplace 추가
/plugin marketplace add roo2323/ce-part-repo

# Plugin 설치
/plugin install solocheck-skills@ce-part-repo
```

---

## 7. 문제 해결

### 오류: "Marketplace file not found"
- `marketplace.json` 파일이 `.claude-plugin/` 디렉토리에 있는지 확인

### 오류: "Invalid schema: plugins.0.source"
- `source` 경로가 유효한지 확인 (예: `./plugin-directory`)
- `"."` 대신 명확한 경로 사용

### 오류: Plugin 설치 시 "(no content)"
- `plugin.json`의 `name`과 `marketplace.json`의 plugin `name`이 일치하는지 확인

### Skill이 /메뉴에 표시되지 않음
- `SKILL.md`의 frontmatter 형식 확인
- `user-invocable: false`가 설정되어 있지 않은지 확인

---

## 8. 체크리스트

### Plugin 배포 전 확인사항
- [ ] `SKILL.md`에 유효한 YAML frontmatter가 있음
- [ ] `plugin.json`의 `name` 필드가 설정됨
- [ ] `plugin.json`의 `skills` 경로가 올바름
- [ ] (Marketplace 사용 시) `marketplace.json`과 `plugin.json`의 name 일치
- [ ] GitHub에 push 완료

### 사용자 설치 확인사항
- [ ] `/plugin marketplace add` 성공
- [ ] `/plugin install` 성공
- [ ] `/plugin list`에서 설치된 plugin 확인
- [ ] Skill이 정상 동작하는지 테스트

---

## 9. 요약: 언제 어떤 방법을 사용할까?

| 상황 | 추천 방법 |
|------|----------|
| 팀 내부에서만 사용 | 로컬 복사 또는 --plugin-dir |
| 공개적으로 배포 | Marketplace |
| 여러 Plugin을 하나의 저장소에서 관리 | Marketplace |
| 빠른 테스트/개발 | --plugin-dir |
| 특정 skill만 사용 | 로컬 복사 |

---

## 참고 링크

- [Claude Code 공식 문서](https://docs.anthropic.com/claude-code)
- [예시 저장소: ce-part-repo](https://github.com/roo2323/ce-part-repo)
