class OrchestratorResponse {
  final String status;
  final String? errorMessage;
  final OrchestratorData? data;

  OrchestratorResponse({required this.status, this.errorMessage, this.data});

  factory OrchestratorResponse.fromJson(Map<String, dynamic> json) {
    return OrchestratorResponse(
      status: json['status'] ?? 'error',
      errorMessage: json['message'],
      data: json['data'] != null ? OrchestratorData.fromJson(json['data']) : null,
    );
  }
}

class OrchestratorData {
  final IntentData? intent;
  final List<ProviderData>? rankedProviders;
  final String? discoverySummary;
  final BookingData? booking;
  final String? whatsappMessage;

  OrchestratorData({
    this.intent,
    this.rankedProviders,
    this.discoverySummary,
    this.booking,
    this.whatsappMessage,
  });

  factory OrchestratorData.fromJson(Map<String, dynamic> json) {
    final discovery = json['discovery'] ?? {};
    final providersList = discovery['ranked_providers'] as List<dynamic>?;

    return OrchestratorData(
      intent: json['intent'] != null ? IntentData.fromJson(json['intent']) : null,
      rankedProviders: providersList?.map((p) => ProviderData.fromJson(p)).toList(),
      discoverySummary: discovery['summary'],
      booking: json['booking']?['booking'] != null 
          ? BookingData.fromJson(json['booking']['booking']) 
          : null,
      whatsappMessage: json['booking']?['whatsapp_message'],
    );
  }
}

class IntentData {
  final String? serviceType;
  final String? subService;
  final String? location;
  final String? preferredDateTime;

  IntentData({this.serviceType, this.subService, this.location, this.preferredDateTime});

  factory IntentData.fromJson(Map<String, dynamic> json) {
    return IntentData(
      serviceType: json['service_type'],
      subService: json['sub_service'],
      location: json['location'],
      preferredDateTime: json['preferred_date_time'],
    );
  }
}

class ProviderData {
  final String id;
  final String name;
  final String area;
  final double? distanceKm;
  final double rating;
  final double score;
  final String reasoning;

  ProviderData({
    required this.id,
    required this.name,
    required this.area,
    this.distanceKm,
    required this.rating,
    required this.score,
    required this.reasoning,
  });

  factory ProviderData.fromJson(Map<String, dynamic> json) {
    return ProviderData(
      id: json['id'] ?? '',
      name: json['name'] ?? 'Unknown Provider',
      area: json['location']?['area'] ?? 'Unknown Area',
      distanceKm: json['distance_km']?.toDouble(),
      rating: json['rating']?.toDouble() ?? 0.0,
      score: json['match_score']?.toDouble() ?? 0.0,
      reasoning: json['reasoning'] ?? 'No reasoning provided.',
    );
  }
}

class BookingData {
  final String bookingId;
  final String status;
  final String scheduledTime;

  BookingData({
    required this.bookingId,
    required this.status,
    required this.scheduledTime,
  });

  factory BookingData.fromJson(Map<String, dynamic> json) {
    return BookingData(
      bookingId: json['booking_id'] ?? '',
      status: json['status'] ?? 'PENDING',
      scheduledTime: json['scheduled_time'] ?? '',
    );
  }
}
