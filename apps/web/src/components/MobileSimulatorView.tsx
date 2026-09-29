import React, { useState, useRef } from 'react';
import {
  Smartphone,
  Camera,
  CheckCircle2,
  RefreshCw,
  ArrowRight,
  ShieldCheck,
  RotateCcw
} from 'lucide-react';
import { api } from '../api';
import { useI18n } from '../i18n';

interface MobileSimulatorViewProps {
  onInspectionCreated: (inspectionId: string) => void;
}

export const MobileSimulatorView: React.FC<MobileSimulatorViewProps> = ({ onInspectionCreated }) => {
  const { t } = useI18n();
  const [productName, setProductName] = useState('Parle Marie Biscuits');
  const [category, setCategory] = useState('food');
  const [stage, setStage] = useState<'SETUP' | 'CAMERA' | 'PROCESSING' | 'COMPLETED'>('SETUP');

  const surfaces = ['Front', 'Back', 'Side A'];
  const [currentSurfaceIdx, setCurrentSurfaceIdx] = useState(0);
  const [capturedImages, setCapturedImages] = useState<Record<string, File>>({});
  const [createdInspectionId, setCreatedInspectionId] = useState<string>('');

  const videoRef = useRef<HTMLVideoElement | null>(null);

  const startCameraStream = async () => {
    setStage('CAMERA');
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (e) {
      console.warn('Webcam stream not directly available in frame; running simulated outdoor lens');
    }
  };

  const captureSurface = async () => {
    const canvas = document.createElement('canvas');
    canvas.width = 640;
    canvas.height = 480;
    const ctx = canvas.getContext('2d')!;

    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, 640, 480);
    ctx.strokeStyle = '#09090b';
    ctx.lineWidth = 4;
    ctx.strokeRect(10, 10, 620, 460);

    const curSurface = surfaces[currentSurfaceIdx];
    ctx.fillStyle = '#09090b';
    ctx.font = 'bold 24px sans-serif';
    ctx.fillText(`${productName} — ${curSurface} Surface`, 40, 80);

    if (curSurface === 'Front') {
      ctx.fillStyle = '#18181b';
      ctx.font = 'bold 22px sans-serif';
      ctx.fillText('Net Quantity: 250 g', 40, 240);
    } else if (curSurface === 'Back') {
      ctx.fillStyle = '#27272a';
      ctx.font = '16px sans-serif';
      ctx.fillText('MRP Rs. 35.00 incl. of all taxes', 40, 180);
      ctx.fillText('Unit Sale Price: ₹0.14 per g', 40, 220);
      ctx.fillText('Manufactured by: Parle Products Pvt Ltd, Mumbai', 40, 260);
      ctx.fillText('PKD 08/2026 • Consumer Helpline: 1800-222-211', 40, 300);
    }

    canvas.toBlob(async (blob) => {
      const file = new File([blob!], `${curSurface.toLowerCase()}.jpg`, { type: 'image/jpeg' });
      setCapturedImages((prev) => ({ ...prev, [curSurface.toLowerCase()]: file }));

      if (currentSurfaceIdx < surfaces.length - 1) {
        setCurrentSurfaceIdx((idx) => idx + 1);
      } else {
        // Complete! Upload and analyze
        setStage('PROCESSING');
        try {
          const created = await api.createInspection({
            product_name: productName,
            category_code: category,
            address: 'GPS Verified: 28.6139° N, 77.2090° E (Field Scan)',
          });
          setCreatedInspectionId(created.id);

          for (const s of ['front', 'back']) {
            if (capturedImages[s] || file) {
              const f = capturedImages[s] || file;
              await api.uploadImage(created.id, s, f);
            }
          }

          await api.triggerAnalysis(created.id);
          setStage('COMPLETED');
        } catch (err) {
          console.error(err);
          setStage('COMPLETED');
        }
      }
    }, 'image/jpeg');
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-12 animate-fade-in">
      {/* Header */}
      <div className="bw-card p-8 bg-white border border-zinc-200">
        <div className="flex items-center space-x-2 text-zinc-900 text-xs font-bold uppercase tracking-wider mb-2">
          <Smartphone className="w-4 h-4 text-zinc-900" />
          <span className="font-mono">{t('mobile_sim_title')}</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold text-zinc-950 tracking-tight">
          {t('mobile_sim_title')}
        </h1>
        <p className="text-sm text-zinc-500 mt-2 max-w-2xl">
          {t('mobile_sim_sub')}
        </p>
      </div>

      {/* Simulated Mobile Phone Chassis */}
      <div className="flex justify-center animate-slide-up">
        <div className="w-[360px] h-[680px] bg-white rounded-[44px] border-[8px] border-zinc-900 shadow-2xl overflow-hidden flex flex-col relative">
          {/* Top Speaker Notch & Dynamic Island */}
          <div className="h-7 bg-white flex justify-center items-center border-b border-zinc-100">
            <div className="w-20 h-4 bg-zinc-950 rounded-full flex items-center justify-end px-2">
              <span className="w-1.5 h-1.5 rounded-full bg-zinc-700"></span>
            </div>
          </div>

          {/* Screen Content */}
          <div className="flex-1 bg-zinc-50 flex flex-col justify-between p-5 text-zinc-900 overflow-y-auto">
            {stage === 'SETUP' && (
              <div className="space-y-5 my-auto">
                <div className="text-center space-y-2">
                  <div className="w-14 h-14 rounded-2xl bg-zinc-900 text-white mx-auto flex items-center justify-center shadow-md">
                    <Camera className="w-7 h-7" />
                  </div>
                  <h2 className="text-lg font-bold text-zinc-950">{t('mobile_step_setup')}</h2>
                  <p className="text-xs text-zinc-500">Step 1 of 3: Commodity Details</p>
                </div>

                <div className="space-y-3 text-xs">
                  <div>
                    <label className="block text-zinc-600 text-xs font-bold mb-1">{t('rules_product_name')}</label>
                    <input
                      type="text"
                      value={productName}
                      onChange={(e) => setProductName(e.target.value)}
                      className="bw-input w-full px-3 py-2 text-xs"
                    />
                  </div>

                  <div>
                    <label className="block text-zinc-600 text-xs font-bold mb-1">{t('rules_category')}</label>
                    <select
                      value={category}
                      onChange={(e) => setCategory(e.target.value)}
                      className="bw-input w-full px-3 py-2 text-xs"
                    >
                      <option value="food">Packaged Food</option>
                      <option value="cosmetics">Cosmetics</option>
                      <option value="imported">Imported Commodity</option>
                    </select>
                  </div>

                  <div className="p-3 rounded-xl bg-white border border-zinc-200 text-xs text-zinc-600 flex items-center space-x-2 shadow-sm font-mono">
                    <span className="w-2 h-2 rounded-full bg-zinc-950 animate-pulse-beacon"></span>
                    <span>GPS: 28.6139° N, 77.2090° E</span>
                  </div>
                </div>

                <button
                  onClick={startCameraStream}
                  className="bw-btn-primary w-full py-3 text-xs tracking-wider uppercase shadow-md flex items-center justify-center space-x-2"
                >
                  <span>{t('mobile_btn_start')}</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            )}

            {stage === 'CAMERA' && (
              <div className="flex-1 flex flex-col justify-between">
                <div className="flex justify-between items-center text-xs font-mono">
                  <span className="font-bold text-zinc-900 bg-zinc-200 px-2.5 py-1 rounded-full">
                    SCAN: {surfaces[currentSurfaceIdx].toUpperCase()}
                  </span>
                  <span className="text-xs text-zinc-500">{currentSurfaceIdx + 1}/3</span>
                </div>

                {/* Reticle / Viewfinder */}
                <div className="relative my-auto h-64 border-2 border-dashed border-zinc-900 rounded-2xl flex items-center justify-center overflow-hidden bg-white shadow-inner">
                  <video ref={videoRef} autoPlay playsInline className="absolute inset-0 w-full h-full object-cover" />
                  <div className="text-center z-10 bg-white/90 p-3 rounded-xl border border-zinc-200 shadow-md">
                    <p className="text-xs font-bold text-zinc-950 font-mono">ALIGN {surfaces[currentSurfaceIdx].toUpperCase()} HERE</p>
                    <p className="text-[11px] text-zinc-500 mt-0.5">Keep package flat & illuminated</p>
                  </div>
                </div>

                {/* Real-time Quality Indicators */}
                <div className="space-y-4">
                  <div className="p-2.5 rounded-xl bg-white border border-zinc-200 flex justify-around text-xs shadow-sm font-mono">
                    <span className="text-zinc-900 flex items-center space-x-1 font-bold">
                      <CheckCircle2 className="w-3.5 h-3.5 text-zinc-900" />
                      <span>Text OK</span>
                    </span>
                    <span className="text-zinc-900 flex items-center space-x-1 font-bold">
                      <CheckCircle2 className="w-3.5 h-3.5 text-zinc-900" />
                      <span>Blur OK</span>
                    </span>
                    <span className="text-zinc-900 flex items-center space-x-1 font-bold">
                      <CheckCircle2 className="w-3.5 h-3.5 text-zinc-900" />
                      <span>Light OK</span>
                    </span>
                  </div>

                  {/* Shutter Button */}
                  <div className="flex justify-center pb-2">
                    <button
                      onClick={captureSurface}
                      className="w-16 h-16 rounded-full border-4 border-zinc-200 bg-zinc-950 flex items-center justify-center shadow-lg active:scale-95 transition-transform"
                    >
                      <Camera className="w-7 h-7 text-white" />
                    </button>
                  </div>
                </div>
              </div>
            )}

            {stage === 'PROCESSING' && (
              <div className="my-auto text-center space-y-4">
                <RefreshCw className="w-10 h-10 text-zinc-900 animate-spin mx-auto" />
                <h3 className="text-base font-bold text-zinc-950">{t('mobile_step_processing')}</h3>
                <p className="text-xs text-zinc-500 font-mono max-w-xs mx-auto">
                  Executing Legal Metrology OCR and deterministic compliance validation
                </p>
              </div>
            )}

            {stage === 'COMPLETED' && (
              <div className="my-auto text-center space-y-5">
                <div className="w-16 h-16 rounded-full bg-zinc-950 text-white mx-auto flex items-center justify-center shadow-lg">
                  <ShieldCheck className="w-9 h-9" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-zinc-950">{t('mobile_step_completed')}</h3>
                  <p className="text-sm font-semibold text-zinc-800 mt-1">{productName}</p>
                  <p className="text-xs text-zinc-400 font-mono mt-0.5">ID: {createdInspectionId}</p>
                </div>
                <button
                  onClick={() => onInspectionCreated(createdInspectionId)}
                  className="bw-btn-primary w-full py-3 text-xs flex items-center justify-center space-x-2 shadow-md"
                >
                  <span>{t('mobile_view_report')}</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
                <button
                  onClick={() => {
                    setStage('SETUP');
                    setCurrentSurfaceIdx(0);
                    setCapturedImages({});
                  }}
                  className="text-xs text-zinc-500 hover:text-zinc-900 flex items-center justify-center space-x-1 mx-auto"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>{t('mobile_btn_reset')}</span>
                </button>
              </div>
            )}
          </div>

          {/* Bottom Home Indicator */}
          <div className="h-6 bg-white flex justify-center items-center border-t border-zinc-100">
            <div className="w-28 h-1 bg-zinc-300 rounded-full"></div>
          </div>
        </div>
      </div>
    </div>
  );
};
