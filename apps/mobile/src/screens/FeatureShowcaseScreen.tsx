import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import type { StackNavigationProp } from '@react-navigation/stack';

type RootStackParamList = {
  Dashboard: undefined;
  Chat: undefined;
  FeatureShowcase: undefined;
};

type FeatureShowcaseScreenNavigationProp = StackNavigationProp<RootStackParamList, 'FeatureShowcase'>;

const FeatureShowcaseScreen = () => {
  const navigation = useNavigation<FeatureShowcaseScreenNavigationProp>();
  
  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Feature Showcase</Text>
      
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>iMessage-style Chat UI</Text>
        <Text style={styles.description}>
          Experience our sleek chat interface with message bubbles, typing indicators, 
          and smooth animations.
        </Text>
        <TouchableOpacity 
          style={styles.button}
          onPress={() => navigation.navigate('Chat')}
        >
          <Text style={styles.buttonText}>Try Chat</Text>
        </TouchableOpacity>
      </View>
      
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Time-based Theme System</Text>
        <Text style={styles.description}>
          Our app automatically adjusts its theme based on the time of day, 
          providing optimal viewing experience.
        </Text>
      </View>
      
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Dynamic Greeting System</Text>
        <Text style={styles.description}>
          Personalized greetings based on time of day and user preferences.
        </Text>
      </View>
      
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Theme Toggle</Text>
        <Text style={styles.description}>
          Switch between light and dark themes with a single tap.
        </Text>
      </View>
      
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Responsive Design</Text>
        <Text style={styles.description}>
          Consistent experience across all device sizes and orientations.
        </Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    padding: 20,
    textAlign: 'center',
  },
  section: {
    backgroundColor: 'white',
    borderRadius: 10,
    padding: 20,
    margin: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  description: {
    fontSize: 16,
    color: '#666',
    lineHeight: 22,
    marginBottom: 15,
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default FeatureShowcaseScreen;
