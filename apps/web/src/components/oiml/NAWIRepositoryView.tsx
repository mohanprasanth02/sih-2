import React, { useState, useEffect } from 'react';
import {
  Scale,
  Search,
  Filter,
  FileText,
  Download,
  CheckCircle2,
  XCircle,
  Clock,
  ShieldCheck,
  ExternalLink,
  ChevronRight,
  Eye,
  Camera,
  Calendar,
  Building,
  RefreshCw,
  Award,
  Hash,
  X,
  Send,
  AlertTriangle,
  History,
  Paperclip,
  UploadCloud,
  FileCheck,
  Lock,
  MessageSquare,
  FileDown
} from 'lucide-react';
import { NAWIModelEvaluation, AccuracyClassType, UserRole, NAWIAttachment, OIMLAuditLog, OIMLReportVersion } from '../../types';
import { api } from '../../api';

interface NAWIRepositoryViewProps {
  initialSelectedId?: string | null;
  onNavigateToWizard: () => void;
  role?: UserRole;
  currentUser?: { name: string; email: string };
}

export const NAWIRepositoryView: React.FC<NAWIRepositoryViewProps> = ({
  initialSelectedId,
  onNavigateToWizard,
  role = 'inspector',
  currentUser = { name: 'Rajesh Sharma', email: 'inspector@legalmetrology.gov.in' }
}) => {
  const [evaluations, setEvaluations] = useState<NAWIModelEvaluation[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [classFilter, setClassFilter] = useState('ALL');
  const [selectedEvaluation, setSelectedEvaluation] = useState<NAWIModelEvaluation | null>(null);

  // Tabs in Detail Drawer
  const [activeTab, setActiveTab] = useState<'tests' | 'attachments' | 'audit' | 'versions'>('tests');

  // Modals & Actions
  const [signingModalOpen, setSigningModalOpen] = useState(false);
  const [signerName, setSignerName] = useState(currentUser.name);
  const [signerRole, setSignerRole] = useState(role === 'supervisor' ? 'Assistant Controller (Metrology)' : 'Metrological Testing Officer');
  const [signing, setSigning] = useState(false);

  const [transitionNotesModal, setTransitionNotesModal] = useState<{ open: boolean; action: string; title: string; prompt: string } | null>(null);
  const [transitionNotes, setTransitionNotes] = useState('');
  const [transitioning, setTransitioning] = useState(false);

  // Attachments State
  const [attachments, setAttachments] = useState<NAWIAttachment[]>([]);
  const [loadingAttachments, setLoadingAttachments] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadTitle, setUploadTitle] = useState('');
  const [uploadType, setUploadType] = useState('INSTRUMENT_PHOTO');
  const [uploading, setUploading] = useState(false);

  // Audit Logs & Versions State
  const [auditLogs, setAuditLogs] = useState<OIMLAuditLog[]>([]);
  const [loadingAudit, setLoadingAudit] = useState(false);
  const [versions, setVersions] = useState<OIMLReportVersion[]>([]);
  const [loadingVersions, setLoadingVersions] = useState(false);

  const fetchEvaluations = async () => {
    try {
      setLoading(true);
      const res = await api.getOIMLEvaluations({
        search,
        status: statusFilter,
        accuracy_class: classFilter,
      });
      setEvaluations(res);

      if (initialSelectedId) {
        const found = res.find((e: any) => e.id === initialSelectedId);
        if (found) {
          handleSelectEvaluation(found.id);
        }
      }
    } catch (err) {
      console.error('Fetch evaluations error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvaluations();
  }, [statusFilter, classFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchEvaluations();
  };

  const handleSelectEvaluation = async (id: string) => {
    try {
      const detail = await api.getOIMLEvaluation(id);
      setSelectedEvaluation(detail);
      loadAttachments(id);
      loadAuditLogs(id);
      loadVersions(id);
    } catch (err) {
      console.error('Fetch detail error:', err);
    }
  };

  const loadAttachments = async (id: string) => {
    try {
      setLoadingAttachments(true);
      const res = await api.getOIMLAttachments(id);
      setAttachments(res || []);
    } catch (err) {
      console.error('Fetch attachments error:', err);
    } finally {
      setLoadingAttachments(false);
    }
  };

  const loadAuditLogs = async (id: string) => {
    try {
      setLoadingAudit(true);
      const res = await api.getOIMLAuditLogs(id);
      setAuditLogs(res || []);
    } catch (err) {
      console.error('Fetch audit logs error:', err);
    } finally {
      setLoadingAudit(false);
    }
  };

  const loadVersions = async (id: string) => {
    try {
      setLoadingVersions(true);
      const res = await api.getOIMLVersions(id);
      setVersions(res || []);
    } catch (err) {
      console.error('Fetch versions error:', err);
    } finally {
      setLoadingVersions(false);
    }
  };

  const handleWorkflowTransition = async (action: string, notes?: string) => {
    if (!selectedEvaluation) return;
    try {
      setTransitioning(true);
      await api.transitionOIMLWorkflow(selectedEvaluation.id, action, notes);
      setTransitionNotesModal(null);
      setTransitionNotes('');
      // Refresh
      const updated = await api.getOIMLEvaluation(selectedEvaluation.id);
      setSelectedEvaluation(updated);
      loadAuditLogs(selectedEvaluation.id);
      loadVersions(selectedEvaluation.id);
      fetchEvaluations();
    } catch (err: any) {
      console.error('Transition error:', err);
      alert(err.message || 'Workflow transition failed');
    } finally {
      setTransitioning(false);
    }
  };

  const handleUploadAttachment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedEvaluation || !uploadFile) return;
    try {
      setUploading(true);
      await api.uploadOIMLAttachment(
        selectedEvaluation.id,
        uploadFile,
        uploadType,
        uploadTitle || uploadFile.name
      );
      setUploadFile(null);
      setUploadTitle('');
      loadAttachments(selectedEvaluation.id);
      loadAuditLogs(selectedEvaluation.id);
    } catch (err: any) {
      console.error('Upload error:', err);
      alert(err.message || 'File upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleDigitalSign = async () => {
    if (!selectedEvaluation) return;
    try {
      setSigning(true);
      await api.signOIMLEvaluation(selectedEvaluation.id, {
        officer_name: signerName,
        designation: signerRole,
        signature_remarks: 'Officially certified under Section 22 of Legal Metrology Act, 2009',
      });
      setSigningModalOpen(false);
      // Reload details
      const updated = await api.getOIMLEvaluation(selectedEvaluation.id);
      setSelectedEvaluation(updated);
      loadAuditLogs(selectedEvaluation.id);
      fetchEvaluations();
    } catch (err: any) {
      console.error('Sign error:', err);
      alert(err.message || 'Failed to digitally sign report');
    } finally {
      setSigning(false);
    }
  };

  // Helper for status badge formatting
  const renderStatusBadge = (status: string) => {
    switch (status) {
      case 'APPROVED_COMPLIANT':
        return <span className="bw-badge-pass">APPROVED COMPLIANT</span>;
      case 'FINALIZED':
        return <span className="px-2.5 py-0.5 rounded-full bg-zinc-900 text-white font-mono text-[10px] font-bold">FINALIZED &amp; LOCKED</span>;
      case 'SUBMITTED':
        return <span className="px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-800 border border-blue-200 font-mono text-[10px] font-bold">SUBMITTED FOR REVIEW</span>;
      case 'UNDER_REVIEW':
        return <span className="px-2.5 py-0.5 rounded-full bg-purple-50 text-purple-800 border border-purple-200 font-mono text-[10px] font-bold">UNDER REVIEW</span>;
      case 'CORRECTION_REQUIRED':
        return <span className="px-2.5 py-0.5 rounded-full bg-amber-50 text-amber-800 border border-amber-200 font-mono text-[10px] font-bold">CORRECTIONS REQUIRED</span>;
      case 'REJECTED_NON_COMPLIANT':
        return <span className="bw-badge-fail">NON-COMPLIANT</span>;
      case 'DRAFT':
      default:
        return <span className="bw-badge-neutral">DRAFT</span>;
    }
  };

  // Metrological tests extraction helper
  const getEvaluatedTests = (evalItem: NAWIModelEvaluation) => {
    const testSummaries = evalItem.evaluation_summary?.test_summaries || {};
    const testData = evalItem.test_data || {};

    // Standard OIML R 76 batteries
    const battery = [
      {
        id: 'weighing_test',
        clause: 'Clause A.4.4',
        name: 'Weighing Performance Test',
        hasData: !!(testData.weighing_test && testData.weighing_test.length > 0),
        status: testSummaries.weighing_test?.status || (testData.weighing_test && testData.weighing_test.every(r => r.status === 'PASS') ? 'PASS' : testData.weighing_test?.length ? 'FAIL' : 'NOT CONDUCTED'),
        detail: testData.weighing_test ? `${testData.weighing_test.length} load steps tested (Incr & Decr)` : 'No steps recorded'
      },
      {
        id: 'repeatability_test',
        clause: 'Clause A.4.10',
        name: 'Repeatability Test',
        hasData: !!(testData.repeatability_test && testData.repeatability_test.length > 0),
        status: testSummaries.repeatability_test?.status || (testData.repeatability_test && testData.repeatability_test.every(s => s.status === 'PASS') ? 'PASS' : testData.repeatability_test?.length ? 'FAIL' : 'NOT CONDUCTED'),
        detail: testData.repeatability_test ? `${testData.repeatability_test.length} series evaluated` : 'No series recorded'
      },
      {
        id: 'eccentricity_test',
        clause: 'Clause A.4.7',
        name: 'Eccentricity (Corner Load)',
        hasData: !!(testData.eccentricity_test && testData.eccentricity_test.positions?.length > 0),
        status: testSummaries.eccentricity_test?.status || (testData.eccentricity_test?.positions && testData.eccentricity_test.positions.every(p => p.status === 'PASS') ? 'PASS' : testData.eccentricity_test?.positions?.length ? 'FAIL' : 'NOT CONDUCTED'),
        detail: testData.eccentricity_test ? `Load: ${testData.eccentricity_test.test_load} ${evalItem.units} across ${testData.eccentricity_test.positions.length} positions` : 'No positions recorded'
      },
      {
        id: 'tare_zero_test',
        clause: 'Clause A.4.2',
        name: 'Tare & Zero-Setting Test',
        hasData: !!(testData.tare_zero_test && Object.keys(testData.tare_zero_test).length > 0),
        status: testSummaries.tare_zero_test?.status || (testData.tare_zero_test?.zero_setting_status || 'NOT CONDUCTED'),
        detail: testData.tare_zero_test ? 'Clause A.4.2.1 zero-setting verification' : 'Not conducted'
      },
      {
        id: 'discrimination_test',
        clause: 'Clause A.4.8',
        name: 'Discrimination Test (1.4d)',
        hasData: !!(testData.discrimination_test && testData.discrimination_test.length > 0),
        status: testSummaries.discrimination_test?.status || (testData.discrimination_test?.length ? 'PASS' : 'NOT CONDUCTED'),
        detail: testData.discrimination_test ? `${testData.discrimination_test.length} steps evaluated` : 'Not conducted'
      },
      {
        id: 'static_temp_test',
        clause: 'Clause A.5.3',
        name: 'Static Temperatures Test',
        hasData: !!(testData.environmental_voltage_test?.temperature_evaluations?.length > 0),
        status: testSummaries.static_temp_test?.status || (testData.environmental_voltage_test?.temperature_evaluations ? 'PASS' : 'NOT CONDUCTED'),
        detail: `Range: ${evalItem.temp_range_min}°C to +${evalItem.temp_range_max}°C`
      },
      {
        id: 'voltage_test',
        clause: 'Clause A.5.4',
        name: 'Voltage Variations Test',
        hasData: !!(testData.environmental_voltage_test?.voltage_evaluations?.length > 0),
        status: testSummaries.voltage_test?.status || (testData.environmental_voltage_test?.voltage_evaluations ? 'PASS' : 'NOT CONDUCTED'),
        detail: 'Power variation limits tested'
      },
    ];

    return battery;
  };

  return (
    <div className="space-y-6 animate-fade-in font-sans max-w-6xl mx-auto pb-16">
      {/* Search & Filter Header Bar */}
      <div className="bw-card p-6 rounded-3xl border border-zinc-200 shadow-sm space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-2 text-zinc-500 text-xs font-mono font-medium uppercase tracking-wider mb-1">
              <Scale className="w-3.5 h-3.5 text-zinc-900" />
              <span>OIML R 76-2:2007 (E) &bull; DIGITAL CERTIFICATION REPOSITORY</span>
            </div>
            <h1 className="text-2xl font-display font-extrabold text-zinc-900 tracking-tight">
              Type Evaluation Archive &amp; Pattern Approvals
            </h1>
            <p className="text-xs text-zinc-500 mt-1">
              Retrieve records, inspect test batteries, manage verification workflow, and export official reports.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            {role !== 'viewer' && (
              <button
                onClick={onNavigateToWizard}
                className="bw-btn-primary px-5 py-2.5 text-xs font-semibold flex items-center space-x-2 shrink-0"
              >
                <span>+ New Type Evaluation</span>
              </button>
            )}
          </div>
        </div>

        {/* Filter Controls */}
        <form onSubmit={handleSearchSubmit} className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs pt-1">
          <div className="sm:col-span-2 relative">
            <Search className="w-4 h-4 text-zinc-400 absolute left-3.5 top-2.5" />
            <input
              type="text"
              placeholder="Search by model, manufacturer, report #, license..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="bw-input w-full pl-9 pr-3.5 py-2 text-xs"
            />
          </div>

          <div>
            <select
              value={classFilter}
              onChange={(e) => setClassFilter(e.target.value)}
              className="bw-input w-full px-3 py-2 text-xs bg-white font-medium"
            >
              <option value="ALL">All Accuracy Classes</option>
              <option value="Class I">Class I (Special)</option>
              <option value="Class II">Class II (High)</option>
              <option value="Class III">Class III (Medium)</option>
              <option value="Class IIII">Class IIII (Ordinary)</option>
            </select>
          </div>

          <div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bw-input w-full px-3 py-2 text-xs bg-white font-medium"
            >
              <option value="ALL">All Evaluation Statuses</option>
              <option value="DRAFT">Draft</option>
              <option value="SUBMITTED">Submitted For Review</option>
              <option value="UNDER_REVIEW">Under Review</option>
              <option value="CORRECTION_REQUIRED">Corrections Required</option>
              <option value="APPROVED_COMPLIANT">Approved &amp; Compliant</option>
              <option value="FINALIZED">Finalized &amp; Locked</option>
              <option value="REJECTED_NON_COMPLIANT">Non-Compliant / Rejected</option>
            </select>
          </div>
        </form>
      </div>

      {/* Main Grid: List on Left, Detail Preview Drawer on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Evaluations List Table */}
        <div className={`bw-card p-6 rounded-3xl border border-zinc-200 shadow-sm space-y-3 ${selectedEvaluation ? 'lg:col-span-5' : 'lg:col-span-12'}`}>
          <div className="flex items-center justify-between border-b border-zinc-100 pb-2.5 text-xs text-zinc-500 font-mono">
            <span>SHOWING {evaluations.length} RECORDS</span>
            <button onClick={fetchEvaluations} className="hover:text-black flex items-center space-x-1.5 transition-colors">
              <RefreshCw className="w-3 h-3" />
              <span>REFRESH</span>
            </button>
          </div>

          {loading ? (
            <div className="py-12 text-center text-xs text-zinc-400 font-mono">Loading reports repository...</div>
          ) : evaluations.length === 0 ? (
            <div className="py-12 text-center text-xs text-zinc-400">No evaluations found matching search filters.</div>
          ) : (
            <div className="space-y-3">
              {evaluations.map((item) => {
                const isSelected = selectedEvaluation?.id === item.id;
                return (
                  <div
                    key={item.id}
                    onClick={() => handleSelectEvaluation(item.id)}
                    className={`p-4 rounded-2xl border transition-all cursor-pointer ${
                      isSelected
                        ? 'bg-zinc-50 border-black shadow-sm ring-1 ring-black'
                        : 'bg-white border-zinc-200 hover:border-zinc-300 hover:bg-zinc-50/50'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="space-y-1">
                        <div className="flex items-center space-x-2">
                          <span className="font-mono text-xs font-bold text-zinc-900">
                            {item.report_number}
                          </span>
                          <span className="text-[10px] px-2 py-0.5 rounded-full font-mono font-medium bg-zinc-100 text-zinc-800 border border-zinc-200">
                            {item.accuracy_class}
                          </span>
                        </div>
                        <h3 className="text-sm font-display font-bold text-zinc-900">{item.model_name}</h3>
                        <p className="text-xs text-zinc-500 line-clamp-1">{item.manufacturer_name}</p>
                      </div>

                      {renderStatusBadge(item.status)}
                    </div>

                    <div className="mt-3 pt-3 border-t border-zinc-100 flex items-center justify-between text-[11px] text-zinc-500 font-mono">
                      <div>
                        Max: <span className="font-bold text-zinc-900">{item.max_capacity} {item.units}</span> (e = {item.verification_scale_interval_e} {item.units})
                      </div>
                      <div className="flex items-center space-x-1.5">
                        <a
                          href={api.getOIMLPdfUrl(item.id)}
                          download
                          onClick={(e) => e.stopPropagation()}
                          className="px-2.5 py-0.5 rounded-full bg-zinc-100 hover:bg-black hover:text-white text-zinc-800 text-[10px] font-mono font-bold border border-zinc-200 transition-colors"
                        >
                          PDF
                        </a>
                        <a
                          href={api.getOIMLDocxUrl(item.id)}
                          download
                          onClick={(e) => e.stopPropagation()}
                          className="px-2.5 py-0.5 rounded-full bg-zinc-100 hover:bg-black hover:text-white text-zinc-800 text-[10px] font-mono font-bold border border-zinc-200 transition-colors"
                        >
                          DOCX
                        </a>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Right: Detailed Evaluation Drawer / Report Inspector */}
        {selectedEvaluation && (
          <div className="lg:col-span-7 bw-card p-6 rounded-3xl border border-zinc-200 shadow-sm space-y-6 sticky top-6 animate-slide-up">
            {/* Header */}
            <div className="flex items-start justify-between border-b border-zinc-100 pb-4">
              <div>
                <div className="flex items-center space-x-2">
                  <span className="font-mono text-xs text-zinc-500 font-bold">
                    {selectedEvaluation.report_number}
                  </span>
                  {renderStatusBadge(selectedEvaluation.status)}
                </div>
                <h2 className="text-xl font-display font-extrabold text-zinc-900 mt-1">{selectedEvaluation.model_name}</h2>
                <p className="text-xs text-zinc-500">{selectedEvaluation.instrument_type} &bull; {selectedEvaluation.manufacturer_name}</p>
              </div>

              <button
                onClick={() => setSelectedEvaluation(null)}
                className="p-1.5 rounded-full text-zinc-400 hover:text-black hover:bg-zinc-100 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Quick Actions Bar & Real Workflow State Machine */}
            <div className="space-y-3">
              <div className="flex flex-wrap items-center gap-2">
                {/* PDF & DOCX Downloads */}
                <a
                  href={api.getOIMLPdfUrl(selectedEvaluation.id)}
                  download
                  className="bw-btn-primary flex items-center space-x-1.5 px-3.5 py-2 text-xs font-semibold"
                >
                  <FileText className="w-3.5 h-3.5 text-white" />
                  <span>Download PDF</span>
                </a>

                <a
                  href={api.getOIMLDocxUrl(selectedEvaluation.id)}
                  download
                  className="bw-btn-secondary flex items-center space-x-1.5 px-3.5 py-2 text-xs font-semibold"
                >
                  <Download className="w-3.5 h-3.5 text-zinc-700" />
                  <span>Download Word (.docx)</span>
                </a>

                {/* Workflow Transitions by Role */}
                {role === 'viewer' ? (
                  <div className="text-[11px] font-mono text-zinc-400 bg-zinc-100 px-3 py-1.5 rounded-full border border-zinc-200 flex items-center space-x-1.5">
                    <Lock className="w-3 h-3 text-zinc-400" />
                    <span>Viewer Mode (Read-Only)</span>
                  </div>
                ) : (
                  <>
                    {/* Inspector Transitions */}
                    {(role === 'inspector' || role === 'admin') && (selectedEvaluation.status === 'DRAFT' || selectedEvaluation.status === 'CORRECTION_REQUIRED') && (
                      <button
                        onClick={() => handleWorkflowTransition('SUBMIT', 'Submitted for supervisory review')}
                        disabled={transitioning}
                        className="px-3.5 py-2 rounded-full bg-blue-600 hover:bg-blue-700 text-white font-mono text-xs font-bold transition-colors flex items-center space-x-1.5"
                      >
                        <Send className="w-3.5 h-3.5" />
                        <span>Submit for Review</span>
                      </button>
                    )}

                    {/* Supervisor Transitions */}
                    {(role === 'supervisor' || role === 'admin') && selectedEvaluation.status === 'SUBMITTED' && (
                      <button
                        onClick={() => handleWorkflowTransition('START_REVIEW', 'Supervisory technical review commenced')}
                        disabled={transitioning}
                        className="px-3.5 py-2 rounded-full bg-purple-600 hover:bg-purple-700 text-white font-mono text-xs font-bold transition-colors flex items-center space-x-1.5"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>Begin Review</span>
                      </button>
                    )}

                    {(role === 'supervisor' || role === 'admin') && selectedEvaluation.status === 'UNDER_REVIEW' && (
                      <div className="flex items-center gap-2">
                        {selectedEvaluation.is_fully_compliant && (
                          <button
                            onClick={() => handleWorkflowTransition('APPROVE', 'Instrument verified fully compliant with OIML R 76')}
                            disabled={transitioning}
                            className="px-3.5 py-2 rounded-full bg-emerald-600 hover:bg-emerald-700 text-white font-mono text-xs font-bold transition-colors flex items-center space-x-1.5"
                          >
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            <span>Approve Report</span>
                          </button>
                        )}

                        <button
                          onClick={() => setTransitionNotesModal({
                            open: true,
                            action: 'REQUEST_CORRECTION',
                            title: 'Request Corrections from Inspector',
                            prompt: 'Detail the observations or readings that require re-testing or correction:'
                          })}
                          disabled={transitioning}
                          className="px-3.5 py-2 rounded-full bg-amber-600 hover:bg-amber-700 text-white font-mono text-xs font-bold transition-colors flex items-center space-x-1.5"
                        >
                          <AlertTriangle className="w-3.5 h-3.5" />
                          <span>Request Correction</span>
                        </button>

                        <button
                          onClick={() => setTransitionNotesModal({
                            open: true,
                            action: 'REJECT',
                            title: 'Reject Pattern Approval',
                            prompt: 'Specify the non-compliance reasons under OIML R 76-1:2006:'
                          })}
                          disabled={transitioning}
                          className="px-3.5 py-2 rounded-full bg-rose-600 hover:bg-rose-700 text-white font-mono text-xs font-bold transition-colors flex items-center space-x-1.5"
                        >
                          <XCircle className="w-3.5 h-3.5" />
                          <span>Reject</span>
                        </button>
                      </div>
                    )}

                    {/* Finalize Action */}
                    {(role === 'supervisor' || role === 'admin') && selectedEvaluation.status === 'APPROVED_COMPLIANT' && (
                      <button
                        onClick={() => handleWorkflowTransition('FINALIZE', 'Final pattern approval certificate generated and sealed')}
                        disabled={transitioning}
                        className="px-3.5 py-2 rounded-full bg-zinc-900 hover:bg-black text-white font-mono text-xs font-bold transition-colors flex items-center space-x-1.5"
                      >
                        <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                        <span>Finalize &amp; Lock Certificate</span>
                      </button>
                    )}

                    {/* Digital Sign */}
                    {!selectedEvaluation.digital_signature && (role === 'supervisor' || role === 'admin') && (
                      <button
                        onClick={() => setSigningModalOpen(true)}
                        className="bw-btn-secondary flex items-center space-x-1.5 px-3.5 py-2 text-xs font-semibold text-zinc-900 border-zinc-300"
                      >
                        <ShieldCheck className="w-3.5 h-3.5 text-zinc-900" />
                        <span>Digitally Sign</span>
                      </button>
                    )}
                  </>
                )}
              </div>

              {/* Digital Certification Stamp */}
              {selectedEvaluation.digital_signature && (
                <div className="p-3.5 rounded-2xl bg-zinc-900 text-white space-y-1.5 text-xs font-mono shadow-sm">
                  <div className="flex items-center space-x-1.5 text-emerald-400 font-bold">
                    <ShieldCheck className="w-4 h-4" />
                    <span>Digitally Certified Pattern Approval</span>
                  </div>
                  <div className="text-[11px] text-zinc-300 space-y-0.5">
                    <div>Officer: {selectedEvaluation.digital_signature.signed_by} ({selectedEvaluation.digital_signature.designation})</div>
                    <div className="truncate text-zinc-400">Token: {selectedEvaluation.digital_signature.signature_token}</div>
                    <div className="truncate text-zinc-500">SHA-256: {selectedEvaluation.digital_signature.sha256_hash}</div>
                    <div className="text-zinc-500">Timestamp: {selectedEvaluation.digital_signature.timestamp}</div>
                  </div>
                </div>
              )}
            </div>

            {/* Navigation Tabs in Drawer */}
            <div className="flex border-b border-zinc-200 text-xs font-mono font-medium">
              <button
                onClick={() => setActiveTab('tests')}
                className={`pb-2 px-3 border-b-2 transition-colors ${
                  activeTab === 'tests'
                    ? 'border-black text-zinc-900 font-bold'
                    : 'border-transparent text-zinc-500 hover:text-black'
                }`}
              >
                OIML Tests &amp; Observations
              </button>

              <button
                onClick={() => setActiveTab('attachments')}
                className={`pb-2 px-3 border-b-2 transition-colors flex items-center space-x-1 ${
                  activeTab === 'attachments'
                    ? 'border-black text-zinc-900 font-bold'
                    : 'border-transparent text-zinc-500 hover:text-black'
                }`}
              >
                <Paperclip className="w-3 h-3" />
                <span>Evidence ({attachments.length})</span>
              </button>

              <button
                onClick={() => setActiveTab('audit')}
                className={`pb-2 px-3 border-b-2 transition-colors flex items-center space-x-1 ${
                  activeTab === 'audit'
                    ? 'border-black text-zinc-900 font-bold'
                    : 'border-transparent text-zinc-500 hover:text-black'
                }`}
              >
                <History className="w-3 h-3" />
                <span>Audit Trail ({auditLogs.length})</span>
              </button>

              <button
                onClick={() => setActiveTab('versions')}
                className={`pb-2 px-3 border-b-2 transition-colors flex items-center space-x-1 ${
                  activeTab === 'versions'
                    ? 'border-black text-zinc-900 font-bold'
                    : 'border-transparent text-zinc-500 hover:text-black'
                }`}
              >
                <FileCheck className="w-3 h-3" />
                <span>Versions ({versions.length})</span>
              </button>
            </div>

            {/* Tab 1: Tests & Observations */}
            {activeTab === 'tests' && (
              <div className="space-y-4">
                {/* Metrological Specifications Table */}
                <div className="p-4 rounded-2xl bg-zinc-50 border border-zinc-200 space-y-2 text-xs">
                  <h4 className="font-display font-bold text-zinc-900">Metrological Specifications</h4>
                  <div className="grid grid-cols-2 gap-2 text-zinc-700">
                    <div>Manufacturer: <span className="font-bold text-zinc-900">{selectedEvaluation.manufacturer_name}</span></div>
                    <div>Accuracy Class: <span className="font-bold text-zinc-900 font-mono">{selectedEvaluation.accuracy_class}</span></div>
                    <div>Max Capacity: <span className="font-mono font-bold text-zinc-900">{selectedEvaluation.max_capacity} {selectedEvaluation.units}</span></div>
                    <div>Scale Interval e: <span className="font-mono font-bold text-zinc-900">{selectedEvaluation.verification_scale_interval_e} {selectedEvaluation.units}</span></div>
                    <div>Scale Interval d: <span className="font-mono font-bold text-zinc-900">{selectedEvaluation.scale_interval_d} {selectedEvaluation.units}</span></div>
                    <div>Intervals (n): <span className="font-mono font-bold text-zinc-900">n = {selectedEvaluation.n_intervals?.toLocaleString()}</span></div>
                    <div>Gravity (g): <span className="font-mono text-zinc-900">{selectedEvaluation.local_gravity_g} m/s²</span></div>
                    <div>Temp Range: <span className="font-mono text-zinc-900">{selectedEvaluation.temp_range_min}°C to +{selectedEvaluation.temp_range_max}°C</span></div>
                  </div>
                </div>

                {/* Dynamic OIML Prescribed Tests Results */}
                <div className="p-4 rounded-2xl bg-zinc-50 border border-zinc-200 space-y-3 text-xs">
                  <div className="flex items-center justify-between">
                    <h4 className="font-display font-bold text-zinc-900">OIML R 76-1:2006 Test Battery Findings</h4>
                    <span className="text-[11px] font-mono text-zinc-500">
                      Compliance: {selectedEvaluation.is_fully_compliant ? 'VERIFIED' : 'FAILED / INCOMPLETE'}
                    </span>
                  </div>

                  <div className="space-y-2">
                    {getEvaluatedTests(selectedEvaluation).map((t, idx) => (
                      <div key={idx} className="p-2.5 rounded-xl bg-white border border-zinc-200/80 flex items-center justify-between text-xs">
                        <div className="space-y-0.5">
                          <div className="flex items-center space-x-2">
                            <span className="font-mono text-zinc-500 font-semibold">{t.clause}</span>
                            <span className="font-bold text-zinc-900">{t.name}</span>
                          </div>
                          <p className="text-[11px] text-zinc-500">{t.detail}</p>
                        </div>

                        <div>
                          {t.status === 'PASS' && (
                            <span className="bw-badge-pass text-[10px]">PASS</span>
                          )}
                          {t.status === 'FAIL' && (
                            <span className="bw-badge-fail text-[10px]">FAIL</span>
                          )}
                          {t.status === 'NOT CONDUCTED' && (
                            <span className="px-2 py-0.5 rounded-full bg-zinc-100 text-zinc-500 font-mono text-[10px] font-bold border border-zinc-200">
                              NOT CONDUCTED
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Weighing Test Observations Table (if present) */}
                {selectedEvaluation.test_data?.weighing_test && selectedEvaluation.test_data.weighing_test.length > 0 && (
                  <div className="p-4 rounded-2xl bg-zinc-50 border border-zinc-200 space-y-2 text-xs">
                    <h4 className="font-display font-bold text-zinc-900">Weighing Performance Data Points</h4>
                    <div className="overflow-x-auto">
                      <table className="w-full text-left font-mono text-[11px]">
                        <thead>
                          <tr className="border-b border-zinc-200 text-zinc-500">
                            <th className="py-1">Dir</th>
                            <th className="py-1">Load</th>
                            <th className="py-1">Indication</th>
                            <th className="py-1">Corr Error</th>
                            <th className="py-1">MPE</th>
                            <th className="py-1 text-right">Result</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-zinc-200/60">
                          {selectedEvaluation.test_data.weighing_test.map((r, i) => (
                            <tr key={i} className="hover:bg-white">
                              <td className="py-1 font-bold">{r.direction}</td>
                              <td className="py-1">{r.load} {selectedEvaluation.units}</td>
                              <td className="py-1">{r.indication}</td>
                              <td className={`py-1 font-bold ${(r.corrected_error ?? 0) < 0 ? 'text-amber-600' : 'text-zinc-900'}`}>
                                {r.corrected_error !== undefined ? r.corrected_error.toFixed(4) : '-'}
                              </td>
                              <td className="py-1 text-zinc-500">±{r.mpe_unit !== undefined ? r.mpe_unit.toFixed(4) : '-'}</td>
                              <td className="py-1 text-right">
                                <span className={r.status === 'PASS' ? 'text-emerald-700 font-bold' : 'text-rose-600 font-bold'}>
                                  {r.status || 'PASS'}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Tab 2: Evidence & Attachments */}
            {activeTab === 'attachments' && (
              <div className="space-y-4">
                {role !== 'viewer' && (
                  <form onSubmit={handleUploadAttachment} className="p-4 rounded-2xl bg-zinc-50 border border-zinc-200 space-y-3 text-xs">
                    <div className="flex items-center space-x-2 font-display font-bold text-zinc-900">
                      <UploadCloud className="w-4 h-4 text-zinc-900" />
                      <span>Upload Official Evidence / Verification Photo</span>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <div>
                        <label className="text-zinc-600 font-medium mb-1 block">Attachment Type</label>
                        <select
                          value={uploadType}
                          onChange={(e) => setUploadType(e.target.value)}
                          className="bw-input w-full px-2.5 py-1.5 text-xs bg-white"
                        >
                          <option value="INSTRUMENT_PHOTO">Instrument Photo</option>
                          <option value="MARKING_PLATE">Marking Plate / Nameplate</option>
                          <option value="TEST_SETUP">Test Setup &amp; Weights</option>
                          <option value="CALIBRATION_CERTIFICATE">Standard Weights Calibration Cert</option>
                          <option value="OTHER_EVIDENCE">Other Evidence</option>
                        </select>
                      </div>

                      <div>
                        <label className="text-zinc-600 font-medium mb-1 block">Title / Caption</label>
                        <input
                          type="text"
                          placeholder="e.g. Front display at 50kg load"
                          value={uploadTitle}
                          onChange={(e) => setUploadTitle(e.target.value)}
                          className="bw-input w-full px-2.5 py-1.5 text-xs"
                        />
                      </div>
                    </div>

                    <div className="flex items-center justify-between gap-3 pt-1">
                      <input
                        type="file"
                        accept="image/png,image/jpeg,image/webp,application/pdf"
                        onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                        className="text-xs text-zinc-600 file:mr-3 file:py-1.5 file:px-3 file:rounded-full file:border file:border-zinc-300 file:text-xs file:font-semibold file:bg-white hover:file:bg-zinc-100"
                      />

                      <button
                        type="submit"
                        disabled={!uploadFile || uploading}
                        className="bw-btn-primary px-4 py-1.5 text-xs font-semibold shrink-0 disabled:opacity-50"
                      >
                        {uploading ? 'Uploading...' : 'Upload'}
                      </button>
                    </div>
                  </form>
                )}

                {loadingAttachments ? (
                  <div className="py-6 text-center text-xs text-zinc-400 font-mono">Loading attachments...</div>
                ) : attachments.length === 0 ? (
                  <div className="py-8 text-center text-xs text-zinc-400 bg-zinc-50 rounded-2xl border border-zinc-200">
                    No attachments uploaded for this evaluation yet.
                  </div>
                ) : (
                  <div className="space-y-2">
                    {attachments.map((att) => (
                      <div key={att.id} className="p-3 rounded-2xl bg-white border border-zinc-200 flex items-center justify-between text-xs">
                        <div className="flex items-center space-x-3">
                          <div className="p-2 rounded-xl bg-zinc-100 text-zinc-700">
                            <Paperclip className="w-4 h-4" />
                          </div>
                          <div>
                            <h5 className="font-bold text-zinc-900">{att.title || att.file_name}</h5>
                            <p className="text-[11px] text-zinc-500 font-mono">
                              {att.attachment_type} &bull; {(att.file_size_bytes / 1024).toFixed(1)} KB &bull; {new Date(att.uploaded_at).toLocaleString()}
                            </p>
                          </div>
                        </div>

                        <a
                          href={`/api/v1/oiml/attachments/${att.id}/file`}
                          target="_blank"
                          rel="noreferrer"
                          className="px-3 py-1 rounded-full bg-zinc-100 hover:bg-black hover:text-white text-zinc-800 text-[11px] font-mono font-bold border border-zinc-200 transition-colors flex items-center space-x-1"
                        >
                          <span>View</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Tab 3: Audit Trail */}
            {activeTab === 'audit' && (
              <div className="space-y-3">
                <div className="text-xs text-zinc-500 flex items-center justify-between font-mono">
                  <span>IMMUTABLE METROLOGICAL AUDIT LOG</span>
                  <button onClick={() => loadAuditLogs(selectedEvaluation.id)} className="hover:text-black">
                    <RefreshCw className="w-3 h-3" />
                  </button>
                </div>

                {loadingAudit ? (
                  <div className="py-6 text-center text-xs text-zinc-400 font-mono">Loading audit logs...</div>
                ) : auditLogs.length === 0 ? (
                  <div className="py-8 text-center text-xs text-zinc-400 bg-zinc-50 rounded-2xl border border-zinc-200">
                    No audit records logged.
                  </div>
                ) : (
                  <div className="space-y-2">
                    {auditLogs.map((log) => (
                      <div key={log.id} className="p-3 rounded-2xl bg-zinc-50 border border-zinc-200 text-xs font-mono space-y-1">
                        <div className="flex items-center justify-between text-zinc-900 font-bold">
                          <span>{log.action}</span>
                          <span className="text-zinc-500 text-[10px]">{new Date(log.timestamp).toLocaleString()}</span>
                        </div>
                        <div className="text-[11px] text-zinc-600">
                          User ID: {log.user_id || 'System'}
                          {log.new_value && (
                            <span className="text-zinc-700 ml-2">[{log.new_value}]</span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Tab 4: Version History */}
            {activeTab === 'versions' && (
              <div className="space-y-3">
                <div className="text-xs text-zinc-500 flex items-center justify-between font-mono">
                  <span>OFFICIAL REPORT VERSIONS &amp; CHECKSUMS</span>
                  <button onClick={() => loadVersions(selectedEvaluation.id)} className="hover:text-black">
                    <RefreshCw className="w-3 h-3" />
                  </button>
                </div>

                {loadingVersions ? (
                  <div className="py-6 text-center text-xs text-zinc-400 font-mono">Loading versions...</div>
                ) : versions.length === 0 ? (
                  <div className="py-8 text-center text-xs text-zinc-400 bg-zinc-50 rounded-2xl border border-zinc-200">
                    No official report versions generated yet.
                  </div>
                ) : (
                  <div className="space-y-2">
                    {versions.map((ver) => (
                      <div key={ver.id} className="p-3 rounded-2xl bg-white border border-zinc-200 text-xs font-mono space-y-1.5">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-zinc-900 px-2 py-0.5 rounded-full bg-zinc-100 border border-zinc-200">
                            Version {ver.version}
                          </span>
                          <span className="text-zinc-500 text-[10px]">{new Date(ver.generated_at).toLocaleString()}</span>
                        </div>
                        <div className="text-[11px] text-zinc-600 truncate">
                          File: {ver.file_location}
                        </div>
                        <div className="text-[10px] text-zinc-400 truncate">
                          SHA-256: {ver.checksum || 'N/A'}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Digital Signing Modal */}
      {signingModalOpen && selectedEvaluation && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-md bg-white border border-zinc-200 rounded-3xl p-6 sm:p-7 space-y-4 shadow-2xl animate-slide-up">
            <div className="flex items-center justify-between border-b border-zinc-100 pb-3">
              <h3 className="text-sm font-display font-bold text-zinc-900 flex items-center space-x-2">
                <ShieldCheck className="w-4 h-4 text-zinc-900" />
                <span>Digitally Certify Model Approval</span>
              </h3>
              <button onClick={() => setSigningModalOpen(false)} className="text-zinc-400 hover:text-black">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="space-y-1">
                <label className="text-zinc-700 font-medium">Signing Officer Name</label>
                <input
                  type="text"
                  value={signerName}
                  onChange={(e) => setSignerName(e.target.value)}
                  className="bw-input w-full px-3.5 py-2.5 text-xs"
                />
              </div>

              <div className="space-y-1">
                <label className="text-zinc-700 font-medium">Official Designation</label>
                <input
                  type="text"
                  value={signerRole}
                  onChange={(e) => setSignerRole(e.target.value)}
                  className="bw-input w-full px-3.5 py-2.5 text-xs"
                />
              </div>

              <div className="p-3.5 bg-zinc-50 rounded-2xl border border-zinc-200 text-[11px] text-zinc-500 leading-relaxed font-sans">
                By clicking Authorize, you certify under the Legal Metrology Act, 2009 that the instrument model has complied with all OIML R 76 testing procedures and Maximum Permissible Error requirements.
              </div>
            </div>

            <div className="flex items-center justify-end space-x-3 pt-3 border-t border-zinc-100">
              <button
                onClick={() => setSigningModalOpen(false)}
                className="px-4 py-2 text-zinc-600 hover:text-black text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                onClick={handleDigitalSign}
                disabled={signing}
                className="bw-btn-primary px-5 py-2 text-xs font-semibold disabled:opacity-50"
              >
                {signing ? 'Signing...' : 'Authorize & Sign'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Workflow Transition Notes Modal (for Request Correction & Reject) */}
      {transitionNotesModal && selectedEvaluation && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-md bg-white border border-zinc-200 rounded-3xl p-6 sm:p-7 space-y-4 shadow-2xl animate-slide-up">
            <div className="flex items-center justify-between border-b border-zinc-100 pb-3">
              <h3 className="text-sm font-display font-bold text-zinc-900 flex items-center space-x-2">
                <MessageSquare className="w-4 h-4 text-zinc-900" />
                <span>{transitionNotesModal.title}</span>
              </h3>
              <button onClick={() => setTransitionNotesModal(null)} className="text-zinc-400 hover:text-black">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <p className="text-zinc-600">{transitionNotesModal.prompt}</p>

              <textarea
                rows={4}
                value={transitionNotes}
                onChange={(e) => setTransitionNotes(e.target.value)}
                placeholder="Enter official remarks..."
                className="bw-input w-full p-3 text-xs resize-none"
              />
            </div>

            <div className="flex items-center justify-end space-x-3 pt-3 border-t border-zinc-100">
              <button
                onClick={() => setTransitionNotesModal(null)}
                className="px-4 py-2 text-zinc-600 hover:text-black text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                onClick={() => handleWorkflowTransition(transitionNotesModal.action, transitionNotes)}
                disabled={transitioning || !transitionNotes.trim()}
                className="bw-btn-primary px-5 py-2 text-xs font-semibold disabled:opacity-50"
              >
                {transitioning ? 'Submitting...' : 'Confirm'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
