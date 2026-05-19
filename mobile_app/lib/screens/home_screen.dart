import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../models/service_request.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final TextEditingController _controller = TextEditingController();
  bool _isLoading = false;
  OrchestratorResponse? _response;

  Future<void> _submitRequest(String text) async {
    if (text.trim().isEmpty) return;

    setState(() {
      _isLoading = true;
      _response = null;
    });

    try {
      // Connect to the local FastAPI backend (Android emulator maps 10.0.2.2 to localhost)
      // Use 127.0.0.1 if running Flutter web/desktop.
      const String apiUrl = 'http://127.0.0.1:8000/api/orchestrate';

      final res = await http.post(
        Uri.parse(apiUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'user_input': text.trim(),
          'user_name': 'Ali Raza',
          'user_phone': '+92-333-1234567'
        }),
      );

      if (res.statusCode == 200) {
        setState(() {
          _response = OrchestratorResponse.fromJson(jsonDecode(res.body));
        });
      } else {
        _showError('Server returned error: ${res.statusCode}');
      }
    } catch (e) {
      _showError('Failed to connect to backend: $e\nEnsure FastAPI is running on port 8000.');
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  void _showError(String msg) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(msg), backgroundColor: Colors.red),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Pakistan Service Orchestrator', style: TextStyle(color: Colors.white)),
        backgroundColor: Theme.of(context).colorScheme.primary,
      ),
      body: Column(
        children: [
          Expanded(
            child: _isLoading
                ? const Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        CircularProgressIndicator(),
                        SizedBox(height: 16),
                        Text('🤖 Agent is thinking, discovering, and ranking...', 
                            style: TextStyle(color: Colors.grey)),
                      ],
                    ),
                  )
                : _response == null
                    ? const Center(
                        child: Text(
                          'Type a request to get started!\n(e.g., "Mujhe G-13 mein kal subah plumber chahiye")',
                          textAlign: TextAlign.center,
                          style: TextStyle(color: Colors.grey, fontSize: 16),
                        ),
                      )
                    : _buildResponseView(),
          ),
          Container(
            padding: const EdgeInsets.all(12.0),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.grey.withOpacity(0.2),
                  spreadRadius: 1,
                  blurRadius: 5,
                  offset: const Offset(0, -1),
                ),
              ],
            ),
            child: SafeArea(
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _controller,
                      decoration: InputDecoration(
                        hintText: 'Describe your service need...',
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(24.0),
                        ),
                        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                      ),
                      onSubmitted: _submitRequest,
                    ),
                  ),
                  const SizedBox(width: 8),
                  CircleAvatar(
                    backgroundColor: Theme.of(context).colorScheme.primary,
                    child: IconButton(
                      icon: const Icon(Icons.send, color: Colors.white),
                      onPressed: () => _submitRequest(_controller.text),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildResponseView() {
    if (_response!.status == 'error') {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Text(
            '⚠️ ${_response!.errorMessage ?? 'An error occurred'}',
            style: const TextStyle(color: Colors.red, fontSize: 16),
            textAlign: TextAlign.center,
          ),
        ),
      );
    }

    final data = _response!.data!;
    
    return ListView(
      padding: const EdgeInsets.all(16.0),
      children: [
        // ── STEP 1: Intent Understanding
        _buildSectionHeader('Step 1: Intent Understanding', Icons.psychology),
        Card(
          elevation: 0,
          color: Colors.blue.shade50,
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _infoRow('Service Type', '${data.intent?.serviceType} (${data.intent?.subService})'),
                _infoRow('Location', data.intent?.location ?? 'Not specified'),
                _infoRow('Preferred Time', data.intent?.preferredDateTime ?? 'Flexible'),
              ],
            ),
          ),
        ),
        const SizedBox(height: 24),

        // ── STEP 2: Discovery & Ranking
        _buildSectionHeader('Step 2: Provider Discovery & Ranking', Icons.search),
        Text(data.discoverySummary ?? 'Top matched providers:', 
            style: const TextStyle(fontStyle: FontStyle.italic)),
        const SizedBox(height: 8),
        if (data.rankedProviders != null)
          ...data.rankedProviders!.map((p) => _buildProviderCard(p)),
        const SizedBox(height: 24),

        // ── STEP 3: Booking Confirmation
        if (data.whatsappMessage != null) ...[
          _buildSectionHeader('Step 3: Booking Confirmation', Icons.check_circle),
          Container(
            padding: const EdgeInsets.all(16.0),
            decoration: BoxDecoration(
              color: const Color(0xFFE1FFC7), // WhatsApp Web Bubble Color
              borderRadius: BorderRadius.circular(12.0),
              boxShadow: const [BoxShadow(color: Colors.black12, blurRadius: 4, offset: Offset(1, 1))],
            ),
            child: Text(
              data.whatsappMessage!,
              style: const TextStyle(fontSize: 15, height: 1.4),
            ),
          ),
        ],
      ],
    );
  }

  Widget _buildSectionHeader(String title, IconData icon) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: Row(
        children: [
          Icon(icon, color: Theme.of(context).colorScheme.primary),
          const SizedBox(width: 8),
          Text(
            title,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Theme.of(context).colorScheme.primary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _infoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6.0),
      child: RichText(
        text: TextSpan(
          style: const TextStyle(color: Colors.black87, fontSize: 15),
          children: [
            TextSpan(text: '$label: ', style: const TextStyle(fontWeight: FontWeight.bold)),
            TextSpan(text: value),
          ],
        ),
      ),
    );
  }

  Widget _buildProviderCard(ProviderData provider) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12.0),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(child: Text(provider.name, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16))),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(color: Colors.green.shade100, borderRadius: BorderRadius.circular(12)),
                  child: Text('Score: ${provider.score.toStringAsFixed(1)}/10', 
                      style: TextStyle(color: Colors.green.shade800, fontWeight: FontWeight.bold, fontSize: 12)),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                const Icon(Icons.star, size: 16, color: Colors.amber),
                Text(' ${provider.rating}'),
                const SizedBox(width: 16),
                const Icon(Icons.location_on, size: 16, color: Colors.grey),
                Text(' ${provider.distanceKm != null ? "${provider.distanceKm} km" : provider.area}'),
              ],
            ),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(8.0),
              decoration: BoxDecoration(color: Colors.grey.shade100, borderRadius: BorderRadius.circular(8)),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(Icons.lightbulb_outline, size: 18, color: Colors.orange),
                  const SizedBox(width: 8),
                  Expanded(child: Text(provider.reasoning, style: const TextStyle(fontSize: 13, color: Colors.black87))),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
