// LabelGuard AI - Create Inspection Screen
import 'package:flutter/material.dart';

class CreateInspectionScreen extends StatefulWidget {
  const CreateInspectionScreen({Key? key}) : super(key: key);

  @override
  State<CreateInspectionScreen> createState() => _CreateInspectionScreenState();
}

class _CreateInspectionScreenState extends State<CreateInspectionScreen> {
  final _productCtrl = TextEditingController();
  final _brandCtrl = TextEditingController();
  String _selectedCategory = "food";
  final String _mockGpsLocation = "28.6139° N, 77.2090° E (Connaught Place, New Delhi)";

  final List<Map<String, String>> _categories = [
    {"code": "food", "name": "Packaged Food & Beverages"},
    {"code": "cosmetics", "name": "Cosmetics & Personal Care"},
    {"code": "household", "name": "Household & Cleaning"},
    {"code": "textiles", "name": "Textiles & Garments"},
    {"code": "electronics", "name": "Consumer Electronics"},
    {"code": "imported", "name": "Imported Packaged Commodities"},
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text("New Field Inspection", style: TextStyle(color: Colors.white, fontSize: 16)),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text("1. Select Commodity Category", style: TextStyle(color: Colors.cyanAccent, fontWeight: FontWeight.bold, fontSize: 13)),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 14),
              decoration: BoxDecoration(
                color: const Color(0xFF1E293B),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.white12),
              ),
              child: DropdownButtonHideUnderline(
                child: DropdownButton<String>(
                  value: _selectedCategory,
                  dropdownColor: const Color(0xFF1E293B),
                  isExpanded: true,
                  items: _categories.map((c) {
                    return DropdownMenuItem<String>(
                      value: c["code"],
                      child: Text(c["name"]!, style: const TextStyle(color: Colors.white, fontSize: 13)),
                    );
                  }).toList(),
                  onChanged: (val) {
                    if (val != null) setState(() => _selectedCategory = val);
                  },
                ),
              ),
            ),
            const SizedBox(height: 20),

            const Text("2. Product Identification", style: TextStyle(color: Colors.cyanAccent, fontWeight: FontWeight.bold, fontSize: 13)),
            const SizedBox(height: 8),
            TextField(
              controller: _productCtrl,
              style: const TextStyle(color: Colors.white, fontSize: 14),
              decoration: InputDecoration(
                filled: true,
                fillColor: const Color(0xFF1E293B),
                labelText: "Commodity / Product Name *",
                labelStyle: const TextStyle(color: Colors.white60, fontSize: 12),
                hintText: "e.g. Marie Gold Biscuits",
                hintStyle: const TextStyle(color: Colors.white24, fontSize: 12),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _brandCtrl,
              style: const TextStyle(color: Colors.white, fontSize: 14),
              decoration: InputDecoration(
                filled: true,
                fillColor: const Color(0xFF1E293B),
                labelText: "Brand Name (Optional)",
                labelStyle: const TextStyle(color: Colors.white60, fontSize: 12),
                hintText: "e.g. Britannia",
                hintStyle: const TextStyle(color: Colors.white24, fontSize: 12),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
              ),
            ),
            const SizedBox(height: 20),

            const Text("3. GPS & Inspection Metadata", style: TextStyle(color: Colors.cyanAccent, fontWeight: FontWeight.bold, fontSize: 13)),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFF1E293B),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.white12),
              ),
              child: Row(
                children: [
                  const Icon(Icons.location_on, color: Colors.greenAccent, size: 20),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      _mockGpsLocation,
                      style: const TextStyle(color: Colors.white70, fontSize: 11),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 36),

            SizedBox(
              width: double.infinity,
              height: 54,
              child: ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.cyanAccent,
                  foregroundColor: Colors.black,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                ),
                onPressed: () {
                  final prodName = _productCtrl.text.trim().isNotEmpty ? _productCtrl.text.trim() : "Sample Packaged Good";
                  Navigator.pushNamed(context, '/scan', arguments: {
                    'inspection_id': "LG-2026-09-${DateTime.now().millisecondsSinceEpoch.toString().substring(7)}",
                    'product_name': prodName,
                    'category_code': _selectedCategory,
                  });
                },
                icon: const Icon(Icons.camera_alt, color: Colors.black),
                label: const Text("LAUNCH LIVE SCANNER", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
