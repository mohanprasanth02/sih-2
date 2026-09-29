// LabelGuard AI - Mobile Inspection Result & Evidence Review Screen
import 'package:flutter/material.dart';

class InspectionResultScreen extends StatelessWidget {
  const InspectionResultScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final args = ModalRoute.of(context)?.settings.arguments as Map<String, dynamic>? ?? {};
    final inspectionId = args['inspection_id'] ?? 'LG-2026-09-000101';
    final productName = args['product_name'] ?? 'Britannia Good Day Butter Cookies';

    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text("Inspection Result", style: TextStyle(color: Colors.white, fontSize: 16)),
        actions: [
          IconButton(
            icon: const Icon(Icons.picture_as_pdf, color: Colors.cyanAccent),
            tooltip: "Download PDF Report",
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
                content: Text("Downloading Official Legal Metrology PDF Report..."),
                backgroundColor: Colors.green,
              ));
            },
          ),
          IconButton(
            icon: const Icon(Icons.share, color: Colors.white),
            onPressed: () {},
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Status Card
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(18),
              decoration: BoxDecoration(
                color: Colors.green.shade900.withOpacity(0.3),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.greenAccent.shade400, width: 1.5),
              ),
              child: Column(
                children: [
                  const Icon(Icons.check_circle, color: Colors.greenAccent, size: 40),
                  const SizedBox(height: 8),
                  const Text(
                    "COMPLIANT",
                    style: TextStyle(color: Colors.greenAccent, fontSize: 20, fontWeight: FontWeight.bold, letterSpacing: 1.2),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    productName,
                    style: const TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.w600),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 2),
                  Text(
                    "ID: $inspectionId • Legal Metrology (PC) Rules 2011",
                    style: TextStyle(color: Colors.grey.shade400, fontSize: 11),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // Summary Stats Row
            Row(
              children: [
                _statBox("Detected Declarations", "7 / 7", Colors.cyanAccent),
                const SizedBox(width: 8),
                _statBox("High Confidence", "6", Colors.greenAccent),
                const SizedBox(width: 8),
                _statBox("Potential Issues", "0", Colors.grey),
              ],
            ),
            const SizedBox(height: 24),

            const Text("Extracted Package Declarations", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15)),
            const SizedBox(height: 10),

            _fieldItem("Product Name", "Britannia Good Day Butter Cookies", "98% (Front Face)", true),
            _fieldItem("Net Quantity", "200 g", "97% (Front Face)", true),
            _fieldItem("Maximum Retail Price", "MRP Rs. 40.00 incl. of all taxes", "96% (Back Face)", true),
            _fieldItem("Unit Sale Price (USP)", "₹0.20 per g", "94% (Back Face)", true),
            _fieldItem("Manufacturer & Address", "Britannia Industries Ltd., Hungerford St, Kolkata", "95% (Back Face)", true),
            _fieldItem("Date of Packing", "PKD 08/2026", "93% (Back Face)", true),
            _fieldItem("Consumer Care", "1800-425-4449 feedback@britindia.com", "96% (Back Face)", true),

            const SizedBox(height: 24),
            const Text("Statutory Rule Validations", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15)),
            const SizedBox(height: 10),

            _ruleItem("LM-RULE-001 • Rule 6(1)(a)", "Generic Commodity Name", "PASS", "Common name declared on front package face."),
            _ruleItem("LM-RULE-004 • Rule 6(1)(d)", "Standard Metric Net Quantity", "PASS", "Valid standard metric unit '200 g'."),
            _ruleItem("LM-RULE-005 • Rule 6(1)(e)", "MRP inclusive of all taxes", "PASS", "Statutory tax clause clearly present."),
            _ruleItem("LM-RULE-006 • Rule 6(1)(n)", "Unit Sale Price Calculation", "PASS", "₹0.20 per g matches calculated rate."),
            _ruleItem("LM-RULE-010 • Rule 10", "Cross-Surface Consistency", "PASS", "No disparate declarations across package faces."),

            const SizedBox(height: 30),
            SizedBox(
              width: double.infinity,
              height: 50,
              child: OutlinedButton.icon(
                style: OutlinedButton.styleFrom(
                  foregroundColor: Colors.cyanAccent,
                  side: const BorderSide(color: Colors.cyanAccent),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                onPressed: () => Navigator.pushNamedAndRemoveUntil(context, '/', (route) => false),
                icon: const Icon(Icons.home),
                label: const Text("RETURN TO HOME", style: TextStyle(fontWeight: FontWeight.bold)),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _statBox(String label, String value, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 8),
        decoration: BoxDecoration(
          color: const Color(0xFF1E293B),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: Colors.white12),
        ),
        child: Column(
          children: [
            Text(value, style: TextStyle(color: color, fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 2),
            Text(label, style: const TextStyle(color: Colors.white60, fontSize: 9), textAlign: TextAlign.center),
          ],
        ),
      ),
    );
  }

  Widget _fieldItem(String name, String value, String meta, bool verified) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: Colors.white10),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.check_circle_outline, color: Colors.greenAccent, size: 18),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(name, style: const TextStyle(color: Colors.cyanAccent, fontSize: 11, fontWeight: FontWeight.w600)),
                const SizedBox(height: 2),
                Text(value, style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w500)),
                const SizedBox(height: 2),
                Text(meta, style: TextStyle(color: Colors.grey.shade400, fontSize: 10)),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.edit_outlined, size: 16, color: Colors.white54),
            tooltip: "Correct Extraction",
            onPressed: () {},
          ),
        ],
      ),
    );
  }

  Widget _ruleItem(String code, String title, String status, String note) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(code, style: const TextStyle(color: Colors.white70, fontSize: 10)),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: Colors.green.shade900.withOpacity(0.4),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(status, style: const TextStyle(color: Colors.greenAccent, fontSize: 10, fontWeight: FontWeight.bold)),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(title, style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
          const SizedBox(height: 2),
          Text(note, style: TextStyle(color: Colors.grey.shade400, fontSize: 11)),
        ],
      ),
    );
  }
}
