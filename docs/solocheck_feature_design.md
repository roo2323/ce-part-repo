# SoloCheck 신규 기능 상세 설계서

> 버전: 1.0  
> 작성일: 2026-01-26  
> 대상: 개발팀

---

## 목차

1. [체크인 방식 다양화](#1-체크인-방식-다양화)
2. [긴급 SOS 버튼](#2-긴급-sos-버튼)
3. [반려동물 및 중요 정보 금고](#3-반려동물-및-중요-정보-금고)
4. [체크인 리마인더 커스터마이징](#4-체크인-리마인더-커스터마이징)
5. [신뢰 연락처 사전 동의 시스템](#5-신뢰-연락처-사전-동의-시스템)
6. [위치정보 공유 기능](#6-위치정보-공유-기능-추가)
7. [DB 스키마 확장](#7-db-스키마-확장)
8. [API 설계](#8-api-설계)

---

## 1. 체크인 방식 다양화

### 1.1 위젯 체크인

#### 기능 정의
- iOS/Android 홈 화면 위젯에서 한 번의 탭으로 체크인 완료
- 앱 실행 없이 빠른 체크인 가능

#### 기술 구현

**iOS (WidgetKit)**
```swift
// Widget Intent
struct CheckInIntent: AppIntent {
    static var title: LocalizedStringResource = "안부 체크인"
    
    func perform() async throws -> some IntentResult {
        // API 호출
        try await CheckInService.shared.performCheckIn()
        return .result()
    }
}
```

**Android (Glance)**
```kotlin
// Widget Action
class CheckInWidget : GlanceAppWidget() {
    override suspend fun provideGlance(context: Context, id: GlanceId) {
        provideContent {
            CheckInButton(
                onClick = actionRunCallback<CheckInCallback>()
            )
        }
    }
}
```

#### 위젯 UI 스펙
| 요소 | 스펙 |
|------|------|
| 크기 | Small (2x2) |
| 메인 버튼 | "괜찮아요 ✓" |
| 상태 표시 | 마지막 체크인 시간, D-day 카운터 |
| 색상 | 정상(Green), 주의(Yellow), 위험(Red) |

#### 위젯 상태별 표시
```
┌─────────────────────┐
│  🟢 SoloCheck      │
│                     │
│   [ 괜찮아요 ✓ ]    │
│                     │
│  마지막: 2시간 전    │
│  다음 체크인: D-5    │
└─────────────────────┘
```

---

### 1.2 Push 알림 응답 체크인

#### 기능 정의
- Push 알림 수신 → 알림 클릭 → 앱 실행 시 자동 체크인
- 별도 버튼 클릭 없이 앱 진입만으로 체크인 완료

#### 플로우

```
[서버] 리마인더 푸시 발송
         ↓
[사용자 디바이스] 푸시 알림 표시
  "안부를 확인해주세요! 탭하면 체크인됩니다."
         ↓
[사용자] 푸시 알림 클릭
         ↓
[앱] 딥링크로 앱 실행 (solocheck://checkin?auto=true)
         ↓
[앱] 자동 체크인 API 호출
         ↓
[앱] 체크인 완료 화면 표시 + 햅틱 피드백
```

#### 기술 구현

**Push Payload**
```json
{
  "notification": {
    "title": "안부를 확인해주세요 👋",
    "body": "탭하면 바로 체크인됩니다"
  },
  "data": {
    "type": "checkin_reminder",
    "action": "auto_checkin",
    "deep_link": "solocheck://checkin?auto=true&token={session_token}"
  }
}
```

**딥링크 처리 (React Native)**
```typescript
// App.tsx
import { Linking } from 'react-native';

useEffect(() => {
  const handleDeepLink = async (url: string) => {
    const parsed = parseUrl(url);
    
    if (parsed.path === 'checkin' && parsed.params.auto === 'true') {
      // 자동 체크인 실행
      await performAutoCheckIn(parsed.params.token);
      
      // 완료 피드백
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      showCheckInSuccessToast();
    }
  };

  Linking.addEventListener('url', ({ url }) => handleDeepLink(url));
}, []);
```

#### 보안 고려사항
- `session_token`: 일회성 토큰 (1시간 유효)
- 동일 토큰 재사용 방지
- 앱 백그라운드 → 포그라운드 전환 시에만 동작

---

## 2. 긴급 SOS 버튼

### 2.1 기능 정의

| 항목 | 설명 |
|------|------|
| 목적 | 체크인 주기와 무관하게 즉시 도움 요청 |
| 트리거 | SOS 버튼 3초 길게 누르기 (오작동 방지) |
| 동작 | 비상 연락처에 즉시 알림 + 위치정보(동의 시) |

### 2.2 SOS 알림 단계

```
┌─────────────────────────────────────────────────┐
│                    SOS 발동                      │
├─────────────────────────────────────────────────┤
│                                                 │
│  [1단계] 5초 카운트다운 (취소 가능)              │
│          "5... 4... 3... 2... 1..."             │
│          [취소하기] 버튼 표시                    │
│                                                 │
│  [2단계] 카운트다운 완료 → 즉시 알림 발송        │
│          - 비상 연락처 전원에게 동시 발송        │
│          - 위치정보 포함 (동의 시)               │
│                                                 │
│  [3단계] 발송 완료 확인 화면                    │
│          "알림이 발송되었습니다"                 │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 2.3 SOS 알림 메시지 템플릿

**기본 메시지 (위치정보 미동의)**
```
[SoloCheck 긴급 알림]

{사용자명}님이 긴급 도움을 요청했습니다.

발생 시각: 2026-01-26 14:30:22

즉시 연락을 시도해주세요.
연락이 되지 않을 경우 112/119에 신고를 고려해주세요.
```

**위치정보 포함 메시지**
```
[SoloCheck 긴급 알림]

{사용자명}님이 긴급 도움을 요청했습니다.

발생 시각: 2026-01-26 14:30:22
마지막 위치: 서울특별시 강남구 테헤란로 123
지도 보기: https://maps.google.com/?q=37.5012,127.0396

즉시 연락을 시도해주세요.
```

### 2.4 UI/UX 스펙

**SOS 버튼 위치**
- 메인 화면 하단 고정
- 눈에 잘 띄는 빨간색 계열
- 접근성: 화면 어디서든 1탭 내 도달

**SOS 버튼 상태**
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│             │     │             │     │             │
│   🆘 SOS    │ --> │  3초 유지   │ --> │  카운트다운  │
│             │     │  프로그레스  │     │   5...4...  │
│             │     │             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
   [대기 상태]        [누르는 중]         [발동 대기]
```

### 2.5 백엔드 처리

```python
# services/sos_service.py
class SOSService:
    async def trigger_sos(self, user_id: str, include_location: bool = False):
        user = await self.user_repo.get(user_id)
        
        # 위치정보 조회 (동의 시에만)
        location = None
        if include_location and user.location_consent:
            location = await self.location_service.get_last_location(user_id)
        
        # SOS 이벤트 기록
        sos_event = await self.sos_repo.create({
            "user_id": user_id,
            "triggered_at": datetime.utcnow(),
            "location": location,
            "status": "triggered"
        })
        
        # 비상 연락처 전원에게 알림 발송
        contacts = await self.contact_repo.get_active_contacts(user_id)
        
        for contact in contacts:
            await self.notification_service.send_sos_alert(
                contact=contact,
                user=user,
                location=location,
                sos_event_id=sos_event.id
            )
        
        return sos_event
```

---

## 3. 반려동물 및 중요 정보 금고

### 3.1 반려동물 정보

#### 데이터 모델
```python
class Pet(BaseModel):
    id: UUID
    user_id: UUID
    name: str                    # 이름
    species: PetSpecies          # 종류 (개, 고양이, 기타)
    breed: Optional[str]         # 품종
    birth_date: Optional[date]   # 생년월일
    weight: Optional[float]      # 체중 (kg)
    medical_notes: Optional[str] # 건강 특이사항 (알레르기 등)
    vet_info: Optional[str]      # 단골 동물병원 정보
    caretaker_contact: Optional[str]  # 긴급 시 돌봐줄 분 연락처
    photo_url: Optional[str]     # 사진
    include_in_alert: bool       # 미체크 알림에 포함 여부
    created_at: datetime
    updated_at: datetime

class PetSpecies(str, Enum):
    DOG = "dog"
    CAT = "cat"
    BIRD = "bird"
    FISH = "fish"
    REPTILE = "reptile"
    SMALL_ANIMAL = "small_animal"  # 햄스터, 토끼 등
    OTHER = "other"
```

#### 미체크 알림 시 포함 메시지
```
[추가 정보]
{사용자명}님의 반려동물이 집에 있을 수 있습니다.

🐱 나비 (고양이, 3살)
- 특이사항: 신장 처방식 급여 중
- 단골 병원: OO동물병원 (02-1234-5678)
- 긴급 돌봄 연락처: 김OO (010-xxxx-xxxx)
```

### 3.2 중요 정보 금고 (Info Vault)

#### 정보 카테고리

| 카테고리 | 저장 항목 예시 | 민감도 |
|----------|---------------|--------|
| 의료 정보 | 지병, 복용 약, 알레르기, 혈액형 | 높음 |
| 주거 정보 | 관리사무소 연락처, 현관 비밀번호 힌트 | 중간 |
| 보험 정보 | 보험사, 증권번호, 담당자 연락처 | 높음 |
| 기타 메모 | 자유 형식 텍스트 | 낮음 |

#### 데이터 모델
```python
class InfoVault(BaseModel):
    id: UUID
    user_id: UUID
    category: VaultCategory
    title: str
    content: str                 # AES-256 암호화 저장
    include_in_alert: bool       # 미체크 알림에 포함 여부
    created_at: datetime
    updated_at: datetime

class VaultCategory(str, Enum):
    MEDICAL = "medical"
    HOUSING = "housing"
    INSURANCE = "insurance"
    FINANCIAL = "financial"
    OTHER = "other"
```

#### 암호화 정책
```python
# 저장 시 암호화
from cryptography.fernet import Fernet

class VaultEncryption:
    def __init__(self, master_key: bytes):
        self.fernet = Fernet(master_key)
    
    def encrypt(self, plaintext: str) -> str:
        return self.fernet.encrypt(plaintext.encode()).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        return self.fernet.decrypt(ciphertext.encode()).decode()
```

#### 미체크 알림 시 포함 여부 선택
- 각 정보 항목별로 "알림에 포함" 토글 제공
- 민감한 정보는 기본값 OFF
- 포함 시 경고 문구 표시: "이 정보가 비상 연락처에 전달됩니다"

---

## 4. 체크인 리마인더 커스터마이징

### 4.1 리마인더 설정 옵션

```python
class ReminderSettings(BaseModel):
    user_id: UUID
    
    # 리마인더 시점 (체크인 마감 전 시간)
    reminder_hours_before: List[int]  # 예: [48, 24, 12, 6]
    
    # 알림 시간대 제한
    quiet_hours_start: Optional[time]  # 예: 22:00
    quiet_hours_end: Optional[time]    # 예: 08:00
    
    # 선호 알림 시간
    preferred_time: Optional[time]     # 예: 09:00
    
    # 알림 채널
    push_enabled: bool = True
    email_enabled: bool = False
    
    # 커스텀 메시지
    custom_message: Optional[str]      # 최대 100자
```

### 4.2 리마인더 스케줄 예시

**체크인 주기: 7일 / 리마인더: [48h, 24h, 6h]**

```
Day 1: 체크인 완료 ✓
Day 2: -
Day 3: -
Day 4: -
Day 5: 48시간 전 리마인더 📱
Day 6: 24시간 전 리마인더 📱
Day 7: 6시간 전 리마인더 📱 (09:00, 선호 시간)
       → 체크인 마감
Day 8: 유예 기간 시작
Day 9: 유예 기간 종료 → 비상 연락처 알림 🚨
```

### 4.3 리마인더 메시지 템플릿

**기본 메시지**
```
안녕하세요! 체크인 마감이 {hours}시간 남았어요.
탭 한 번으로 체크인하세요 👋
```

**커스텀 메시지 예시**
```
{custom_message}
체크인 마감까지 {hours}시간 남았습니다.
```

사용자 설정 예: "오늘 하루도 수고했어요 😊"
→ "오늘 하루도 수고했어요 😊 체크인 마감까지 24시간 남았습니다."

### 4.4 Quiet Hours 처리

```python
def should_send_reminder(user_settings: ReminderSettings, current_time: time) -> bool:
    """방해금지 시간 체크"""
    if not user_settings.quiet_hours_start or not user_settings.quiet_hours_end:
        return True
    
    start = user_settings.quiet_hours_start
    end = user_settings.quiet_hours_end
    
    # 자정을 넘는 경우 (예: 22:00 ~ 08:00)
    if start > end:
        return not (current_time >= start or current_time <= end)
    else:
        return not (start <= current_time <= end)
```

---

## 5. 신뢰 연락처 사전 동의 시스템

### 5.1 법적 근거

개인정보보호법 제15조에 따라 제3자(비상 연락처)의 개인정보를 수집하려면 해당 제3자의 동의가 필요합니다.

### 5.2 동의 플로우

```
[사용자] 비상 연락처 등록 시도
         ↓
[시스템] 연락처에 동의 요청 발송 (이메일/SMS)
         ↓
[연락처] 동의 링크 클릭 → 동의 페이지
         ↓
[연락처] 서비스 설명 확인 + 동의 체크
         ↓
[시스템] 동의 완료 → 연락처 활성화
         ↓
[사용자] 연락처 상태 업데이트 확인
```

### 5.3 연락처 상태 관리

```python
class EmergencyContactStatus(str, Enum):
    PENDING = "pending"       # 동의 대기 중
    APPROVED = "approved"     # 동의 완료
    REJECTED = "rejected"     # 동의 거부
    EXPIRED = "expired"       # 동의 요청 만료 (7일)

class EmergencyContact(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    contact_method: ContactMethod  # email / sms
    contact_value: str             # 이메일 주소 또는 전화번호
    priority: int                  # 알림 순서 (1, 2, 3)
    status: EmergencyContactStatus
    consent_requested_at: Optional[datetime]
    consent_responded_at: Optional[datetime]
    consent_token: Optional[str]   # 일회성 동의 토큰
    created_at: datetime
    updated_at: datetime
```

### 5.4 동의 요청 메시지

**이메일 템플릿**
```
제목: [SoloCheck] {사용자명}님이 비상 연락처로 등록을 요청했습니다

안녕하세요,

{사용자명}님이 SoloCheck 서비스의 비상 연락처로 
귀하를 등록하고자 합니다.

📌 SoloCheck 서비스란?
1인 가구 사용자의 장기 미연락 상황을 감지하여
사전에 지정한 비상 연락처에 알림을 전달하는 서비스입니다.

📌 동의 시 어떤 알림을 받게 되나요?
- {사용자명}님이 설정한 기간 동안 앱에 접속하지 않을 경우
- 긴급 SOS 버튼을 누른 경우
위 상황에서 이메일/SMS로 알림을 받게 됩니다.

📌 개인정보 처리
- 귀하의 연락처 정보는 알림 발송 목적으로만 사용됩니다.
- 언제든지 동의를 철회할 수 있습니다.

[동의하기] [거부하기]

본 요청은 7일 후 자동 만료됩니다.
```

### 5.5 동의 페이지 UI

```
┌─────────────────────────────────────────┐
│                                         │
│        SoloCheck 비상 연락처 동의        │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  {사용자명}님이 귀하를 비상 연락처로      │
│  등록하고자 합니다.                      │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ ✓ 서비스 이용약관에 동의합니다    │   │
│  │ ✓ 개인정보 수집·이용에 동의합니다 │   │
│  │ ✓ 알림 수신에 동의합니다         │   │
│  └─────────────────────────────────┘   │
│                                         │
│     [동의하기]     [거부하기]            │
│                                         │
│  ─────────────────────────────────────  │
│                                         │
│  ⚠️ 본 서비스는 사망 여부를 확인하지     │
│     않습니다. 긴급 상황 시 112/119에     │
│     신고해주세요.                        │
│                                         │
└─────────────────────────────────────────┘
```

---

## 6. 위치정보 공유 기능 (추가)

### 6.1 법적 요건

위치정보법 제19조에 따라:
1. 사용자의 명시적 사전 동의 필요
2. 위치정보 이용약관에 명시
3. 제3자 제공 시 사용자에게 즉시 통보
4. 위치기반서비스 사업자 신고 검토

### 6.2 동의 화면

```
┌─────────────────────────────────────────┐
│                                         │
│         📍 위치정보 공유 설정            │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  긴급 상황 시 비상 연락처에게 현재       │
│  위치를 공유하시겠습니까?                │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  🔴 SOS 버튼 발동 시             │   │
│  │  🔴 미체크 알림 발송 시           │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ⚠️ 위치정보는 알림 발송 시에만        │
│     수집되며, 실시간 추적되지 않습니다.  │
│                                         │
│  [ ] 위치정보 이용약관에 동의합니다      │
│      [약관 전문 보기]                   │
│                                         │
│       [동의하기]    [나중에]            │
│                                         │
└─────────────────────────────────────────┘
```

### 6.3 위치정보 처리 플로우

```python
class LocationService:
    async def share_location_with_contacts(
        self, 
        user_id: str, 
        event_type: str  # "sos" | "missed_checkin"
    ):
        user = await self.user_repo.get(user_id)
        
        # 1. 동의 확인
        if not user.location_consent:
            return None
        
        # 2. 현재 위치 조회 (일회성)
        location = await self.get_current_location(user_id)
        
        # 3. 위치정보 제공 기록 저장 (법적 요건)
        await self.log_location_sharing({
            "user_id": user_id,
            "event_type": event_type,
            "location": location,
            "shared_at": datetime.utcnow(),
            "recipients": [c.id for c in user.emergency_contacts]
        })
        
        # 4. 사용자에게 위치 공유 사실 통보 (법적 요건)
        await self.notify_user_location_shared(
            user_id=user_id,
            location=location,
            recipients=[c.name for c in user.emergency_contacts]
        )
        
        return location
```

### 6.4 위치정보 저장 정책

| 항목 | 정책 |
|------|------|
| 저장 기간 | 6개월 (법적 최소 보존 기간) |
| 저장 항목 | 위도, 경도, 수집 시각, 공유 대상 |
| 암호화 | AES-256 |
| 삭제 | 사용자 요청 시 즉시 삭제 가능 |

---

## 7. DB 스키마 확장

### 7.1 신규 테이블

```sql
-- 반려동물 정보
CREATE TABLE pets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    species VARCHAR(50) NOT NULL,
    breed VARCHAR(100),
    birth_date DATE,
    weight DECIMAL(5,2),
    medical_notes TEXT,
    vet_info TEXT,
    caretaker_contact VARCHAR(200),
    photo_url VARCHAR(500),
    include_in_alert BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 정보 금고
CREATE TABLE info_vault (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content_encrypted TEXT NOT NULL,  -- AES-256 암호화
    include_in_alert BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SOS 이벤트 로그
CREATE TABLE sos_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    triggered_at TIMESTAMP NOT NULL,
    cancelled_at TIMESTAMP,
    location_lat DECIMAL(10, 8),
    location_lng DECIMAL(11, 8),
    status VARCHAR(50) NOT NULL,  -- triggered, cancelled, sent
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 리마인더 설정
CREATE TABLE reminder_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reminder_hours_before INTEGER[] DEFAULT '{48, 24, 12}',
    quiet_hours_start TIME,
    quiet_hours_end TIME,
    preferred_time TIME,
    push_enabled BOOLEAN DEFAULT true,
    email_enabled BOOLEAN DEFAULT false,
    custom_message VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- 위치정보 공유 로그 (법적 요건)
CREATE TABLE location_sharing_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,  -- sos, missed_checkin
    location_lat DECIMAL(10, 8),
    location_lng DECIMAL(11, 8),
    recipient_ids UUID[],
    shared_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 7.2 기존 테이블 수정

```sql
-- emergency_contacts 테이블 수정
ALTER TABLE emergency_contacts
ADD COLUMN status VARCHAR(50) DEFAULT 'pending',
ADD COLUMN consent_requested_at TIMESTAMP,
ADD COLUMN consent_responded_at TIMESTAMP,
ADD COLUMN consent_token VARCHAR(255);

-- users 테이블 수정
ALTER TABLE users
ADD COLUMN location_consent BOOLEAN DEFAULT false,
ADD COLUMN location_consent_at TIMESTAMP;
```

---

## 8. API 설계

### 8.1 체크인 API

```yaml
# 위젯/푸시 체크인
POST /api/v1/checkin/quick
Headers:
  Authorization: Bearer {token}
  X-Device-Type: widget | push
Body:
  session_token?: string  # 푸시 체크인 시

Response 200:
  success: true
  checked_in_at: "2026-01-26T14:30:00Z"
  next_deadline: "2026-02-02T14:30:00Z"
```

### 8.2 SOS API

```yaml
# SOS 트리거
POST /api/v1/sos/trigger
Headers:
  Authorization: Bearer {token}
Body:
  include_location: boolean

Response 200:
  sos_event_id: "uuid"
  status: "triggered"
  countdown_seconds: 5

# SOS 취소
POST /api/v1/sos/{sos_event_id}/cancel
Headers:
  Authorization: Bearer {token}

Response 200:
  success: true
  cancelled_at: "2026-01-26T14:30:05Z"
```

### 8.3 반려동물 API

```yaml
# 반려동물 등록
POST /api/v1/pets
Headers:
  Authorization: Bearer {token}
Body:
  name: string
  species: string
  breed?: string
  birth_date?: string
  weight?: number
  medical_notes?: string
  vet_info?: string
  caretaker_contact?: string
  include_in_alert: boolean

# 반려동물 목록
GET /api/v1/pets
Headers:
  Authorization: Bearer {token}

# 반려동물 수정
PUT /api/v1/pets/{pet_id}

# 반려동물 삭제
DELETE /api/v1/pets/{pet_id}
```

### 8.4 정보 금고 API

```yaml
# 정보 등록
POST /api/v1/vault
Headers:
  Authorization: Bearer {token}
Body:
  category: string
  title: string
  content: string
  include_in_alert: boolean

# 정보 목록
GET /api/v1/vault
Headers:
  Authorization: Bearer {token}

# 정보 상세 (복호화된 내용)
GET /api/v1/vault/{vault_id}
Headers:
  Authorization: Bearer {token}

# 정보 수정
PUT /api/v1/vault/{vault_id}

# 정보 삭제
DELETE /api/v1/vault/{vault_id}
```

### 8.5 비상 연락처 동의 API

```yaml
# 동의 요청 발송
POST /api/v1/contacts/{contact_id}/request-consent
Headers:
  Authorization: Bearer {token}

Response 200:
  success: true
  consent_expires_at: "2026-02-02T14:30:00Z"

# 동의 처리 (연락처가 접근)
POST /api/v1/consent/{token}
Body:
  approved: boolean

Response 200:
  success: true
  message: "동의가 완료되었습니다" | "동의가 거부되었습니다"

# 동의 상태 확인
GET /api/v1/contacts/{contact_id}/consent-status
Headers:
  Authorization: Bearer {token}

Response 200:
  status: "pending" | "approved" | "rejected" | "expired"
  requested_at: "2026-01-26T14:30:00Z"
  responded_at?: "2026-01-27T10:00:00Z"
```

### 8.6 리마인더 설정 API

```yaml
# 리마인더 설정 조회
GET /api/v1/settings/reminder
Headers:
  Authorization: Bearer {token}

Response 200:
  reminder_hours_before: [48, 24, 12]
  quiet_hours_start: "22:00"
  quiet_hours_end: "08:00"
  preferred_time: "09:00"
  push_enabled: true
  email_enabled: false
  custom_message: "오늘 하루도 수고했어요 😊"

# 리마인더 설정 수정
PUT /api/v1/settings/reminder
Headers:
  Authorization: Bearer {token}
Body:
  reminder_hours_before?: number[]
  quiet_hours_start?: string
  quiet_hours_end?: string
  preferred_time?: string
  push_enabled?: boolean
  email_enabled?: boolean
  custom_message?: string
```

---

## 부록: 개발 우선순위

| 순위 | 기능 | 예상 공수 | 의존성 |
|------|------|----------|--------|
| 1 | 푸시 알림 체크인 | 3일 | FCM 설정 |
| 2 | 리마인더 커스터마이징 | 2일 | 배치 로직 수정 |
| 3 | 신뢰 연락처 동의 | 5일 | 이메일 서비스 |
| 4 | 위젯 체크인 | 5일 | 네이티브 개발 |
| 5 | SOS 버튼 | 4일 | 위치정보 연동 |
| 6 | 반려동물 정보 | 3일 | - |
| 7 | 정보 금고 | 4일 | 암호화 모듈 |
| 8 | 위치정보 공유 | 5일 | 위치정보 이용약관 |

**총 예상 공수: 약 31일 (1.5 스프린트)**

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| 1.0 | 2026-01-26 | 최초 작성 | Claude |