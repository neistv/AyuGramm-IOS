# AyuGram iOS — полный handoff для следующего Codex

> Этот файл — единая точка входа во весь проект. Его можно отдать другому Codex с доступом к локальному workspace и GitHub. Не проси пользователя повторять уже описанный контекст. Сначала прочитай этот файл целиком, затем проверь актуальное состояние через `git` и `gh`.

## 0. Что от тебя ожидается

Ты продолжаешь разработку нативного AyuGram для iPhone. Работай автономно, но не делай destructive/force операции без явной необходимости и подтверждения. Пользователь владеет репозиторием `neistv/AyuGramm-IOS` и является разработчиком upstream-проекта.

Главные правила:

1. Код и сборки пользователя идут только в `https://github.com/neistv/AyuGramm-IOS` (`origin`).
2. Не запускай сборку, пока пользователь прямо не попросил. Если попросил — запускай и дожидайся результата.
3. Для GitHub используй `gh`, а не ручные запросы к REST API.
4. Официальный upstream `dsn2fvhmn4-lgtm/AyuGramm-IOS` не используй для пользовательских сборок.
5. Не публикуй secrets, API ID/hash, signing credentials, provisioning profile или session data.
6. Не делай `git push --force` и не переписывай `origin/main`: история `origin/main` отличается от official upstream.
7. Патчи обязаны проходить `git diff --check` и чисто применяться к pinned Telegram-iOS.

## 1. Репозитории, remotes и локальные пути

Локальный репозиторий:

```text
/home/neist/AyuGramm-IOS
```

Remotes:

```text
origin   https://github.com/neistv/AyuGramm-IOS.git
fork     https://github.com/neistv/AyuGramm-IOS-fork.git
upstream https://github.com/dsn2fvhmn4-lgtm/AyuGramm-IOS.git
```

Назначение:

- `origin` — личный GitHub пользователя, единственное место для его CI-сборок.
- `upstream` — официальный AyuGramm-IOS, только для синхронизации и upstream PR.
- `fork` — старый fork, использовавшийся для PR №6; новые пользовательские сборки туда не направлять.

Obsidian-контекст проекта:

```text
/home/neist/obsidian-mind/work/active/AyuGram iOS.md
/home/neist/obsidian-mind/brain/Gotchas.md
/home/neist/obsidian-mind/brain/Key Decisions.md
```

Pinned Telegram-iOS:

```text
repository: https://github.com/TelegramMessenger/Telegram-iOS.git
commit: fb0e62ba8a147f0821da6aa63c09da7d79a10111
```

Pin хранится в `upstream.json`. `ci/prepare.py` отказывается накладывать патчи на другой commit.

## 2. Текущее состояние Git

Основная рабочая ветка:

```text
fix/supporter-badge-parity
```

Последние важные коммиты:

```text
da83582 ci: build supporter badge branch
1b31d8a feat: add leading AyuGram developer badges
1cb6894 feat: add deleted opacity control and iOS badge registry
c4a064d fix: restore extera badge parity
7271620 Merge pull request #6 from neistv/feature/desktop-parity
7c8a165 feat: add desktop parity pack (supporter badges, deleted message replies, profile ID/DC card, top banner)
```

Ветка `fix/supporter-badge-parity` запушена в:

```text
origin/fix/supporter-badge-parity
```

`origin/main` имеет отдельную старую линейную историю. В него отдельно, fast-forward коммитом `0b7cc03`, опубликован только runtime JSON-реестр:

```text
assets/ayugram_ios_badges.json
```

Это сделано намеренно: приложение читает raw URL из `main`, а перенос всей feature-ветки в старый `origin/main` потребовал бы опасного переписывания/сложного merge дублирующей истории.

## 3. Текущая GitHub Actions сборка

На момент создания файла запущена сборка:

```text
repo: neistv/AyuGramm-IOS
workflow: Native iOS port
run: 40766590656
run number: 26
branch: fix/supporter-badge-parity
sha: da83582e2a40dc84462089441358abc9a3d9b4b6
configuration: release_arm64
URL: https://github.com/neistv/AyuGramm-IOS/actions/runs/40766590656
```

Последний зафиксированный статус:

- checkout — success;
- Xcode 27.1 selection — success;
- macOS dependencies — success;
- Telegram API secrets validation — success;
- pinned Telegram source fetch — success;
- patch application and source checks — success;
- native dependencies — success;
- Bazel disk cache restore — success;
- `Build native AyuGram port` — in progress с `2026-10-28T20:55:14Z`.

Продолжить наблюдение:

```bash
cd /home/neist/AyuGramm-IOS
gh run watch 40766590656 --repo neistv/AyuGramm-IOS --interval 10 --exit-status
```

Посмотреть структурированный статус:

```bash
gh run view 40766590656 \
  --repo neistv/AyuGramm-IOS \
  --json status,conclusion,url,headBranch,headSha,jobs
```

При failure:

```bash
gh run view 40766590656 --repo neistv/AyuGramm-IOS --log-failed
```

После success посмотреть артефакты:

```bash
gh run view 40766590656 --repo neistv/AyuGramm-IOS
gh run download 40766590656 --repo neistv/AyuGramm-IOS --dir /home/neist/Загрузки/ayugram-run-26
find /home/neist/Загрузки/ayugram-run-26 -maxdepth 3 -type f -print
sha256sum /home/neist/Загрузки/ayugram-run-26/**/*.ipa
```

Если glob `**` не включён в shell, используй `find ... -name '*.ipa' -exec sha256sum {} \;`.

Workflow загружает артефакт с именем примерно:

```text
ayugram-ios-release_arm64-unsigned-26
```

Retention: 7 дней.

## 4. Как устроена сборка

Workflow:

```text
.github/workflows/build.yml
```

Сейчас push trigger временно разрешён для:

```yaml
branches: [main, fix/supporter-badge-parity]
```

Служебный коммит `da83582` добавил feature-ветку в trigger, потому что локальный `gh` сначала показывал устаревшую авторизацию и build был запущен push-событием. На данный момент `gh auth status` уже снова показывает рабочий keyring token с scopes `repo`, `workflow`, `read:org`, `gist`.

После завершения текущей сборки реши вместе с пользователем, оставлять ли branch trigger. Не удаляй его посреди текущего run.

Основные шаги workflow:

1. checkout порта;
2. выбрать `/Applications/Xcode_27.1.app`;
3. проверить macOS build dependencies;
4. проверить `TELEGRAM_API_ID` и `TELEGRAM_API_HASH`;
5. shallow-fetch pinned Telegram-iOS;
6. `python3 ci/prepare.py telegram`;
7. `git -C telegram diff --check`;
8. Python unit tests;
9. `ci/preflight.py`;
10. `ci/test_models.py`;
11. recursive native submodules;
12. Bazel cache;
13. `ci/build.py ... --configuration release_arm64`;
14. upload IPA/log/manifest.

Ожидаемое время:

- с прогретым Bazel cache: обычно 15–25 минут;
- cold build: до 2–3 часов;
- private macOS Actions расходует минуты с множителем 10x; репозиторий сейчас public.

## 5. Порядок применения патчей

`ci/prepare.py` применяет строго по порядку:

```text
patches/ayugram-ghost-mode.patch
patches/ayugram-custom-features.patch
patches/ayugram-followup-features.patch
patches/ayugram-developer-badges.patch
```

Назначение:

### `ayugram-ghost-mode.patch`

Большой основной порт AyuGram:

- ghost mode и локальная история;
- settings UI;
- plugin engine;
- MessageShot;
- UI/appearance;
- deleted-message state;
- полу-прозрачные удалённые (исходно fixed alpha 0.5);
- прочие базовые возможности проекта.

### `ayugram-custom-features.patch`

Desktop parity pack:

- pseudo-quotes для reply на удалённое;
- auto-quote replies;
- supporter badges exteraGram;
- ID/DC/registration date profile card;
- AyuGram top badge/banner;
- настройки этих функций;
- исправление Premium/status/custom badge совместимости.

### `ayugram-followup-features.patch`

Новые доработки текущей сессии:

- настраиваемая прозрачность удалённых 25–99%;
- условный slider под toggle;
- GitHub runtime registry AyuGram iOS;
- cache реестра в Application Support;
- расширяемый диапазон `ThemeSettingsBrightnessItem`.

### `ayugram-developer-badges.patch`

Отдельное размещение developer badges AyuGram iOS:

- новый тип `AyuSupporterBadge.ayuDeveloper`;
- iOS developer badge идёт в leading/verified slot перед ником;
- обычный Premium и Telegram emoji-status остаются справа от имени;
- поддержка в chat list, chat title component/view и profile header;
- тап по значку в профиле показывает верхний overlay;
- `(name)` заменяется актуальным `peer.compactDisplayTitle`.

## 6. Система бейджей — архитектура

### 6.1 exteraGram/AyuGram API

Внешняя база загружается из:

```text
https://update.ayugram.one/rc/current/desktop2
https://api.exteragram.app/api/v1/profiles/compact
```

Разбираются разные сущности:

- `developers`;
- `supporters`;
- `officialChannels`;
- `supporterChannels`;
- `customBadges`.

Их нельзя сплющивать в один `Set<Int64>`, иначе теряются тип, `documentId` и текст.

Типы:

```swift
public enum AyuSupporterBadge: Equatable {
    case developer(text: String?)
    case supporter(text: String?)
    case custom(documentId: Int64, text: String?)
    case ayuDeveloper(documentId: Int64, text: String?)
}
```

### 6.2 AyuGram iOS GitHub registry

Файл:

```text
assets/ayugram_ios_badges.json
```

Runtime URL:

```text
https://raw.githubusercontent.com/neistv/AyuGramm-IOS/main/assets/ayugram_ios_badges.json
```

Формат:

```json
{
  "version": 1,
  "badges": [
    {
      "id": 123456789,
      "documentId": 5341356487631448969,
      "title": "(name) является членом команды разработчиков ayugram-ios"
    }
  ]
}
```

Приоритет:

1. AyuGram iOS GitHub registry;
2. exteraGram `customBadges`;
3. exteraGram developers;
4. exteraGram supporters.

Реестр кешируется в:

```text
Application Support/AyuGram/ayu-ios-badges.json
```

Если GitHub временно недоступен, используется cache. exteraGram cache отдельно:

```text
Application Support/AyuGram/supporters.json
```

Важно: текущая реализация не имеет отдельной UI notification/invalidation после фонового refresh. На первом абсолютно чистом запуске remote badge может появиться после повторного открытия профиля/чата; кеш решает последующие запуски. Если пользователь пожалуется — добавь notification/signal, который инвалидирует видимые peer rows после обновления registry.

### 6.3 Текущие custom developer badges

```text
ID 8276132300
documentId 5341356487631448969
glyph 🌟
title: (name) является членом команды разработчиков ayugram-ios (femboy ebany syka.)

ID 7556953433
documentId 5208467231670812677
glyph 🦋
title: (name) является членом команды разработчиков ayugram-ios

ID 7864640050
documentId 5341356487631448969
glyph 🌟
title: (name) является членом команды разработчиков ayugram-ios
```

Также в registry сейчас есть четыре ранее добавленные записи AyuGram/exteraGram. Не удаляй их без запроса пользователя.

### 6.4 Положение иконок

Требование пользователя:

- все `ayuDeveloper` badges — перед ником;
- Premium star — после ника;
- Telegram custom emoji-status — после ника;
- обычный extera supporter/custom badge остаётся в обычном credibility slot;
- тап по Ayu iOS badge в profile header показывает текст сверху, не нижней строкой профиля.

Реализация использует leading verified-icon slot для `ayuDeveloper`:

- chat list: `currentVerifiedIconContent`;
- chat title: `titleVerifiedIcon`;
- profile header: `verifiedIcon = .ayuDeveloper(...)`.

Не переноси iOS badge обратно в `credibilityIcon`: он окажется после ника и нарушит требование.

## 7. Исправление положения обычного самолётика

Ассеты:

```text
assets/branding/ExteraBadge.imageset/extera_badge.png
assets/branding/ExteraBadge.imageset/extera_badge@2x.png
assets/branding/ExteraBadge.imageset/extera_badge@3x.png
```

Старый PNG 18×16 имел реальный alpha bounding box примерно с `x=5, y=3`, поэтому UIKit центрировал весь холст, а glyph визуально уезжал вправо-вниз.

Новые холсты:

```text
1x 16×16
2x 32×32
3x 48×48
```

Glyph центрирован внутри прозрачного квадратного canvas. Не возвращай старые размеры/поля.

## 8. Premium + supporter/custom badge

Telegram-iOS имеет несколько визуальных слотов:

- `statusIcon` — Telegram custom emoji-status;
- `credibilityIcon` — Premium, verified/scam/fake и другие credibility marks;
- `verifiedIcon`/leading slot — отдельная иконка до имени.

Проблема старой реализации: supporter badge безусловно перезаписывал `credibilityIcon = .premium`, и Premium star пропадала.

Исправление:

- для обычного supporter/custom badge Premium переносится в status slot, supporter остаётся credibility;
- Telegram custom emoji-status не затирается;
- Ayu iOS developer badge использует leading slot и вообще не должен вытеснять Premium.

Проверь это во всех трёх поверхностях: chat list, title, profile.

## 9. Полупрозрачные удалённые и slider

Настройка toggle:

```swift
semiTransparentDeletedMessages: Bool
```

Новая настройка:

```swift
deletedMessageTransparency: Int32 = 50
```

Диапазон жёстко clamp'ится:

```text
25...99
```

UI:

- toggle выключен → slider и percentage label отсутствуют;
- toggle включён → сразу под toggle появляется slider 25–99 и строка с текущим процентом;
- изменение slider сохраняется через `ayuGhostMode.update`;
- `store.signal` перестраивает settings list.

Применение к bubble:

```swift
alpha = max(0.01, 1.0 - CGFloat(transparency) / 100.0)
```

То есть значение означает именно процент прозрачности:

- 25% → alpha 0.75;
- 50% → alpha 0.50;
- 99% → alpha 0.01.

Миграция старых настроек:

- отсутствующее поле → 50%;
- decoded значение clamp 25...99.

## 10. Остальные реализованные функции Desktop Parity

### Reply на удалённое

Telegram сервер отвергает `reply_to_msg_id` удалённого сообщения с `MESSAGE_ID_INVALID`.

Решение:

- извлечь локально сохранённый текст и автора;
- prepend псевдо-цитату;
- `.BlockQuote` на тело;
- `.Bold` на имя;
- сдвинуть UTF-16 entity ranges исходного текста;
- очистить server reply ID;
- разрешить кнопку Reply для `AyuDeletedMessageAttribute`.

### Auto-quote replies

Обычный swipe reply создаёт `EngineMessageReplyQuote`, если включён `autoQuoteReplies`.

### Profile ID/DC/regdate

Показывает:

- user/channel ID;
- media DC и location;
- calendar action;
- live inline query `regdate <userId>` к `@exteraAuthBot`, fallback `@ayugrambot`;
- offline interpolation fallback;
- tap копирует ID.

Не импортируй `Postbox` напрямую в TelegramUI: `PostboxImportCheck` валит CI. Используй `EnginePeer`, `EngineMessage`, TelegramEngine wrappers или inference без явных Postbox типов.

### AyuGram top banner

- `AppBadge@3x.png`, строго только declared scale;
- notch + Dynamic Island;
- Dynamic Island offset `badgeY = 18.0`.

Нельзя класть лишний `AppBadge@2x.png`: `actool` выдаст `unassigned child`.

## 11. Локальные проверки

Быстрый набор:

```bash
cd /home/neist/AyuGramm-IOS
git diff --check
python3 -m unittest discover -s ci/tests -v
```

Сейчас ожидается:

```text
71 tests, OK
```

Полная проверка применения патчей на Linux:

```bash
rm -rf /tmp/ayugram-telegram-verify
git clone --filter=blob:none --no-checkout https://github.com/TelegramMessenger/Telegram-iOS.git /tmp/ayugram-telegram-verify
git -C /tmp/ayugram-telegram-verify checkout --detach fb0e62ba8a147f0821da6aa63c09da7d79a10111
python3 ci/prepare.py /tmp/ayugram-telegram-verify
git -C /tmp/ayugram-telegram-verify diff --check
python3 ci/preflight.py /tmp/ayugram-telegram-verify
python3 ci/test_models.py /tmp/ayugram-telegram-verify
```

Не используй destructive `rm -rf` без проверки точного `/tmp/...` пути. Можно переиспользовать уже существующее `/tmp/ayugram-telegram-verify`, сбросив только собственное временное дерево.

Linux не имеет `swiftc`/полного Xcode toolchain, поэтому окончательная Swift typecheck/build проверяется GitHub Actions macOS job.

## 12. Тесты, добавленные для бейджей

Файл:

```text
ci/tests/test_supporter_badges.py
```

Проверяет:

- extera custom badge metadata;
- ID `1226061708` и его document ID;
- разделение типов;
- Premium slot preservation;
- нормальные размеры PNG;
- уникальность/валидность iOS registry;
- три заданных пользователем ID/document IDs/titles;
- наличие conditional opacity slider;
- диапазон slider;
- raw GitHub registry URL;
- leading slot для `ayuDeveloper`;
- `(name)` replacement.

## 13. Критические Swift/CI gotchas

1. `Signal<T, NoError>.start(next:error:)` не компилируется: error closure недостижим. Используй только `start(next:)`.
2. Прямой `import Postbox` в UI компонентах блокируется CI.
3. Любой trailing whitespace в patch ломает `git diff --check`.
4. Telegram text entity ranges — UTF-16, не Swift character offsets.
5. `EmojiStatusComponent.Content.image` уважает canvas PNG, поэтому внутренние alpha padding визуально сдвигают glyph.
6. `statusIcon = .none` нельзя ставить бездумно: можно уничтожить Telegram custom status.
7. `credibilityIcon` нельзя бездумно перезаписывать: можно уничтожить Premium.
8. Для Ayu iOS developer badge нужен leading slot, не credibility slot.
9. `customBadges` document IDs — `Int64`; JSON через `NSNumber.int64Value`.
10. Runtime GitHub registry должен оставаться в `origin/main`, потому что raw URL указывает на main.
11. GitHub Actions artifact unsigned; установка требует TrollStore на совместимой iOS либо переподпись AltStore/Sideloadly/другим сертификатом.
12. Не обещай безопасность как абсолют: ранее статический аудит и ClamAV были чистыми, но это не математическое доказательство отсутствия вредоносного поведения.

## 14. GitHub CLI cookbook

Проверить auth:

```bash
gh auth status
```

Список последних runs:

```bash
gh run list --repo neistv/AyuGramm-IOS --limit 10
```

Смотреть текущий run:

```bash
gh run watch 40766590656 --repo neistv/AyuGramm-IOS --interval 10 --exit-status
```

Логи упавшего run:

```bash
gh run view 40766590656 --repo neistv/AyuGramm-IOS --log-failed
```

Запустить workflow вручную в будущем:

```bash
gh workflow run build.yml \
  --repo neistv/AyuGramm-IOS \
  --ref fix/supporter-badge-parity \
  -f configuration=release_arm64 \
  -f native_build=true
```

Найти новый run:

```bash
gh run list --repo neistv/AyuGramm-IOS --workflow build.yml --branch fix/supporter-badge-parity --limit 5
```

Скачать артефакт:

```bash
gh run download RUN_ID --repo neistv/AyuGramm-IOS --dir /home/neist/Загрузки/ayugram-RUN_ID
```

## 15. Что сделать сразу после чтения этого файла

1. Выполни `git status --short --branch` в `/home/neist/AyuGramm-IOS`.
2. Выполни `gh auth status`.
3. Проверь run `40766590656` через `gh run view`.
4. Если run ещё идёт — продолжай `gh run watch`, не запускай дубль.
5. Если success — скачай artifact, найди IPA, вычисли SHA-256, сообщи пользователю точный путь и ссылку на run.
6. Если failure — сразу забери `--log-failed`, найди первую настоящую Swift/Bazel ошибку, исправь patch, прогони локальные тесты, commit/push и дождись нового run.
7. Не останавливайся на «CI упал»: пользователь просил готовую сборку.

## 16. Готовый промпт для другого Codex

Скопируй ему это:

```text
Работай в /home/neist/AyuGramm-IOS. Сначала полностью прочитай CODEX_HANDOFF.md. У тебя есть доступ к GitHub через gh. Продолжи текущую задачу до готового результата: проверь GitHub Actions run 40766590656 в neistv/AyuGramm-IOS, дождись завершения, при failure изучи gh run view --log-failed, исправь код/патчи, локально проверь git diff --check и все ci/tests, push только в neistv/AyuGramm-IOS и перезапусти release_arm64. При success скачай IPA через gh run download, вычисли SHA-256 и сообщи точный путь. Не используй официальный upstream для сборки, не force-push origin/main, не публикуй secrets и не запускай дублирующий workflow, если run уже идёт.
```

## 17. Критерий полной готовности

Задача считается завершённой только когда:

- feature branch опубликована в `neistv/AyuGramm-IOS`;
- raw GitHub registry доступен из `origin/main`;
- source checks зелёные;
- native `release_arm64` build зелёный;
- GitHub artifact содержит IPA;
- IPA скачан локально;
- SHA-256 вычислен;
- пользователь получил run URL, artifact name, локальный путь и checksum.

До этого проект находится в состоянии «в работе».
