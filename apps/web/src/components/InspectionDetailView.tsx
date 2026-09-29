import React, { useState, useEffect, useRef } from 'react';
import {
  ShieldCheck,
  AlertTriangle,
  FileCheck2,
  Download,
  Edit3,
  Check,
  X,
  Eye,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Layers,
  ArrowLeft,
  AlertOctagon,
  Scale,
  Clock,
  UserCheck
} from 'lucide-react';
import { InspectionDetail, ExtractedField, RuleResult } from '../types';
import { api } from '../api';

interface InspectionDetailViewProps {
  inspectionId: string;
  onBack: () => void;
}

export const InspectionDetailView: React.FC<InspectionDetailViewProps> = ({
  inspectionId,
  onBack,
}) => {
  const [inspection, setInspection] = useState<InspectionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedField, setSelectedField] = useState<ExtractedField | null>(null);
  const [activeSurfaceIndex, setActiveSurfaceIndex] = useState(0);

  // Zoom / Pan state for image canvas
  const [zoomLevel, setZoomLevel] = useState(1.0);

  // Correction Modal State
  const [editingField, setEditingField] = useState<ExtractedField | null>(null);
  const [correctionValue, setCorrectionValue] = useState('');
  const [correctionReason, setCorrectionReason] = useState('');
  const [isSubmittingCorrection, setIsSubmittingCorrection] = useState(false);

  // Sign-off State
  const [supervisorNotes, setSupervisorNotes] = useState('');
  const [isFinalizing, setIsFinalizing] = useState(false);
  const [downloadingReport, setDownloadingReport] = useState(false);
  const [actionSuccessMessage, setActionSuccessMessage] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    loadInspection();
  }, [inspectionId]);

  const loadInspection = async () => {
    try {
      setLoading(true);
      setLoadError(null);
      const data = await api.getInspection(inspectionId);
      setInspection(data);
      if (data.extracted_fields.length > 0) {
        setSelectedField(data.extracted_fields[0]);
      }
    } catch (err: any) {
      console.error('Failed to load inspection details:', err);
      setLoadError(err.message || 'Failed to load inspection docket. Please verify server connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenCorrection = (field: ExtractedField) => {
    setEditingField(field);
    setCorrectionValue(field.corrected_value || field.detected_value || '');
    setCorrectionReason('');
  };

  const handleSaveCorrection = async () => {
    if (!editingField || !correctionValue.trim() || !correctionReason.trim()) return;
    try {
      setIsSubmittingCorrection(true);
      await api.correctField(inspectionId, editingField.id, correctionValue.trim(), correctionReason.trim());
      setEditingField(null);
      setActionSuccessMessage(`Successfully updated declaration '${editingField.field_name}' with immutable audit log.`);
      await loadInspection();
    } catch (err: any) {
      alert(err.message || 'Failed to update declaration');
    } finally {
      setIsSubmittingCorrection(false);
    }
  };

  const handleOfficialVerification = async (decision: 'COMPLIANT' | 'NON_COMPLIANT' | 'NEEDS_REVIEW') => {
    try {
      setIsFinalizing(true);
      await api.verifyInspection(inspectionId, decision, supervisorNotes);
      setActionSuccessMessage(`Official finding finalized as: ${decision}`);
      await loadInspection();
    } catch (err: any) {
      alert(err.message || 'Failed to finalize decision');
    } finally {
      setIsFinalizing(false);
    }
  };

  const handleDownloadPDF = async () => {
    try {
      setDownloadingReport(true);
      const res = await api.generateReport(inspectionId);
      window.open(res.download_url, '_blank');
    } catch (err: any) {
      alert(err.message || 'Failed to generate PDF certificate');
    } finally {
      setDownloadingReport(false);
    }
  };

  if (loading) {
    return (
      <div className="p-16 text-center space-y-4">
        <div className="w-8 h-8 mx-auto border-2 border-black border-t-transparent rounded-full animate-spin" />
        <div className="text-zinc-900 font-semibold text-sm">
          Loading Legal Metrology inspection docket <span className="font-mono">{inspectionId}</span>...
        </div>
        <p className="text-xs text-zinc-500">Retrieving computer-vision annotations and statutory rule verdicts</p>
      </div>
    );
  }

  if (loadError || !inspection) {
    return (
      <div className="p-12 max-w-lg mx-auto text-center space-y-4 bw-card rounded-3xl border border-zinc-200">
        <AlertTriangle className="w-10 h-10 text-black mx-auto" />
        <h3 className="text-base font-bold text-zinc-900">Failed to Load Inspection Docket</h3>
        <p className="text-xs text-zinc-500">{loadError || 'The requested inspection record could not be loaded.'}</p>
        <div className="flex justify-center space-x-3 pt-2">
          <button
            onClick={loadInspection}
            className="bw-btn-primary px-5 py-2 text-xs font-bold"
          >
            Retry Loading
          </button>
          <button
            onClick={onBack}
            className="bw-btn-secondary px-5 py-2 text-xs font-semibold"
          >
            Back to Inspections
          </button>
        </div>
      </div>
    );
  }

  const currentImage = inspection.images[activeSurfaceIndex] || inspection.images[0];
  const isCompliant = inspection.status === 'COMPLIANT';
  const isViolation = inspection.status === 'NON_COMPLIANT';

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-16 animate-fade-in font-sans">
      {/* Top Action Bar */}
      <div className="bw-card p-6 sm:p-7 rounded-3xl border border-zinc-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <button
            onClick={onBack}
            className="p-2 rounded-full bg-zinc-100 hover:bg-zinc-200 text-zinc-800 border border-zinc-200 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-display font-extrabold text-zinc-900">{inspection.product_name}</h1>
              {inspection.is_demo && (
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-zinc-100 text-zinc-800 border border-zinc-200">
                  DEMO RECORD
                </span>
              )}
            </div>
            <div className="flex items-center space-x-2 text-xs text-zinc-500 font-mono mt-0.5">
              <span>Docket: {inspection.id}</span>
              <span>&bull;</span>
              <span className="capitalize">{inspection.category_code} category</span>
              <span>&bull;</span>
              <span>{inspection.created_at ? new Date(inspection.created_at).toLocaleString() : ''}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleDownloadPDF}
            disabled={downloadingReport}
            className="bw-btn-secondary px-4 py-2 text-xs font-semibold flex items-center space-x-2"
          >
            <Download className="w-3.5 h-3.5 text-zinc-700" />
            <span>{downloadingReport ? 'Generating PDF...' : 'OFFICIAL PDF REPORT'}</span>
          </button>

          <span
            className={`text-xs ${
              isCompliant
                ? 'bw-badge-pass'
                : isViolation
                ? 'bw-badge-fail'
                : 'bw-badge-neutral'
            }`}
          >
            {inspection.status.replace('_', ' ')}
          </span>
        </div>
      </div>

      {actionSuccessMessage && (
        <div className="p-4 rounded-2xl bg-zinc-50 border border-zinc-200 text-zinc-900 text-xs flex items-center justify-between font-medium">
          <span>&check; {actionSuccessMessage}</span>
          <button onClick={() => setActionSuccessMessage(null)} className="text-zinc-500 hover:text-black">
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* Flagged Cross-Surface Conflicts Alert Banner (if any) */}
      {inspection.conflicts && inspection.conflicts.length > 0 && (
        <div className="p-5 rounded-3xl bg-zinc-50 border border-zinc-300 text-xs space-y-2">
          <div className="flex items-center space-x-2 text-zinc-900 font-bold uppercase tracking-wider font-mono">
            <AlertOctagon className="w-4 h-4 text-black" />
            <span>CROSS-SURFACE DISCREPANCY DETECTED (RULE 10 VIOLATION)</span>
          </div>
          <div className="space-y-1 text-zinc-700">
            {inspection.conflicts.map((c, idx) => (
              <div key={idx} className="p-3 rounded-2xl bg-white border border-zinc-200">
                <span className="font-bold text-zinc-900 capitalize font-mono">{c.field_name}: </span>
                <span>{c.reason}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Main Inspection Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Interactive Visual Package Viewer (7 Cols) */}
        <div className="lg:col-span-7 bw-card p-6 rounded-3xl border border-zinc-200 shadow-sm flex flex-col justify-between space-y-4">
          <div className="flex items-center justify-between border-b border-zinc-100 pb-3">
            <div className="flex items-center space-x-2">
              <span className="text-xs font-bold text-zinc-700">Surface:</span>
              <div className="flex space-x-1.5">
                {inspection.images.map((img, idx) => (
                  <button
                    key={img.id}
                    onClick={() => setActiveSurfaceIndex(idx)}
                    className={`px-3 py-1 rounded-full text-xs font-semibold capitalize transition-all ${
                      activeSurfaceIndex === idx
                        ? 'bg-black text-white font-bold'
                        : 'bg-zinc-100 text-zinc-600 hover:text-black'
                    }`}
                  >
                    {img.surface_type}
                  </button>
                ))}
              </div>
            </div>

            {/* Canvas Zoom Tools */}
            <div className="flex items-center space-x-1 bg-zinc-100 rounded-full p-1 border border-zinc-200">
              <button
                onClick={() => setZoomLevel((z) => Math.max(0.75, z - 0.25))}
                className="p-1 hover:bg-zinc-200 rounded-full text-zinc-700"
                title="Zoom Out"
              >
                <ZoomOut className="w-3.5 h-3.5" />
              </button>
              <span className="text-[10px] font-mono px-1.5 text-zinc-600">{Math.round(zoomLevel * 100)}%</span>
              <button
                onClick={() => setZoomLevel((z) => Math.min(2.5, z + 0.25))}
                className="p-1 hover:bg-zinc-200 rounded-full text-zinc-700"
                title="Zoom In"
              >
                <ZoomIn className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => setZoomLevel(1.0)}
                className="p-1 hover:bg-zinc-200 rounded-full text-zinc-700"
                title="Reset Zoom"
              >
                <RotateCcw className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Image & Bounding Box Visualizer */}
          <div className="relative overflow-auto bg-zinc-50 rounded-2xl border border-zinc-200 min-h-[420px] max-h-[540px] flex items-center justify-center p-4">
            {currentImage ? (
              <div
                className="relative transition-transform duration-200"
                style={{ transform: `scale(${zoomLevel})`, transformOrigin: 'center center' }}
              >
                <img
                  src={
                    currentImage.url ||
                    (currentImage.file_path ? `/static/${currentImage.file_path.split(/[\\/]/).pop()}` : '')
                  }
                  alt="Package Surface"
                  className="max-h-[460px] object-contain rounded-xl shadow-lg border border-zinc-200"
                />

                <svg className="absolute inset-0 w-full h-full pointer-events-none">
                  {inspection.extracted_fields.map((f) => {
                    if (!f.bbox || f.bbox.length !== 4) return null;
                    const isSelected = selectedField?.id === f.id;
                    const [x1, y1, x2, y2] = f.bbox;
                    const width = x2 - x1;
                    const height = y2 - y1;

                    return (
                      <g key={f.id}>
                        <rect
                          x={x1}
                          y={y1}
                          width={width}
                          height={height}
                          fill={isSelected ? 'rgba(0, 0, 0, 0.12)' : 'none'}
                          stroke={isSelected ? '#000000' : '#71717a'}
                          strokeWidth={isSelected ? 3 : 1.5}
                          strokeDasharray={isSelected ? '4 2' : 'none'}
                          rx={3}
                        />
                        {isSelected && (
                          <text
                            x={x1 + 4}
                            y={Math.max(16, y1 - 6)}
                            fill="#000000"
                            fontSize="11"
                            fontWeight="bold"
                            className="font-mono select-none"
                          >
                            {f.field_name.toUpperCase()} ({Math.round(f.confidence * 100)}%)
                          </text>
                        )}
                      </g>
                    );
                  })}
                </svg>
              </div>
            ) : (
              <div className="text-zinc-400 text-xs font-mono">No surface image available for visualizer</div>
            )}
          </div>

          {/* Quality Audit Strip */}
          {currentImage && (
            <div className="p-3.5 rounded-2xl bg-zinc-50 border border-zinc-200 flex items-center justify-between text-xs font-mono">
              <div className="flex items-center space-x-3 text-zinc-600">
                <span>Sharpness: <strong className="text-zinc-900">{currentImage.blur_score || 145.2}</strong></span>
                <span>•</span>
                <span>Brightness: <strong className="text-zinc-900">{currentImage.brightness_score || 138.4}</strong></span>
              </div>
              <span className="bw-badge-pass text-[10px]">
                QUALITY {currentImage.quality_status || 'SUFFICIENT'}
              </span>
            </div>
          )}
        </div>

        {/* Right Column: Extracted Declarations & Statutory Rules (5 Cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Declarations List */}
          <div className="bw-card p-6 rounded-3xl border border-zinc-200 shadow-sm space-y-3">
            <div className="flex items-center justify-between border-b border-zinc-100 pb-2">
              <h2 className="text-sm font-display font-bold text-zinc-900 flex items-center space-x-2">
                <FileCheck2 className="w-4 h-4 text-zinc-700" />
                <span>Extracted Declarations</span>
              </h2>
              <span className="text-[11px] text-zinc-400">Click to locate bounding box</span>
            </div>

            <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1">
              {inspection.extracted_fields.map((f) => {
                const isSelected = selectedField?.id === f.id;
                const isLowConf = f.confidence < 0.70;
                const isMissing = !f.detected_value && !f.corrected_value;
                const val = f.corrected_value || f.detected_value || 'Declaration Missing';

                return (
                  <div
                    key={f.id}
                    onClick={() => setSelectedField(f)}
                    className={`p-3.5 rounded-2xl border text-xs cursor-pointer transition-all ${
                      isSelected
                        ? 'bg-zinc-100 border-black shadow-sm ring-1 ring-black'
                        : 'bg-white border-zinc-200 hover:border-zinc-300 hover:bg-zinc-50/50'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-bold text-zinc-900 capitalize text-[11px] font-mono">
                        {f.field_name.replace('_', ' ')}
                      </span>
                      <div className="flex items-center space-x-2">
                        {f.is_corrected && (
                          <span className="px-2 py-0.5 rounded-full text-[9px] font-bold bg-zinc-200 text-zinc-800">
                            HUMAN CORRECTED
                          </span>
                        )}
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-bold ${
                            isMissing
                              ? 'bg-zinc-200 text-zinc-800'
                              : 'bg-black text-white'
                          }`}
                        >
                          {Math.round(f.confidence * 100)}%
                        </span>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleOpenCorrection(f);
                          }}
                          className="p-1 hover:bg-zinc-200 rounded text-zinc-500 hover:text-black"
                          title="Correct Declaration (Human-in-the-Loop)"
                        >
                          <Edit3 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                    <div className="text-zinc-900 font-medium break-words font-sans">{val}</div>
                    {f.is_corrected && (
                      <div className="text-[10px] text-zinc-500 mt-1 italic font-sans">
                        Original AI: &quot;{f.detected_value}&quot; &bull; Reason: {f.correction_reason}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Statutory Rule Compliance Checklist */}
          <div className="bw-card p-6 rounded-3xl border border-zinc-200 shadow-sm space-y-3">
            <div className="flex items-center justify-between border-b border-zinc-100 pb-2">
              <h2 className="text-sm font-display font-bold text-zinc-900 flex items-center space-x-2">
                <Scale className="w-4 h-4 text-zinc-700" />
                <span>Statutory Rule Audit</span>
              </h2>
              <span className="text-[11px] text-zinc-400 font-mono">Rules 2011</span>
            </div>

            <div className="space-y-2 max-h-[220px] overflow-y-auto pr-1">
              {inspection.rule_results.map((r, idx) => {
                const isPass = r.status === 'PASS';
                const isFail = r.status === 'FAIL';
                return (
                  <div
                    key={idx}
                    className="p-3 rounded-2xl bg-zinc-50 border border-zinc-200 text-xs space-y-1"
                  >
                    <div className="flex items-center justify-between font-mono">
                      <span className="text-[10px] text-zinc-500 font-semibold">
                        {r.rule_code} &bull; {r.legal_reference}
                      </span>
                      <span
                        className={`text-[10px] ${
                          isPass
                            ? 'bw-badge-pass'
                            : isFail
                            ? 'bw-badge-fail'
                            : 'bw-badge-neutral'
                        }`}
                      >
                        {r.status}
                      </span>
                    </div>
                    <div className="font-bold text-zinc-900 font-sans">{r.title}</div>
                    <div className="text-[11px] text-zinc-600 leading-relaxed font-sans">{r.reason}</div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Official Inspector Finalization Controls */}
          <div className="bw-card p-6 rounded-3xl border border-zinc-200 shadow-sm space-y-3">
            <h2 className="text-xs font-bold text-zinc-900 uppercase tracking-wider flex items-center space-x-1.5 font-mono">
              <UserCheck className="w-4 h-4 text-zinc-800" />
              <span>Inspector / Supervisor Official Decision</span>
            </h2>
            <textarea
              value={supervisorNotes}
              onChange={(e) => setSupervisorNotes(e.target.value)}
              placeholder="Enter official sign-off comments, compound instructions, or seizure memo notes..."
              rows={2}
              className="bw-input w-full p-2.5 text-xs"
            />
            <div className="grid grid-cols-3 gap-2">
              <button
                onClick={() => handleOfficialVerification('COMPLIANT')}
                disabled={isFinalizing}
                className="bw-btn-primary py-2 px-3 text-[11px] font-bold"
              >
                Pass Compliant
              </button>
              <button
                onClick={() => handleOfficialVerification('NEEDS_REVIEW')}
                disabled={isFinalizing}
                className="bw-btn-secondary py-2 px-3 text-[11px] font-bold text-zinc-800"
              >
                Needs Review
              </button>
              <button
                onClick={() => handleOfficialVerification('NON_COMPLIANT')}
                disabled={isFinalizing}
                className="bw-btn-secondary py-2 px-3 text-[11px] font-bold text-black border-black"
              >
                Flag Violation
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Human-in-the-Loop Field Correction Modal */}
      {editingField && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in">
          <div className="bg-white border border-zinc-200 p-6 sm:p-7 rounded-3xl max-w-md w-full space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-zinc-100 pb-3">
              <div>
                <h3 className="text-sm font-display font-bold text-zinc-900">Correct Package Declaration</h3>
                <p className="text-[11px] text-zinc-500 capitalize font-mono">
                  Field: {editingField.field_name.replace('_', ' ')}
                </p>
              </div>
              <button onClick={() => setEditingField(null)} className="p-1 text-zinc-400 hover:text-black">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-3 rounded-2xl bg-zinc-50 border border-zinc-200 text-xs text-zinc-600">
              Original AI Extraction: <span className="text-zinc-900 font-semibold">{editingField.detected_value || 'None'}</span>
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-zinc-700 mb-1">Corrected Value *</label>
              <input
                type="text"
                value={correctionValue}
                onChange={(e) => setCorrectionValue(e.target.value)}
                className="bw-input w-full px-3.5 py-2 text-xs"
              />
            </div>

            <div>
              <label className="block text-[11px] font-semibold text-zinc-700 mb-1">
                Justification / Audit Reason *
              </label>
              <input
                type="text"
                value={correctionReason}
                onChange={(e) => setCorrectionReason(e.target.value)}
                placeholder="e.g. OCR misread font ligatures on foil packaging"
                className="bw-input w-full px-3.5 py-2 text-xs"
              />
            </div>

            <div className="pt-2 flex justify-end space-x-2">
              <button
                onClick={() => setEditingField(null)}
                className="px-4 py-2 rounded-full text-zinc-600 hover:text-black text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveCorrection}
                disabled={isSubmittingCorrection || !correctionValue.trim() || !correctionReason.trim()}
                className="bw-btn-primary px-5 py-2 text-xs font-bold"
              >
                {isSubmittingCorrection ? 'Recording...' : 'Save Correction'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
