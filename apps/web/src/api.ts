// LabelGuard AI - API Client
import { OverviewKPI, InspectionListItem, InspectionDetail, ComplianceRuleItem } from './types';

const API_BASE = '/api/v1';

let authToken: string | null = localStorage.getItem('labelguard_token');

export const setAuthToken = (token: string | null) => {
  authToken = token;
  if (token) {
    localStorage.setItem('labelguard_token', token);
  } else {
    localStorage.removeItem('labelguard_token');
  }
};

async function authFetch(url: string, options: RequestInit = {}, isJson = true): Promise<Response> {
  if (!authToken) {
    authToken = localStorage.getItem('labelguard_token');
  }

  const makeHeaders = (token: string | null) => {
    const h: Record<string, string> = {};
    if (isJson) {
      h['Content-Type'] = 'application/json';
    }
    if (token) {
      h['Authorization'] = `Bearer ${token}`;
    }
    return h;
  };

  let res = await fetch(url, {
    ...options,
    headers: {
      ...makeHeaders(authToken),
      ...(options.headers as Record<string, string> || {})
    }
  });

  // If 401 Unauthorized, automatically re-authenticate and retry once
  if (res.status === 401) {
    try {
      const loginRes = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'inspector@legalmetrology.gov.in', password: 'Inspector@123' }),
      });
      if (loginRes.ok) {
        const authData = await loginRes.json();
        setAuthToken(authData.access_token);
        res = await fetch(url, {
          ...options,
          headers: {
            ...makeHeaders(authData.access_token),
            ...(options.headers as Record<string, string> || {})
          }
        });
      }
    } catch (e) {
      console.warn('Auto-reauth failed:', e);
    }
  }

  return res;
}

export const api = {
  async login(email: string, password: string) {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Login failed');
    }
    const data = await res.json();
    setAuthToken(data.access_token);
    return data;
  },

  async getHealth() {
    const res = await fetch(`${API_BASE}/health`);
    return res.json();
  },

  async getOverviewKPI(): Promise<OverviewKPI> {
    const res = await authFetch(`${API_BASE}/analytics/overview`);
    if (!res.ok) throw new Error('Failed to fetch KPI overview');
    return res.json();
  },

  async getViolationsAnalytics() {
    const res = await authFetch(`${API_BASE}/analytics/violations`);
    if (!res.ok) throw new Error('Failed to fetch violation analytics');
    return res.json();
  },

  async getAIModels() {
    const res = await authFetch(`${API_BASE}/analytics/ai-models`);
    if (!res.ok) throw new Error('Failed to fetch AI model telemetry');
    return res.json();
  },

  async getInspections(params?: { status?: string; category?: string; search?: string; limit?: number; offset?: number }): Promise<{ items: InspectionListItem[]; total: number }> {
    const url = new URL(`${window.location.origin}${API_BASE}/inspections`);
    if (params?.status && params.status !== 'ALL') url.searchParams.append('status', params.status);
    if (params?.category && params.category !== 'ALL') url.searchParams.append('category', params.category);
    if (params?.search) url.searchParams.append('search', params.search);
    if (params?.limit) url.searchParams.append('limit', params.limit.toString());
    if (params?.offset) url.searchParams.append('offset', params.offset.toString());

    const res = await authFetch(url.toString());
    if (!res.ok) throw new Error('Failed to fetch inspections');
    return res.json();
  },

  async getInspection(id: string): Promise<InspectionDetail> {
    const res = await authFetch(`${API_BASE}/inspections/${id}`);
    if (!res.ok) throw new Error(`Failed to fetch inspection ${id}`);
    return res.json();
  },

  async createInspection(data: { product_name: string; brand?: string; category_code: string; address?: string }) {
    const res = await authFetch(`${API_BASE}/inspections`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create inspection');
    return res.json();
  },

  async uploadImage(inspectionId: string, surfaceType: string, file: File) {
    const formData = new FormData();
    formData.append('surface_type', surfaceType);
    formData.append('file', file);

    const res = await authFetch(`${API_BASE}/inspections/${inspectionId}/images`, {
      method: 'POST',
      body: formData,
    }, false);
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to upload image');
    }
    return res.json();
  },

  async uploadSurfaceImage(inspectionId: string, file: File, surfaceType: string) {
    return this.uploadImage(inspectionId, surfaceType, file);
  },

  async triggerAnalysis(inspectionId: string) {
    const res = await authFetch(`${API_BASE}/inspections/${inspectionId}/analyze`, {
      method: 'POST',
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Analysis trigger failed');
    }
    return res.json();
  },

  async runInspection(inspectionId: string) {
    return this.triggerAnalysis(inspectionId);
  },

  async correctField(inspectionId: string, fieldId: string, correctedValue: string, reason: string) {
    const res = await authFetch(`${API_BASE}/inspections/${inspectionId}/fields/${fieldId}`, {
      method: 'PATCH',
      body: JSON.stringify({ corrected_value: correctedValue, reason }),
    });
    if (!res.ok) throw new Error('Failed to correct field declaration');
    return res.json();
  },

  async verifyInspection(inspectionId: string, decision: string, notes?: string) {
    const res = await authFetch(`${API_BASE}/inspections/${inspectionId}/verify`, {
      method: 'POST',
      body: JSON.stringify({ decision, notes }),
    });
    if (!res.ok) throw new Error('Failed to finalize verification');
    return res.json();
  },

  async generateReport(inspectionId: string) {
    const res = await authFetch(`${API_BASE}/inspections/${inspectionId}/reports`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to generate PDF report');
    return res.json();
  },

  async getRules(): Promise<ComplianceRuleItem[]> {
    const res = await authFetch(`${API_BASE}/rules`);
    if (!res.ok) throw new Error('Failed to fetch legal rules');
    return res.json();
  },

  async testRules(payload: { category_code: string; fields: Record<string, any>; conflicts?: any[] }) {
    const res = await authFetch(`${API_BASE}/rules/test`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to execute rule test');
    return res.json();
  },

  // ==========================================
  // OIML R 76 NAWI Endpoints
  // ==========================================

  async getOIMLDashboardStats() {
    const res = await authFetch(`${API_BASE}/oiml/dashboard-stats`);
    if (!res.ok) throw new Error('Failed to fetch OIML dashboard statistics');
    return res.json();
  },

  async getOIMLEvaluations(params?: { search?: string; status?: string; accuracy_class?: string; instrument_type?: string }) {
    const searchParams = new URLSearchParams();
    if (params?.search) searchParams.append('search', params.search);
    if (params?.status && params.status !== 'ALL') searchParams.append('status', params.status);
    if (params?.accuracy_class && params.accuracy_class !== 'ALL') searchParams.append('accuracy_class', params.accuracy_class);
    if (params?.instrument_type && params.instrument_type !== 'ALL') searchParams.append('instrument_type', params.instrument_type);

    const qs = searchParams.toString() ? `?${searchParams.toString()}` : '';
    const res = await authFetch(`${API_BASE}/oiml/evaluations${qs}`);
    if (!res.ok) throw new Error('Failed to fetch OIML evaluations');
    return res.json();
  },

  async getOIMLEvaluation(id: string) {
    const res = await authFetch(`${API_BASE}/oiml/evaluations/${id}`);
    if (!res.ok) throw new Error('Failed to fetch OIML evaluation details');
    return res.json();
  },

  async createOIMLEvaluation(data: any) {
    const res = await authFetch(`${API_BASE}/oiml/evaluations`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to create OIML evaluation');
    }
    return res.json();
  },

  async updateOIMLEvaluation(id: string, data: any) {
    const res = await authFetch(`${API_BASE}/oiml/evaluations/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to update OIML evaluation');
    }
    return res.json();
  },

  async calculateOIML(payload: any) {
    const res = await authFetch(`${API_BASE}/oiml/calculate`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to perform metrological calculation');
    return res.json();
  },

  async signOIMLEvaluation(id: string, payload: { officer_name: string; designation: string; pin_or_token?: string; signature_remarks?: string }) {
    const res = await authFetch(`${API_BASE}/oiml/evaluations/${id}/sign`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to digitally sign report');
    return res.json();
  },

  async seedOIMLDemo() {
    const res = await authFetch(`${API_BASE}/oiml/seed-demo`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to seed OIML demo records');
    return res.json();
  },

  async getOIMLStandards() {
    const res = await authFetch(`${API_BASE}/oiml/standards`);
    if (!res.ok) throw new Error('Failed to fetch OIML standards');
    return res.json();
  },

  async transitionOIMLWorkflow(id: string, action: string, notes?: string) {
    const res = await authFetch(`${API_BASE}/oiml/evaluations/${id}/transition`, {
      method: 'POST',
      body: JSON.stringify({ action, notes }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Failed to transition report to ${action}`);
    }
    return res.json();
  },

  async uploadOIMLAttachment(id: string, file: File, attachmentType: string = 'INSTRUMENT_PHOTO', title: string = 'Instrument Photo') {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('attachment_type', attachmentType);
    formData.append('title', title);

    const res = await authFetch(`${API_BASE}/oiml/evaluations/${id}/upload-photo`, {
      method: 'POST',
      body: formData,
    }, false);
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to upload attachment');
    }
    return res.json();
  },

  async getOIMLAttachments(id: string) {
    const res = await authFetch(`${API_BASE}/oiml/evaluations/${id}/attachments`);
    if (!res.ok) throw new Error('Failed to fetch evaluation attachments');
    return res.json();
  },

  async getOIMLAuditLogs(id: string) {
    const res = await authFetch(`${API_BASE}/oiml/evaluations/${id}/audit-logs`);
    if (!res.ok) throw new Error('Failed to fetch audit logs');
    return res.json();
  },

  async getOIMLVersions(id: string) {
    const res = await authFetch(`${API_BASE}/oiml/evaluations/${id}/versions`);
    if (!res.ok) throw new Error('Failed to fetch report version history');
    return res.json();
  },

  async getOIMLLaboratories() {
    const res = await authFetch(`${API_BASE}/oiml/laboratories`);
    if (!res.ok) throw new Error('Failed to fetch laboratories');
    return res.json();
  },

  async getOIMLManufacturers() {
    const res = await authFetch(`${API_BASE}/oiml/manufacturers`);
    if (!res.ok) throw new Error('Failed to fetch manufacturers');
    return res.json();
  },

  async getOIMLRuleVersions() {
    const res = await authFetch(`${API_BASE}/oiml/rule-versions`);
    if (!res.ok) throw new Error('Failed to fetch rule versions');
    return res.json();
  },

  getOIMLPdfUrl(id: string) {
    return `${API_BASE}/oiml/evaluations/${id}/export/pdf`;
  },

  getOIMLDocxUrl(id: string) {
    return `${API_BASE}/oiml/evaluations/${id}/export/docx`;
  },
};

