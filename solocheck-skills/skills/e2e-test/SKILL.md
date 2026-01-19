---
name: e2e-test
description: E2E 시나리오 테스트 작성 시 사용. QA 전용. 사용자 플로우 테스트.
---

# E2E 시나리오 테스트 체크리스트

## 파일 구조
- [ ] `tests/e2e/test_{scenario}.py` 위치
- [ ] 시나리오별 파일 분리

## 시나리오 유형
- [ ] 사용자 온보딩 (회원가입 → 설정 → 첫 체크인)
- [ ] 핵심 기능 플로우 (CRUD)
- [ ] 알림 발송 플로우 (미체크 → 알림)

## 테스트 원칙
- [ ] 실제 사용자 행동 시뮬레이션
- [ ] 여러 API 연속 호출
- [ ] 상태 변화 확인
- [ ] 최소한의 Mock

---

## E2E 테스트 템플릿
```python
import pytest
from fastapi.testclient import TestClient


class TestUserOnboardingFlow:
    """
    사용자 온보딩 E2E 테스트
    시나리오: 회원가입 → 체크인 설정 → 연락처 등록 → 메시지 작성 → 첫 체크인
    """
    
    def test_complete_onboarding_flow(self, client: TestClient):
        """전체 온보딩 플로우"""
        
        # === 1. 회원가입 ===
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "securepassword123",
                "nickname": "새사용자"
            }
        )
        assert register_response.status_code == 201
        tokens = register_response.json()
        assert "access_token" in tokens
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # === 2. 체크인 설정 ===
        settings_response = client.put(
            "/api/v1/checkin/settings",
            json={"check_in_cycle": 7, "grace_period": 48},
            headers=headers
        )
        assert settings_response.status_code == 200
        settings = settings_response.json()
        assert settings["check_in_cycle"] == 7
        
        # === 3. 비상연락처 등록 ===
        contact_response = client.post(
            "/api/v1/contacts",
            json={
                "name": "가족",
                "contact_type": "email",
                "contact_value": "family@example.com",
                "priority": 1
            },
            headers=headers
        )
        assert contact_response.status_code == 201
        
        # === 4. 개인 메시지 작성 ===
        message_response = client.put(
            "/api/v1/message",
            json={
                "content": "연락이 없다면 확인 부탁드립니다.",
                "is_enabled": True
            },
            headers=headers
        )
        assert message_response.status_code == 200
        
        # === 5. 첫 체크인 ===
        checkin_response = client.post(
            "/api/v1/checkin",
            json={"method": "button_click"},
            headers=headers
        )
        assert checkin_response.status_code == 201
        
        # === 6. 상태 확인 ===
        status_response = client.get("/api/v1/checkin/status", headers=headers)
        assert status_response.status_code == 200
        status = status_response.json()
        assert status["is_overdue"] == False
        
        print("✅ 온보딩 플로우 완료")


class TestContactManagementFlow:
    """연락처 관리 CRUD 플로우"""
    
    def test_contact_crud_flow(self, client, auth_headers):
        """연락처 생성 → 조회 → 수정 → 삭제"""
        
        # 1. 생성
        create_response = client.post(
            "/api/v1/contacts",
            json={
                "name": "친구",
                "contact_type": "email",
                "contact_value": "friend@example.com",
                "priority": 1
            },
            headers=auth_headers
        )
        assert create_response.status_code == 201
        contact_id = create_response.json()["id"]
        
        # 2. 조회
        list_response = client.get("/api/v1/contacts", headers=auth_headers)
        assert list_response.status_code == 200
        assert list_response.json()["count"] == 1
        
        # 3. 수정
        update_response = client.put(
            f"/api/v1/contacts/{contact_id}",
            json={"name": "친한친구", "priority": 2},
            headers=auth_headers
        )
        assert update_response.status_code == 200
        assert update_response.json()["name"] == "친한친구"
        
        # 4. 삭제
        delete_response = client.delete(
            f"/api/v1/contacts/{contact_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == 204
        
        # 5. 삭제 확인
        final_response = client.get("/api/v1/contacts", headers=auth_headers)
        assert final_response.json()["count"] == 0
        
        print("✅ CRUD 플로우 완료")
```

---

## 핵심 시나리오 목록
| 시나리오 | 설명 | 우선순위 |
|----------|------|----------|
| 온보딩 | 회원가입 → 설정 → 첫 체크인 | 🔴 높음 |
| 연락처 CRUD | 생성 → 조회 → 수정 → 삭제 | 🔴 높음 |
| 체크인 플로우 | 체크인 → 상태 확인 | 🔴 높음 |
| 토큰 갱신 | Access 만료 → Refresh | 🟡 중간 |

## 완료 확인
- [ ] 핵심 시나리오 테스트 작성
- [ ] 실제 사용자 플로우 반영
- [ ] 연속 API 호출 검증
- [ ] 테스트 통과 확인
