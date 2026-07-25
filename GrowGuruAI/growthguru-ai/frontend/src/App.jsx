import { useState, useEffect } from 'react';
import Layout from './components/Layout';
import HomeScreen from './screens/HomeScreen';
import UploadScreen from './screens/UploadScreen';
import DashboardScreen from './screens/DashboardScreen';
import GrowthCoachScreen from './screens/GrowthCoachScreen';

// ---------------------------------------------------------------------------
// Session-scoped state management
//
// GOAL:
//   ✔ SPA navigation  → preserve state (no re-fetch, no re-render flicker)
//   ✔ Browser refresh → start a completely clean session
//
// HOW IT WORKS:
//   1. A unique token (PAGE_SESSION_TOKEN) is generated at module evaluation
//      time — i.e. the very moment the JS bundle first runs after a page
//      load or refresh.  It lives only in JS memory (a module-level const).
//   2. On every save we also persist that token inside sessionStorage.
//   3. On load we compare the stored token to the in-memory token.
//      • Same token  → same JS execution context → SPA navigation → restore.
//      • Different   → the page was refreshed (new JS context, new token)
//                      → discard the old data and start fresh.
// ---------------------------------------------------------------------------
const SESSION_KEY  = 'growguru_session';
const TOKEN_KEY    = 'growguru_page_token';

// Generated once per JS execution context (survives SPA nav, reset on refresh)
const PAGE_SESSION_TOKEN = Math.random().toString(36).slice(2);

function loadSession() {
  try {
    const storedToken = sessionStorage.getItem(TOKEN_KEY);
    // Mismatch → page was refreshed → ignore stale data
    if (storedToken !== PAGE_SESSION_TOKEN) return null;
    const raw = sessionStorage.getItem(SESSION_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function saveSession(state) {
  try {
    // Always stamp the current token so subsequent reads can verify it
    sessionStorage.setItem(TOKEN_KEY, PAGE_SESSION_TOKEN);
    sessionStorage.setItem(SESSION_KEY, JSON.stringify(state));
  } catch {
    // Storage quota exceeded — silently ignore
  }
}

export default function App() {
  // Rehydrate from sessionStorage on first render (cleared automatically on refresh)
  const session = loadSession();

  // Global App State
  const [currentScreen, setCurrentScreen] = useState(session?.currentScreen || 'home');
  const [businessProfile, setBusinessProfile] = useState(
    session?.businessProfile || {
      businessName: '',
      businessType: '',
      targetAudience: '',
      businessGoals: '',
    }
  );

  // Data state
  const [csvData, setCsvData] = useState(session?.csvData || null);
  const [kpis, setKpis] = useState(session?.kpis || null);
  const [fileId, setFileId] = useState(session?.fileId || null);
  const [growthData, setGrowthData] = useState(session?.growthData || null);
  // GrowthLens (ScenarioSimulator) — lifted here so it survives SPA navigation
  const [scenarioData, setScenarioData] = useState(session?.scenarioData || null);

  // Persist all state to sessionStorage whenever any piece changes
  useEffect(() => {
    saveSession({ currentScreen, businessProfile, csvData, kpis, fileId, growthData, scenarioData });
  }, [currentScreen, businessProfile, csvData, kpis, fileId, growthData, scenarioData]);

  // Navigation handlers
  const handleProfileComplete = () => {
    setCurrentScreen('upload');
  };

  const handleDataReady = async ({ rawRows, kpis: newKpis, headers, fileId }) => {
    setCsvData(rawRows);
    setKpis(newKpis);
    setFileId(fileId);
    setGrowthData(null);   // New CSV → clear stale growth plan
    setScenarioData(null); // New CSV → clear stale GrowthLens data
    setCurrentScreen('dashboard');
  };

  const handleNavigateToCoach = () => {
    setCurrentScreen('coach');
  };

  // Render current screen
  const renderScreen = () => {
    switch (currentScreen) {
      case 'home':
        return (
          <HomeScreen
            businessProfile={businessProfile}
            setBusinessProfile={setBusinessProfile}
            onContinue={handleProfileComplete}
          />
        );
      case 'upload':
        return (
          <UploadScreen
            businessProfile={businessProfile}
            setBusinessProfile={setBusinessProfile}
            onDataReady={handleDataReady}
            onNavigate={setCurrentScreen}
          />
        );
      case 'dashboard':
        return (
          <DashboardScreen
            businessProfile={businessProfile}
            kpis={kpis}
            productData={kpis?.productData}
            onNavigateToCoach={handleNavigateToCoach}
          />
        );
      case 'coach':
        return (
          <GrowthCoachScreen
            businessProfile={businessProfile}
            setBusinessProfile={setBusinessProfile}
            kpis={kpis}
            fileId={fileId}
            growthData={growthData}
            setGrowthData={setGrowthData}
            scenarioData={scenarioData}
            setScenarioData={setScenarioData}
            onNavigate={setCurrentScreen}
          />
        );
      default:
        return <HomeScreen businessProfile={businessProfile} setBusinessProfile={setBusinessProfile} onContinue={handleProfileComplete} />;
    }
  };

  return (
    <Layout currentScreen={currentScreen} setCurrentScreen={setCurrentScreen}>
      {renderScreen()}
    </Layout>
  );
}
