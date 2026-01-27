import { ScrollView, Text, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Stack } from 'expo-router';

export default function PrivacyScreen() {
  return (
    <>
      <Stack.Screen options={{ title: '개인정보 처리방침' }} />
      <SafeAreaView style={styles.container} edges={['bottom']}>
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          <Text style={styles.title}>개인정보 처리방침</Text>
          <Text style={styles.date}>시행일: 2026년 1월 27일</Text>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>제1조 (목적)</Text>
            <Text style={styles.content}>
              하루안부(이하 "회사")는 「개인정보 보호법」 제30조에 따라 정보주체의 개인정보를 보호하고 이와 관련한 고충을 신속하고 원활하게 처리할 수 있도록 하기 위하여 다음과 같이 개인정보 처리방침을 수립·공개합니다.
            </Text>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>제2조 (개인정보의 처리 목적)</Text>
            <Text style={styles.content}>
              회사는 다음의 목적을 위하여 개인정보를 처리합니다. 처리하고 있는 개인정보는 다음의 목적 이외의 용도로는 이용되지 않으며, 이용 목적이 변경되는 경우에는 「개인정보 보호법」 제18조에 따라 별도의 동의를 받는 등 필요한 조치를 이행할 예정입니다.
            </Text>
            <Text style={styles.listItem}>1. 회원 가입 및 관리</Text>
            <Text style={styles.listContent}>
              회원 가입의사 확인, 회원제 서비스 제공에 따른 본인 식별·인증, 회원자격 유지·관리, 서비스 부정이용 방지 목적으로 개인정보를 처리합니다.
            </Text>
            <Text style={styles.listItem}>2. 서비스 제공</Text>
            <Text style={styles.listContent}>
              체크인 알림 서비스, 비상연락처 관리 및 알림 발송, 반려동물 정보 관리, 정보 금고 서비스 제공 목적으로 개인정보를 처리합니다.
            </Text>
            <Text style={styles.listItem}>3. 고충처리</Text>
            <Text style={styles.listContent}>
              민원인의 신원 확인, 민원사항 확인, 사실조사를 위한 연락·통지, 처리결과 통보 목적으로 개인정보를 처리합니다.
            </Text>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>제3조 (처리하는 개인정보의 항목)</Text>
            <Text style={styles.content}>회사는 다음의 개인정보 항목을 처리하고 있습니다.</Text>
            <Text style={styles.listItem}>1. 필수 항목</Text>
            <Text style={styles.listContent}>• 이메일 주소, 비밀번호, 이름(닉네임)</Text>
            <Text style={styles.listItem}>2. 선택 항목</Text>
            <Text style={styles.listContent}>
              • 비상연락처 정보 (이름, 이메일, 전화번호, 관계){'\n'}
              • 반려동물 정보 (이름, 종류, 품종, 건강정보 등){'\n'}
              • 정보 금고 저장 정보 (의료, 주거, 보험 등){'\n'}
              • 위치정보 (동의 시에만 수집)
            </Text>
            <Text style={styles.listItem}>3. 자동 수집 항목</Text>
            <Text style={styles.listContent}>
              • 서비스 이용기록, 접속 로그, 기기정보(OS, 앱 버전)
            </Text>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>제4조 (개인정보의 처리 및 보유 기간)</Text>
            <Text style={styles.content}>
              회사는 법령에 따른 개인정보 보유·이용기간 또는 정보주체로부터 개인정보를 수집 시에 동의받은 개인정보 보유·이용기간 내에서 개인정보를 처리·보유합니다.
            </Text>
            <Text style={styles.listItem}>1. 회원 정보</Text>
            <Text style={styles.listContent}>보유기간: 회원 탈퇴 시까지 (탈퇴 후 즉시 파기)</Text>
            <Text style={styles.listItem}>2. 서비스 이용 기록</Text>
            <Text style={styles.listContent}>보유기간: 1년</Text>
            <Text style={styles.listItem}>3. 정보 금고 데이터</Text>
            <Text style={styles.listContent}>보유기간: 회원 탈퇴 시까지 (암호화 저장)</Text>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>제5조 (개인정보의 제3자 제공)</Text>
            <Text style={styles.content}>
              회사는 정보주체의 개인정보를 제2조에서 명시한 범위 내에서만 처리하며, 정보주체의 동의, 법률의 특별한 규정 등 「개인정보 보호법」 제17조 및 제18조에 해당하는 경우에만 개인정보를 제3자에게 제공합니다.
            </Text>
            <Text style={styles.highlight}>
              ※ 비상연락처에 알림을 발송하는 것은 사용자가 직접 등록하고 동의를 받은 연락처에 한하며, 이는 서비스의 핵심 기능입니다.
            </Text>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>제6조 (개인정보의 파기)</Text>
            <Text style={styles.content}>
              회사는 개인정보 보유기간의 경과, 처리목적 달성 등 개인정보가 불필요하게 되었을 때에는 지체없이 해당 개인정보를 파기합니다.
            </Text>
            <Text style={styles.listItem}>파기 방법</Text>
            <Text style={styles.listContent}>
              • 전자적 파일: 복구 및 재생이 불가능하도록 안전하게 삭제{'\n'}
              • 그 밖의 기록물: 파쇄 또는 소각
            </Text>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>제7조 (정보주체의 권리·의무)</Text>
            <Text style={styles.content}>
              정보주체는 회사에 대해 언제든지 개인정보 열람·정정·삭제·처리정지 요구 등의 권리를 행사할 수 있습니다.
            </Text>
            <Text style={styles.listContent}>
              • 앱 내 설정 메뉴에서 직접 정보 수정 및 삭제 가능{'\n'}
              • 회원 탈퇴 시 모든 개인정보 즉시 파기{'\n'}
              • 고객센터를 통한 권리 행사 가능
            </Text>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>제8조 (개인정보의 안전성 확보조치)</Text>
            <Text style={styles.content}>
              회사는 개인정보의 안전성 확보를 위해 다음과 같은 조치를 취하고 있습니다.
            </Text>
            <Text style={styles.listContent}>
              • 비밀번호 암호화 저장 (bcrypt){'\n'}
              • 정보 금고 데이터 암호화 (Fernet 대칭키 암호화){'\n'}
              • SSL/TLS 통신 암호화{'\n'}
              • 접근 권한 관리 및 제한
            </Text>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>제9조 (개인정보 보호책임자)</Text>
            <Text style={styles.content}>
              회사는 개인정보 처리에 관한 업무를 총괄해서 책임지고, 개인정보 처리와 관련한 정보주체의 불만처리 및 피해구제 등을 위하여 아래와 같이 개인정보 보호책임자를 지정하고 있습니다.
            </Text>
            <Text style={styles.listContent}>
              • 담당자: 개인정보 보호책임자{'\n'}
              • 연락처: privacy@dailyhello.app
            </Text>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>제10조 (개인정보 처리방침 변경)</Text>
            <Text style={styles.content}>
              이 개인정보처리방침은 2026년 1월 27일부터 적용됩니다. 변경사항이 있을 경우 앱 내 공지사항을 통해 고지하겠습니다.
            </Text>
          </View>

          <View style={styles.footer}>
            <Text style={styles.footerText}>
              본 서비스는 사망 여부를 확인하지 않습니다.{'\n'}
              긴급 상황 시 112/119 등 공공기관에 연락하세요.
            </Text>
          </View>
        </ScrollView>
      </SafeAreaView>
    </>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  scrollContent: {
    paddingHorizontal: 20,
    paddingVertical: 24,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  date: {
    fontSize: 14,
    color: '#666',
    marginBottom: 24,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  content: {
    fontSize: 14,
    color: '#444',
    lineHeight: 22,
    marginBottom: 8,
  },
  listItem: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginTop: 8,
    marginBottom: 4,
  },
  listContent: {
    fontSize: 14,
    color: '#444',
    lineHeight: 22,
    paddingLeft: 8,
  },
  highlight: {
    fontSize: 13,
    color: '#007AFF',
    backgroundColor: '#f0f8ff',
    padding: 12,
    borderRadius: 8,
    marginTop: 8,
    lineHeight: 20,
  },
  footer: {
    marginTop: 32,
    paddingTop: 24,
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  footerText: {
    fontSize: 12,
    color: '#999',
    textAlign: 'center',
    lineHeight: 18,
  },
});
