import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { DashboardView } from './components/DashboardView';
import { VerifyProductView } from './components/VerifyProductView';
import { InspectionsListView } from './components/InspectionsListView';
import { InspectionDetailView } from './components/InspectionDetailView';
import { RulesPlaygroundView } from './components/RulesPlaygroundView';
import { MobileSimulatorView } from './components/MobileSimulatorView';
import { AIModelsView } from './components/AIModelsView';
import { NAWIDashboardView } from './components/oiml/NAWIDashboardView';
import { NAWITestWizardView } from './components/oiml/NAWITestWizardView';
import { NAWIRepositoryView } from './components/oiml/NAWIRepositoryView';
import { OIMLStandardsExplorerView } from './components/oiml/OIMLStandardsExplorerView';
import { UserRole } from './types';
import { api, setAuthToken } from './api';
import { I18nProvider } from './i18n';

function AppContent() {
  const [activeModule, setActiveModule] = useState<'oiml' | 'labelguard'>('oiml');
  const [currentTab, setCurrentTab] = useState('oiml-dashboard');
  const [selectedInspectionId, setSelectedInspectionId] = useState<string | null>(null);
  const [role, setRole] = useState<UserRole>('inspector');
  const [user, setUser] = useState({
    name: 'Rajesh Sharma',
    email: 'inspector@legalmetrology.gov.in',
  });

  // Ensure default authentication on mount for seamless hackathon demo experience
  useEffect(() => {
    async function autoAuthenticate() {
      try {
        const credentials: Record<UserRole, { email: string; pass: string; name: string }> = {
          inspector: { email: 'inspector@legalmetrology.gov.in', pass: 'Inspector@123', name: 'Rajesh Sharma (Inspector)' },
          supervisor: { email: 'supervisor@legalmetrology.gov.in', pass: 'Supervisor@123', name: 'Priya V. Iyer (Assistant Controller)' },
          admin: { email: 'admin@legalmetrology.gov.in', pass: 'Admin@123', name: 'Anil K. Verma (Directorate Admin)' },
          viewer: { email: 'viewer@legalmetrology.gov.in', pass: 'Viewer@123', name: 'Suresh Nair (Verification Officer / Public Viewer)' },
        };
        const active = credentials[role];
        const res = await api.login(active.email, active.pass);
        setUser({ name: active.name, email: active.email });
      } catch (err) {
        console.error('Auto-login error:', err);
      }
    }
    autoAuthenticate();
  }, [role]);

  const handleRoleChange = (newRole: UserRole) => {
    setRole(newRole);
  };

  const handleModuleChange = (mod: 'oiml' | 'labelguard') => {
    setActiveModule(mod);
    if (mod === 'oiml') {
      setCurrentTab('oiml-dashboard');
    } else {
      setCurrentTab('dashboard');
    }
    setSelectedInspectionId(null);
  };

  const handleNavigate = (tab: string, entityId?: string) => {
    if (entityId) {
      setSelectedInspectionId(entityId);
      if (tab === 'oiml-repository') {
        setCurrentTab('oiml-repository');
      } else {
        setCurrentTab('inspection-detail');
      }
    } else {
      setCurrentTab(tab);
    }
  };

  const renderContent = () => {
    // Detail view for Packaged Commodities
    if (currentTab === 'inspection-detail' && selectedInspectionId) {
      return (
        <InspectionDetailView
          inspectionId={selectedInspectionId}
          onBack={() => handleNavigate('inspections')}
        />
      );
    }

    // OIML R 76 NAWI Routes
    if (activeModule === 'oiml' || currentTab.startsWith('oiml-')) {
      switch (currentTab) {
        case 'oiml-dashboard':
          return <NAWIDashboardView onNavigate={handleNavigate} />;
        case 'oiml-wizard':
          return (
            <NAWITestWizardView
              onSuccess={(id) => handleNavigate('oiml-repository', id)}
              onCancel={() => handleNavigate('oiml-dashboard')}
            />
          );
        case 'oiml-repository':
          return (
            <NAWIRepositoryView
              initialSelectedId={selectedInspectionId}
              onNavigateToWizard={() => handleNavigate('oiml-wizard')}
              role={role}
              currentUser={user}
            />
          );
        case 'oiml-standards':
          return <OIMLStandardsExplorerView />;
        default:
          return <NAWIDashboardView onNavigate={handleNavigate} />;
      }
    }

    // Packaged Commodities (Rules 2011) Routes
    switch (currentTab) {
      case 'dashboard':
        return <DashboardView role={role} onNavigate={handleNavigate} />;
      case 'verify':
        return (
          <VerifyProductView
            onInspectionCreated={(id) => handleNavigate('inspection-detail', id)}
          />
        );
      case 'inspections':
        return (
          <InspectionsListView
            onSelectInspection={(id) => handleNavigate('inspection-detail', id)}
          />
        );
      case 'review-queue':
        return (
          <InspectionsListView
            initialFilter="NEEDS_REVIEW"
            onSelectInspection={(id) => handleNavigate('inspection-detail', id)}
          />
        );
      case 'rules':
        return <RulesPlaygroundView />;
      case 'mobile-sim':
        return (
          <MobileSimulatorView
            onInspectionCreated={(id) => handleNavigate('inspection-detail', id)}
          />
        );
      case 'analytics':
        return <DashboardView role={role} onNavigate={handleNavigate} />;
      case 'ai-models':
        return <AIModelsView />;
      default:
        return <DashboardView role={role} onNavigate={handleNavigate} />;
    }
  };

  return (
    <div className="min-h-screen bg-white text-zinc-900 flex flex-col font-sans antialiased selection:bg-black selection:text-white">
      {/* Top Header */}
      <Header
        currentRole={role}
        onRoleChange={handleRoleChange}
        currentUser={user}
        onLogout={() => {
          setAuthToken(null);
          window.location.reload();
        }}
        activeModule={activeModule}
        onModuleChange={handleModuleChange}
      />

      {/* Main App Body */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Navigation Sidebar */}
        <Sidebar
          currentTab={currentTab}
          onSelectTab={(tab) => handleNavigate(tab)}
          role={role}
          activeModule={activeModule}
        />

        {/* Content View Area */}
        <main className="flex-1 overflow-y-auto p-6 lg:p-8 bg-zinc-50/60 bg-dots-pattern">
          {renderContent()}
        </main>
      </div>
    </div>
  );
}

export function App() {
  return (
    <I18nProvider>
      <AppContent />
    </I18nProvider>
  );
}

export default App;
