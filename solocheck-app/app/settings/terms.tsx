import { ScrollView, Text, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function TermsScreen() {
  return (
    <SafeAreaView style={styles.container} edges={['bottom']}>
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          <Text style={styles.title}>하루안부 이용약관</Text>
          <Text style={styles.date}>시행일: 2026년 1월 27일</Text>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>제1조 (목적)</Text>
            <Text style={styles.content}>
              본 약관은 하루안부(이하 "회사")가 제공하는 하루안부 서비스(이하 "서비스")의 이용조건 및 절차, 회사와 이용자의 권리, 의무 및 책임사항을 규정함을 목적으로 합니다.
            </Text>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>제2조 (용어의 정의)</Text>
            <Text style={styles.listContent}>
              1. "서비스"란 회사가 제공하는 체크인 알림 서비스 및 관련 부가서비스를 의미합니다.{'\n\n'}
              2. "이용자"란 본 약관에 동의하고 서비스를 이용하는 자를 의미합니다.{'\n\n'}
              3. "체크인"이란 이용자가 앱을 통해 자신의 안부를 확인하는 행위를 의미합니다.{'\n\n'}
              4. "비상연락처"란 이용자가 지정한 긴급 시 연락받을 사람을 의미합니다.
            </Text>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>제3조 (약관의 효력 및 변경)</Text>
            <Text style={styles.content}>
              1. 본 약관은 서비스 화면에 게시하거나 기타의 방법으로 이용자에게 공지함으로써 효력을 발생합니다.{'\n\n'}
              2. 회사는 필요한 경우 관련 법령을 위배하지 않는 범위에서 본 약관을 변경할 수 있습니다.{'\n\n'}
              3. 약관이 변경되는 경우 회사는 변경사항을 시행일 7일 전부터 앱 내 공지사항을 통해 공지합니다.
            </Text>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>제4조 (서비스의 내용)</Text>
            <Text style={styles.content}>
              회사는 다음과 같은 서비스를 제공합니다.
            </Text>
            <Text style={styles.listContent}>
              1. 체크인 서비스: 정해진 주기에 따른 안부 확인{'\n\n'}
              2. 비상연락처 알림: 체크인 미완료 시 지정 연락처에 알림 발송{'\n\n'}
              3. 반려동물 정보 관리: 반려동물 정보 등록 및 비상 시 전달{'\n\n'}
              4. 정보 금고: 중요 정보 암호화 저장{'\n\n'}
              5. SOS 긴급 알림: 긴급 상황 시 즉시 알림 발송
            </Text>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>제5조 (서비스의 제한)</Text>
            <Text style={styles.highlight}>
              본 서비스는 다음을 포함하지 않습니다:{'\n\n'}
              • 사망 확인 또는 인증 기능{'\n'}
              • 의료 서비스 또는 응급 구조 서비스{'\n'}
              • 법적 효력이 있는 유언장 또는 유서 기능{'\n'}
              • 112/119 등 공공기관과의 자동 연동{'\n\n'}
              긴급 상황 시에는 반드시 112/119 등 공공기관에 직접 연락하시기 바랍니다.
            </Text>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>제6조 (이용자의 의무)</Text>
            <Text style={styles.content}>
              이용자는 다음 행위를 하여서는 안 됩니다.
            </Text>
            <Text style={styles.listContent}>
              1. 타인의 정보를 도용하는 행위{'\n\n'}
              2. 서비스를 이용하여 법령 또는 공서양속에 위반되는 행위{'\n\n'}
              3. 서비스의 운영을 방해하는 행위{'\n\n'}
              4. 비상연락처로 동의 없이 타인을 등록하는 행위{'\n\n'}
              5. 허위 또는 과장된 정보를 등록하는 행위
            </Text>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>제7조 (비상연락처 등록 및 동의)</Text>
            <Text style={styles.content}>
              1. 이용자는 비상연락처를 등록할 때 해당 연락처의 동의를 받아야 합니다.{'\n\n'}
              2. 회사는 비상연락처로 등록된 자에게 등록 사실을 안내합니다.{'\n\n'}
              3. 비상연락처 등록자는 언제든지 동의를 철회할 수 있습니다.
            </Text>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>제8조 (서비스 이용료)</Text>
            <Text style={styles.content}>
              본 서비스는 무료로 제공됩니다. 단, 향후 유료 서비스가 추가될 경우 사전에 안내드립니다.
            </Text>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>제9조 (회사의 의무)</Text>
            <Text style={styles.content}>
              1. 회사는 관련 법령과 본 약관이 금지하는 행위를 하지 않으며, 지속적이고 안정적으로 서비스를 제공하기 위해 노력합니다.{'\n\n'}
              2. 회사는 이용자의 개인정보를 보호하기 위해 보안 시스템을 갖추며, 개인정보 처리방침을 준수합니다.{'\n\n'}
              3. 회사는 서비스 이용과 관련하여 이용자의 불만 또는 피해구제 요청을 적절하게 처리합니다.
            </Text>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>제10조 (면책조항)</Text>
            <Text style={styles.content}>
              1. 회사는 천재지변, 전쟁, 기간통신사업자의 서비스 중단 등 불가항력적인 사유로 서비스를 제공할 수 없는 경우 책임이 면제됩니다.{'\n\n'}
              2. 회사는 이용자의 귀책사유로 인한 서비스 이용 장애에 대해 책임지지 않습니다.{'\n\n'}
              3. 회사는 이용자가 등록한 정보의 정확성, 진실성에 대해 책임지지 않습니다.{'\n\n'}
              4. 알림 발송 후 발생하는 결과에 대해서는 회사가 책임지지 않습니다.
            </Text>
            <Text style={styles.highlight}>
              본 서비스는 사망 여부를 확인하지 않으며, 알림은 '연락 두절' 기준으로만 발송됩니다. 서비스 알림을 통한 어떠한 법적 판단도 이루어지지 않습니다.
            </Text>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>제11조 (회원 탈퇴 및 자격 상실)</Text>
            <Text style={styles.content}>
              1. 이용자는 언제든지 서비스 내 탈퇴 기능을 통해 회원 탈퇴를 요청할 수 있습니다.{'\n\n'}
              2. 회원 탈퇴 시 모든 개인정보는 즉시 파기됩니다.{'\n\n'}
              3. 회사는 이용자가 본 약관을 위반한 경우 사전 통지 후 이용 자격을 제한하거나 상실시킬 수 있습니다.
            </Text>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>제12조 (분쟁 해결)</Text>
            <Text style={styles.content}>
              1. 회사와 이용자 간 발생한 분쟁에 관하여는 당사자 간 협의에 의해 해결합니다.{'\n\n'}
              2. 협의가 이루어지지 않을 경우 관할 법원은 회사 소재지 관할 법원으로 합니다.
            </Text>
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>부칙</Text>
            <Text style={styles.content}>
              본 약관은 2026년 1월 27일부터 시행합니다.
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
  listContent: {
    fontSize: 14,
    color: '#444',
    lineHeight: 24,
    paddingLeft: 8,
  },
  highlight: {
    fontSize: 13,
    color: '#d9534f',
    backgroundColor: '#fff5f5',
    padding: 12,
    borderRadius: 8,
    marginTop: 8,
    lineHeight: 20,
    borderLeftWidth: 3,
    borderLeftColor: '#d9534f',
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
