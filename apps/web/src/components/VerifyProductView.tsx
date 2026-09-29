import React, { useState, useRef } from 'react';
import {
  UploadCloud,
  Camera,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Trash2,
  Play,
  FileCheck2,
  ArrowRight,
  ShieldCheck,
  Eye,
  Sparkles,
  FileImage,
  Layers
} from 'lucide-react';
import { api } from '../api';

interface VerifyProductViewProps {
  onInspectionCreated: (inspectionId: string) => void;
}

interface SurfaceImageUpload {
  surface: string;
  file: File | null;
  previewUrl: string | null;
  fileName?: string;
  fileSize?: string;
}

export const VerifyProductView: React.FC<VerifyProductViewProps> = ({ onInspectionCreated }) => {
  const [productName, setProductName] = useState('Packaged Commodity');
  const [brand, setBrand] = useState('');
  const [categoryCode, setCategoryCode] = useState('food');
  const [activeSurfaceTab, setActiveSurfaceTab] = useState('front');
  const [isDragOver, setIsDragOver] = useState(false);

  const [surfaces, setSurfaces] = useState<Record<string, SurfaceImageUpload>>({
    front: { surface: 'front', file: null, previewUrl: null },
    back: { surface: 'back', file: null, previewUrl: null },
    side_a: { surface: 'side_a', file: null, previewUrl: null },
    top: { surface: 'top', file: null, previewUrl: null },
  });

  const [isWebcamActive, setIsWebcamActive] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [activeInspectionId, setActiveInspectionId] = useState<string | null>(null);
  const [analysisLogs, setAnalysisLogs] = useState<{ step: string; message: string; done: boolean }[]>([]);
  const [analysisFinished, setAnalysisFinished] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const surfaceTabs = [
    { id: 'front', label: 'Front Surface *', required: true },
    { id: 'back', label: 'Back Surface', required: false },
    { id: 'side_a', label: 'Side Surface', required: false },
    { id: 'top', label: 'Top / Bottom', required: false },
  ];

  const startWebcam = async () => {
    setIsWebcamActive(true);
    setErrorMessage(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      console.error('Camera access error:', err);
      setIsWebcamActive(false);
      setErrorMessage('Camera access was blocked or not found. Please click "Select Image" to choose a file from your device.');
    }
  };

  const captureWebcamSnapshot = () => {
    if (!videoRef.current || !canvasRef.current) return;
    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], `${activeSurfaceTab}_camera_snapshot.jpg`, { type: 'image/jpeg' });
        attachFileToSurface(activeSurfaceTab, file);
      }
    }, 'image/jpeg', 0.92);

    const stream = video.srcObject as MediaStream;
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
    }
    setIsWebcamActive(false);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const attachFileToSurface = (surface: string, file: File) => {
    const previewUrl = URL.createObjectURL(file);
    setSurfaces((prev) => ({
      ...prev,
      [surface]: {
        surface,
        file,
        previewUrl,
        fileName: file.name,
        fileSize: formatFileSize(file.size),
      },
    }));
    setErrorMessage(null);
  };

  const handleFileDropOrSelect = (files: FileList | null) => {
    if (!files || files.length === 0) return;
    if (files.length >= 2) {
      attachFileToSurface('front', files[0]);
      attachFileToSurface('back', files[1]);
      if (files.length >= 3) {
        attachFileToSurface('side_a', files[2]);
      }
    } else {
      attachFileToSurface(activeSurfaceTab, files[0]);
    }
  };

  const removeSurfaceImage = (surface: string) => {
    setSurfaces((prev) => ({
      ...prev,
      [surface]: { surface, file: null, previewUrl: null },
    }));
  };

  const loadDemoPackage = async () => {
    const makeDemoImage = (isBack: boolean): Promise<File> => {
      return new Promise((resolve) => {
        const canvas = document.createElement('canvas');
        canvas.width = 800;
        canvas.height = 600;
        const ctx = canvas.getContext('2d')!;

        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, 800, 600);
        ctx.strokeStyle = '#000000';
        ctx.lineWidth = 4;
        ctx.strokeRect(10, 10, 780, 580);

        if (!isBack) {
          ctx.fillStyle = '#09090b';
          ctx.font = 'bold 36px sans-serif';
          ctx.fillText('Britannia Good Day Butter Cookies', 50, 120);

          ctx.fillStyle = '#52525b';
          ctx.font = 'bold 24px sans-serif';
          ctx.fillText('Rich Butter Cookies • 100% Vegetarian', 50, 170);

          ctx.fillStyle = '#000000';
          ctx.font = 'bold 32px sans-serif';
          ctx.fillText('Net Quantity: 200 g', 50, 320);

          ctx.fillStyle = '#71717a';
          ctx.font = '18px sans-serif';
          ctx.fillText('Serving Suggestion • Proprietary Food', 50, 480);
        } else {
          ctx.fillStyle = '#09090b';
          ctx.font = 'bold 22px sans-serif';
          ctx.fillText('MANDATORY STATUTORY DECLARATIONS (LM RULES 2011)', 50, 80);

          ctx.fillStyle = '#27272a';
          ctx.font = '18px sans-serif';
          ctx.fillText('Maximum Retail Price (MRP): Rs. 40.00 incl. of all taxes', 50, 140);
          ctx.fillText('Unit Sale Price (USP): ₹0.20 per g', 50, 180);
          ctx.fillText('Manufactured & Packed By: Britannia Industries Ltd.,', 50, 230);
          ctx.fillText('5/1A Hungerford Street, Kolkata - 700017, West Bengal', 50, 260);
          ctx.fillText('Date of Manufacture / Packing: PKD 08/2026', 50, 310);
          ctx.fillText('Consumer Care Cell: 1800-425-4449 or feedback@britindia.com', 50, 360);
          ctx.fillText('Batch No: B24089 • Country of Origin: India', 50, 410);
        }

        canvas.toBlob((blob) => {
          resolve(new File([blob!], isBack ? 'good_day_back.jpg' : 'good_day_front.jpg', { type: 'image/jpeg' }));
        }, 'image/jpeg');
      });
    };

    try {
      const frontFile = await makeDemoImage(false);
      const backFile = await makeDemoImage(true);
      attachFileToSurface('front', frontFile);
      attachFileToSurface('back', backFile);
      setProductName('Britannia Good Day Butter Cookies');
      setBrand('Britannia');
      setCategoryCode('food');
    } catch (e) {
      console.error('Failed to load demo images:', e);
    }
  };

  const handleStartAnalysis = async () => {
    if (!surfaces.front.file) {
      setErrorMessage('The Front Surface image is mandatory for inspection compliance.');
      setActiveSurfaceTab('front');
      return;
    }

    try {
      setIsAnalyzing(true);
      setAnalysisFinished(false);
      setAnalysisLogs([]);
      setErrorMessage(null);

      const inspection = await api.createInspection({
        product_name: productName,
        brand: brand || undefined,
        category_code: categoryCode,
      });

      const inspId = inspection.id;
      setActiveInspectionId(inspId);

      setAnalysisLogs((prev) => [
        ...prev,
        { step: 'INIT', message: `Initialized inspection docket #${inspId}`, done: true },
      ]);

      const uploadPromises: Promise<any>[] = [];
      Object.entries(surfaces).forEach(([surfaceKey, surf]) => {
        if (surf.file) {
          uploadPromises.push(api.uploadSurfaceImage(inspId, surf.file, surfaceKey));
        }
      });

      setAnalysisLogs((prev) => [
        ...prev,
        { step: 'UPLOAD', message: `Uploading ${uploadPromises.length} high-resolution package surface images...`, done: false },
      ]);

      await Promise.all(uploadPromises);

      setAnalysisLogs((prev) => [
        ...prev,
        { step: 'UPLOAD_DONE', message: 'All surfaces ingested and indexed for OCR.', done: true },
      ]);

      setAnalysisLogs((prev) => [
        ...prev,
        { step: 'EXECUTE', message: 'Triggering OCR text extraction and Legal Metrology rule engine...', done: false },
      ]);

      const updatedInspection = await api.runInspection(inspId);

      setAnalysisLogs((prev) => [
        ...prev,
        { step: 'COMPLETE', message: `Verification finished: Status = ${updatedInspection.status} (${updatedInspection.confidence_score}% confidence)`, done: true },
      ]);

      setAnalysisFinished(true);
      setIsAnalyzing(false);
    } catch (err: any) {
      console.error('Inspection error:', err);
      setIsAnalyzing(false);
      setErrorMessage(err.message || 'Inspection pipeline failed. Please check backend connection.');
    }
  };

  const attachedCount = Object.values(surfaces).filter((s) => !!s.file).length;

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-16 animate-fade-in font-sans">
      {/* Page Title & Action Bar */}
      <div className="bw-card p-6 sm:p-7 rounded-3xl border border-zinc-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-zinc-500 text-xs font-mono font-medium uppercase tracking-wider mb-1.5">
            <span className="w-2 h-2 rounded-full bg-black"></span>
            <span>LEGAL METROLOGY (PACKAGED COMMODITIES) RULES, 2011</span>
          </div>
          <h1 className="text-2xl font-display font-extrabold text-zinc-900 tracking-tight">
            Package Verification &amp; Label OCR Inspection
          </h1>
          <p className="text-xs text-zinc-500 mt-1">
            Upload multi-surface photographs or capture live scans for automated statutory declaration checks.
          </p>
        </div>

        <button
          onClick={loadDemoPackage}
          className="bw-btn-secondary px-4 py-2 text-xs flex items-center space-x-2 shrink-0"
        >
          <Sparkles className="w-3.5 h-3.5 text-zinc-700" />
          <span>Load Standard Sample</span>
        </button>
      </div>

      {errorMessage && (
        <div className="p-4 rounded-2xl bg-zinc-100 border border-zinc-300 text-zinc-900 text-xs flex items-center space-x-2">
          <AlertTriangle className="w-4 h-4 text-black shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Metadata Configuration */}
      <div className="bw-card p-6 rounded-3xl border border-zinc-200 shadow-sm grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-[11px] font-semibold text-zinc-600 uppercase tracking-wider mb-1.5">
            Commodity / Product Name *
          </label>
          <input
            type="text"
            value={productName}
            onChange={(e) => setProductName(e.target.value)}
            placeholder="e.g. Daawat Basmati Rice or Parle Biscuits"
            className="bw-input w-full px-3.5 py-2 text-xs"
          />
        </div>
        <div>
          <label className="block text-[11px] font-semibold text-zinc-600 uppercase tracking-wider mb-1.5">
            Brand Name (Optional)
          </label>
          <input
            type="text"
            value={brand}
            onChange={(e) => setBrand(e.target.value)}
            placeholder="e.g. Daawat or Britannia"
            className="bw-input w-full px-3.5 py-2 text-xs"
          />
        </div>
        <div>
          <label className="block text-[11px] font-semibold text-zinc-600 uppercase tracking-wider mb-1.5">
            Statutory Category *
          </label>
          <select
            value={categoryCode}
            onChange={(e) => setCategoryCode(e.target.value)}
            className="bw-input w-full px-3.5 py-2 text-xs bg-white font-medium"
          >
            <option value="food">Packaged Food &amp; Beverages (FSSAI &amp; LM)</option>
            <option value="cosmetics">Cosmetics &amp; Personal Care</option>
            <option value="household">Household &amp; Cleaning Commodities</option>
            <option value="textiles">Textiles &amp; Garments</option>
            <option value="electronics">Consumer Electronics</option>
            <option value="imported">Imported Packaged Commodities</option>
          </select>
        </div>
      </div>

      {/* Multi-Surface Ingestion Tabs */}
      <div className="bw-card p-6 sm:p-7 rounded-3xl border border-zinc-200 shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-zinc-100 pb-3 gap-2">
          <div className="flex flex-wrap gap-2">
            {surfaceTabs.map((t) => {
              const hasFile = !!surfaces[t.id]?.file;
              const isCurrent = activeSurfaceTab === t.id;
              return (
                <button
                  key={t.id}
                  onClick={() => setActiveSurfaceTab(t.id)}
                  className={`px-4 py-1.5 rounded-full text-xs font-semibold transition-all flex items-center space-x-1.5 ${
                    isCurrent
                      ? 'bg-black text-white shadow-sm'
                      : hasFile
                      ? 'bg-zinc-100 text-zinc-900 border border-zinc-300'
                      : 'bg-zinc-50 text-zinc-500 hover:text-black'
                  }`}
                >
                  <span>{t.label}</span>
                  {hasFile && <CheckCircle2 className="w-3.5 h-3.5" />}
                </button>
              );
            })}
          </div>
          <div className="text-xs text-zinc-500 font-mono flex items-center space-x-2">
            <span>Attached:</span>
            <span className="font-bold text-zinc-900">{attachedCount} surface{attachedCount !== 1 ? 's' : ''}</span>
          </div>
        </div>

        {/* Surface Capture & Preview Area */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Dropzone & Camera Trigger */}
          <div
            onDragOver={(e) => {
              e.preventDefault();
              e.stopPropagation();
              setIsDragOver(true);
            }}
            onDragLeave={(e) => {
              e.preventDefault();
              e.stopPropagation();
              setIsDragOver(false);
            }}
            onDrop={(e) => {
              e.preventDefault();
              e.stopPropagation();
              setIsDragOver(false);
              handleFileDropOrSelect(e.dataTransfer.files);
            }}
            className={`border-2 border-dashed rounded-3xl p-8 flex flex-col items-center justify-center text-center space-y-4 transition-all ${
              isDragOver
                ? 'border-black bg-zinc-50 scale-[1.01]'
                : 'border-zinc-200 hover:border-zinc-400 bg-zinc-50/50'
            }`}
          >
            <input
              type="file"
              ref={fileInputRef}
              accept="image/*"
              multiple
              className="hidden"
              onChange={(e) => handleFileDropOrSelect(e.target.files)}
            />
            <div className="flex space-x-3">
              <button
                onClick={() => fileInputRef.current?.click()}
                className="p-4 rounded-2xl bg-white hover:bg-zinc-100 text-zinc-900 border border-zinc-200 transition-all flex flex-col items-center space-y-2 group cursor-pointer shadow-sm"
              >
                <UploadCloud className="w-7 h-7 group-hover:scale-110 transition-transform text-black" />
                <span className="text-xs font-bold">Select Image</span>
              </button>

              <button
                onClick={startWebcam}
                className="p-4 rounded-2xl bg-white hover:bg-zinc-100 text-zinc-900 border border-zinc-200 transition-all flex flex-col items-center space-y-2 group cursor-pointer shadow-sm"
              >
                <Camera className="w-7 h-7 group-hover:scale-110 transition-transform text-black" />
                <span className="text-xs font-bold">Live Camera</span>
              </button>
            </div>
            <p className="text-[11px] text-zinc-500 max-w-xs leading-relaxed">
              Drag &amp; drop photos or click to upload. Attaching both <span className="text-zinc-900 font-bold">Front</span> and <span className="text-zinc-900 font-bold">Back</span> surfaces enables complete Legal Metrology cross-check.
            </p>
          </div>

          {/* Preview / Active Capture */}
          <div className="bg-zinc-50 border border-zinc-200 rounded-3xl p-4 flex flex-col items-center justify-center min-h-[260px] relative">
            {isWebcamActive ? (
              <div className="w-full h-full flex flex-col items-center justify-center space-y-3">
                <video ref={videoRef} autoPlay playsInline className="w-full max-h-56 object-cover rounded-2xl border border-zinc-300" />
                <div className="flex space-x-2">
                  <button
                    onClick={captureWebcamSnapshot}
                    className="bw-btn-primary px-4 py-1.5 text-xs font-bold"
                  >
                    Capture Snapshot
                  </button>
                  <button
                    onClick={() => {
                      if (videoRef.current && videoRef.current.srcObject) {
                        (videoRef.current.srcObject as MediaStream).getTracks().forEach((t) => t.stop());
                      }
                      setIsWebcamActive(false);
                    }}
                    className="bw-btn-secondary px-3 py-1.5 text-xs font-semibold"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : surfaces[activeSurfaceTab]?.previewUrl ? (
              <div className="w-full h-full flex flex-col items-center space-y-3">
                <img
                  src={surfaces[activeSurfaceTab].previewUrl!}
                  alt="Surface Preview"
                  className="w-full max-h-56 object-contain rounded-2xl border border-zinc-200"
                />
                <div className="w-full flex items-center justify-between px-2 text-xs">
                  <div className="flex items-center space-x-2 text-zinc-900 font-semibold truncate max-w-[200px]">
                    <CheckCircle2 className="w-4 h-4 shrink-0 text-black" />
                    <span className="truncate">{surfaces[activeSurfaceTab].fileName || `${activeSurfaceTab}.jpg`}</span>
                    {surfaces[activeSurfaceTab].fileSize && (
                      <span className="text-zinc-500 font-mono text-[10px]">({surfaces[activeSurfaceTab].fileSize})</span>
                    )}
                  </div>
                  <button
                    onClick={() => removeSurfaceImage(activeSurfaceTab)}
                    className="p-1.5 text-zinc-600 hover:text-black bg-zinc-200/80 rounded-lg text-xs flex items-center space-x-1"
                    title="Remove this photograph"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    <span>Remove</span>
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-center text-zinc-400 space-y-1.5 p-6">
                <FileImage className="w-10 h-10 mx-auto text-zinc-300" />
                <p className="text-xs font-semibold text-zinc-600">No photograph attached for {activeSurfaceTab.toUpperCase()}</p>
                <p className="text-[11px] text-zinc-400">Drop an image on the left to attach</p>
              </div>
            )}
            <canvas ref={canvasRef} className="hidden" />
          </div>
        </div>

        {/* Execution Pipeline Button */}
        <div className="pt-4 border-t border-zinc-100 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="text-xs text-zinc-500">
            Powered by <span className="text-zinc-900 font-semibold">RapidOCR (PaddleOCR ONNX)</span> &amp; deterministic Legal Metrology rules.
          </div>
          <button
            onClick={handleStartAnalysis}
            disabled={isAnalyzing}
            className="bw-btn-primary px-6 py-2.5 text-xs font-bold tracking-wider uppercase flex items-center justify-center space-x-2 disabled:opacity-50"
          >
            {isAnalyzing ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin text-white" />
                <span>Executing Pipeline...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" />
                <span>RUN COMPLIANCE VERIFICATION</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Live Progress Panel */}
      {(isAnalyzing || analysisFinished) && (
        <div className="bw-card p-6 sm:p-7 rounded-3xl border border-zinc-200 shadow-sm space-y-4 animate-slide-up">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {isAnalyzing ? (
                <div className="w-2.5 h-2.5 rounded-full bg-black animate-pulse" />
              ) : (
                <CheckCircle2 className="w-4 h-4 text-black" />
              )}
              <h2 className="text-sm font-display font-bold text-zinc-900">
                {isAnalyzing ? 'Live AI & Legal Metrology Verification Pipeline' : 'Verification Complete — Ready for Inspector Review'}
              </h2>
            </div>
            <span className="text-[11px] font-mono text-zinc-900 font-bold">Docket: {activeInspectionId}</span>
          </div>

          {/* Progress Steps Feed */}
          <div className="space-y-2 max-h-60 overflow-y-auto p-4 rounded-2xl bg-zinc-900 text-white text-xs font-mono">
            {analysisLogs.map((log, idx) => (
              <div key={idx} className="flex items-start space-x-2.5 py-1 text-zinc-300">
                <CheckCircle2 className="w-3.5 h-3.5 text-white shrink-0 mt-0.5" />
                <div>
                  <span className="text-white font-bold mr-2">[{log.step}]</span>
                  <span>{log.message}</span>
                </div>
              </div>
            ))}
          </div>

          {analysisFinished && (
            <div className="pt-2 flex items-center justify-between">
              <span className="text-xs text-zinc-600 font-medium flex items-center space-x-1.5">
                <ShieldCheck className="w-4 h-4 text-black" />
                <span>Deep-learning OCR extraction and statutory rule checks completed.</span>
              </span>
              <button
                onClick={() => onInspectionCreated(activeInspectionId!)}
                className="bw-btn-primary px-5 py-2 text-xs font-bold flex items-center space-x-1.5"
              >
                <span>VIEW EVIDENCE &amp; AUDIT</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
