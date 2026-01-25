import { View, Text, ScrollView, TouchableOpacity, Switch } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { useUserStore } from '@/stores/userStore';
import { useGamificationStore } from '@/stores/gamificationStore';
import XPBar from '@/components/XPBar';

export default function ProfileScreen() {
  const router = useRouter();
  const { displayName, level, totalXP, gradeLevel, setGradeLevel } = useUserStore();
  const { totalBadges, currentStreak, dailyStreak } = useGamificationStore();

  const ProfileStat = ({ icon, label, value, color }: any) => (
    <View className="bg-white rounded-xl p-4 flex-1 mx-1 items-center shadow-sm">
      <Ionicons name={icon} size={28} color={color} />
      <Text className="text-2xl font-bold text-gray-800 mt-1">{value}</Text>
      <Text className="text-xs text-gray-500">{label}</Text>
    </View>
  );

  const SettingsItem = ({ icon, label, onPress, rightElement }: any) => (
    <TouchableOpacity
      className="bg-white flex-row items-center p-4 border-b border-gray-100"
      onPress={onPress}
    >
      <View className="bg-gray-100 rounded-full p-2">
        <Ionicons name={icon} size={20} color="#4F46E5" />
      </View>
      <Text className="flex-1 ml-3 text-gray-800 font-medium">{label}</Text>
      {rightElement || <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />}
    </TouchableOpacity>
  );

  return (
    <ScrollView className="flex-1 bg-gray-50">
      {/* Profile Header */}
      <View className="bg-primary-600 px-4 pt-6 pb-8 items-center">
        <View className="bg-white rounded-full p-1 mb-3">
          <View className="bg-primary-100 rounded-full w-24 h-24 items-center justify-center">
            <Text className="text-4xl font-bold text-primary-600">
              {(displayName || 'O')[0].toUpperCase()}
            </Text>
          </View>
        </View>
        <Text className="text-white text-2xl font-bold">{displayName || 'Ogrenci'}</Text>
        <Text className="text-white/80">Seviye {level}</Text>

        <View className="w-full mt-4">
          <XPBar />
        </View>
      </View>

      {/* Stats Row */}
      <View className="flex-row px-4 -mt-4">
        <ProfileStat icon="star" label="Seviye" value={level} color="#4F46E5" />
        <ProfileStat icon="flame" label="Seri" value={currentStreak} color="#F59E0B" />
        <ProfileStat icon="trophy" label="Rozet" value={totalBadges} color="#10B981" />
      </View>

      {/* Grade Level Selector */}
      <View className="px-4 mt-6">
        <Text className="text-xl font-bold text-gray-800 mb-4">Sinif Seviyesi</Text>
        <View className="bg-white rounded-xl p-4 shadow-sm">
          <View className="flex-row flex-wrap">
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((grade) => (
              <TouchableOpacity
                key={grade}
                className={`w-1/4 p-2`}
                onPress={() => setGradeLevel(grade)}
              >
                <View
                  className={`rounded-xl p-3 items-center ${
                    gradeLevel === grade
                      ? 'bg-primary-600'
                      : 'bg-gray-100'
                  }`}
                >
                  <Text
                    className={`font-bold ${
                      gradeLevel === grade ? 'text-white' : 'text-gray-600'
                    }`}
                  >
                    {grade}
                  </Text>
                </View>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      </View>

      {/* Settings */}
      <View className="px-4 mt-6 mb-8">
        <Text className="text-xl font-bold text-gray-800 mb-4">Ayarlar</Text>
        <View className="bg-white rounded-xl overflow-hidden shadow-sm">
          <SettingsItem
            icon="notifications"
            label="Bildirimler"
            rightElement={<Switch value={true} />}
          />
          <SettingsItem
            icon="volume-high"
            label="Ses Efektleri"
            rightElement={<Switch value={true} />}
          />
          <SettingsItem
            icon="moon"
            label="Karanlik Mod"
            rightElement={<Switch value={false} />}
          />
          <SettingsItem icon="language" label="Dil" />
          <SettingsItem icon="help-circle" label="Yardim" />
          <SettingsItem icon="information-circle" label="Hakkinda" />
        </View>
      </View>

      {/* Logout */}
      <TouchableOpacity className="mx-4 mb-8 bg-red-50 p-4 rounded-xl flex-row items-center justify-center">
        <Ionicons name="log-out" size={20} color="#EF4444" />
        <Text className="text-red-500 font-medium ml-2">Cikis Yap</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}
