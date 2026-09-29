// LabelGuard AI - Intelligent Live Camera Scan Screen
// Real-time package alignment guide, blur status, lighting indicator, and multi-surface capture
import 'package:flutter/material.dart';

class CameraScanScreen extends StatefulWidget {
  final String inspectionId;
  final String productName;
  final String categoryCode;

  const CameraScanScreen({
    Key? key,
    required this.inspectionId,
    required this.productName,
    required this.categoryCode,
  }) : super(key: key);

  @override
  State<CameraScanScreen> createState() => _CameraScanScreenState();
}

class _CameraScanScreenState extends State<CameraScanScreen> {
  final List<String> _surfaces = ['Front', 'Back', 'Side A', 'Side B', 'Top', 'Bottom'];
  int _currentSurfaceIndex = 0;
  final Map<String, String?> _capturedSurfaces = {};
  
  // Real-time simulated CV feedback indicators
  bool _textDetected = true;
  bool _blurStatusOk = true;
  bool _lightingOk = true;
  bool _isProcessing = false;

  void _captureCurrentSurface() async {
    setState(() => _isProcessing = true);
    
    // Simulate capture and quality evaluation
    await Future.delayed(const Duration(milliseconds: 600));
    final surfaceName = _surfaces[_currentSurfaceIndex];
    _capturedSurfaces[surfaceName] = "captured_path_$surfaceName.jpg";

    if (_currentSurfaceIndex < _surfaces.length - 1) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text("✓ $surfaceName captured. Next: ${_surfaces[_currentSurfaceIndex + 1]}"),
        backgroundColor: Colors.green.shade700,
        duration: const Duration(seconds: 1),
      ));
      setState(() {
        _currentSurfaceIndex++;
        _isProcessing = false;
      });
    } else {
      setState(() => _isProcessing = false);
      // All stages captured, navigate to results
      Navigator.pushReplacementNamed(context, '/results', arguments: {
        'inspection_id': widget.inspectionId,
        'product_name': widget.productName,
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final currentSurface = _surfaces[_currentSurfaceIndex];

    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.black87,
        elevation: 0,
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              "LabelGuard AI • LIVE SCANNER",
              style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold, letterSpacing: 1.1, color: Colors.cyanAccent),
            ),
            Text(
              "${widget.productName} (${widget.inspectionId})",
              style: const TextStyle(fontSize: 11, color: Colors.white70),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.flash_auto, color: Colors.white),
            onPressed: () {},
          ),
          IconButton(
            icon: const Icon(Icons.flip_camera_ios, color: Colors.white),
            onPressed: () {},
          ),
        ],
      ),
      body: Stack(
        children: [
          // Camera Preview Area with Darkened Vignette
          Container(
            width: double.infinity,
            height: double.infinity,
            color: const Color(0xFF121418),
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.camera_alt_outlined, size: 48, color: Colors.white.withOpacity(0.2)),
                  const SizedBox(height: 8),
                  Text("Live Camera Stream Active", style: TextStyle(color: Colors.white.withOpacity(0.4), fontSize: 12)),
                ],
              ),
            ),
          ),

          // Package Alignment Guide Frame
          Center(
            child: Container(
              width: MediaQuery.of(context).size.width * 0.84,
              height: MediaQuery.of(context).size.height * 0.54,
              decoration: BoxDecoration(
                border: Border.all(color: Colors.cyanAccent, width: 2.5),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Stack(
                children: [
                  // Corner Reticles
                  Positioned(
                    top: 12,
                    left: 12,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.black.withOpacity(0.65),
                        borderRadius: BorderRadius.circular(20),
                        border: Border.all(color: Colors.cyanAccent.withOpacity(0.4)),
                      ),
                      child: Text(
                        "TARGET: ${currentSurface.toUpperCase()}",
                        style: const TextStyle(color: Colors.cyanAccent, fontWeight: FontWeight.bold, fontSize: 11),
                      ),
                    ),
                  ),
                  const Center(
                    child: Text(
                      "ALIGN PACKAGE HERE",
                      style: TextStyle(
                        color: Colors.white54,
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                        letterSpacing: 1.5,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),

          // Top Multi-Surface Progress Bar
          Positioned(
            top: 16,
            left: 16,
            right: 16,
            child: Container(
              padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
              decoration: BoxDecoration(
                color: Colors.black.withOpacity(0.75),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.white12),
              ),
              child: SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: _surfaces.map((surface) {
                    final isCaptured = _capturedSurfaces.containsKey(surface);
                    final isCurrent = surface == currentSurface;
                    return Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 4),
                      child: Chip(
                        avatar: isCaptured
                            ? const Icon(Icons.check_circle, size: 16, color: Colors.greenAccent)
                            : (isCurrent
                                ? const Icon(Icons.radio_button_checked, size: 16, color: Colors.cyanAccent)
                                : const Icon(Icons.radio_button_unchecked, size: 16, color: Colors.white38)),
                        label: Text(
                          surface,
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: isCurrent ? FontWeight.bold : FontWeight.normal,
                            color: isCurrent ? Colors.white : (isCaptured ? Colors.greenAccent : Colors.white60),
                          ),
                        ),
                        backgroundColor: isCurrent ? Colors.cyan.shade900 : Colors.black45,
                        side: BorderSide(color: isCurrent ? Colors.cyanAccent : Colors.white12),
                      ),
                    );
                  }).toList(),
                ),
              ),
            ),
          ),

          // Bottom Real-time Quality Indicators & Shutter Button
          Positioned(
            bottom: 24,
            left: 0,
            right: 0,
            child: Column(
              children: [
                // Live CV Quality Indicators
                Container(
                  margin: const EdgeInsets.symmetric(horizontal: 28),
                  padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
                  decoration: BoxDecoration(
                    color: Colors.black.withOpacity(0.75),
                    borderRadius: BorderRadius.circular(24),
                    border: Border.all(color: Colors.white24),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: [
                      _qualityChip("Text Detected", _textDetected),
                      _qualityChip("Blur Status", _blurStatusOk),
                      _qualityChip("Lighting", _lightingOk),
                    ],
                  ),
                ),
                const SizedBox(height: 20),

                // Large Shutter Button (Outdoor one-handed operation)
                GestureDetector(
                  onTap: _isProcessing ? null : _captureCurrentSurface,
                  child: Container(
                    width: 78,
                    height: 78,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(color: Colors.white, width: 4),
                      color: Colors.cyanAccent,
                      boxShadow: [
                        BoxShadow(
                          color: Colors.cyanAccent.withOpacity(0.4),
                          blurRadius: 16,
                          spreadRadius: 2,
                        ),
                      ],
                    ),
                    child: _isProcessing
                        ? const Center(child: CircularProgressIndicator(color: Colors.black))
                        : const Center(
                            child: Icon(Icons.camera_alt, size: 34, color: Colors.black87),
                          ),
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  "TAP TO CAPTURE ${currentSurface.toUpperCase()}",
                  style: const TextStyle(color: Colors.white70, fontSize: 10, letterSpacing: 1.2, fontWeight: FontWeight.bold),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _qualityChip(String label, bool isGood) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(
          isGood ? Icons.check_circle : Icons.warning_amber_rounded,
          size: 14,
          color: isGood ? Colors.greenAccent : Colors.amberAccent,
        ),
        const SizedBox(width: 4),
        Text(
          label,
          style: TextStyle(
            color: isGood ? Colors.white : Colors.amberAccent,
            fontSize: 10,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }
}
