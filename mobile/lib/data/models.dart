// Lightweight data models mirroring the backend schemas.

class Job {
  Job({
    required this.id,
    required this.name,
    required this.address,
    required this.status,
    this.clientId,
  });

  final String id;
  final String name;
  final String address;
  final String status;
  final String? clientId;

  factory Job.fromJson(Map<String, dynamic> j) => Job(
        id: j['id'] as String,
        name: j['name'] as String,
        address: j['address'] as String,
        status: j['status'] as String,
        clientId: j['client_id'] as String?,
      );
}

class Defect {
  Defect({
    required this.id,
    required this.jobId,
    required this.title,
    required this.status,
    this.description,
    this.location,
    this.rectificationId,
  });

  final String id;
  final String jobId;
  final String title;
  final String status;
  final String? description;
  final String? location;
  final String? rectificationId;

  factory Defect.fromJson(Map<String, dynamic> j) => Defect(
        id: j['id'] as String,
        jobId: j['job_id'] as String,
        title: j['title'] as String,
        status: j['status'] as String,
        description: j['description'] as String?,
        location: j['location'] as String?,
        rectificationId: j['rectification_id'] as String?,
      );
}

class JobReview {
  JobReview({required this.rating, this.comment});
  final int rating;
  final String? comment;

  factory JobReview.fromJson(Map<String, dynamic> j) => JobReview(
        rating: j['rating'] as int,
        comment: j['comment'] as String?,
      );
}

class Document {
  Document({
    required this.id,
    required this.type,
    required this.title,
    required this.currentVersionNo,
  });

  final String id;
  final String type;
  final String title;
  final int currentVersionNo;

  factory Document.fromJson(Map<String, dynamic> j) => Document(
        id: j['id'] as String,
        type: j['type'] as String,
        title: j['title'] as String,
        currentVersionNo: (j['current_version_no'] as num?)?.toInt() ?? 1,
      );
}

class DefectHistoryEntry {
  DefectHistoryEntry({
    required this.toStatus,
    this.fromStatus,
    this.reason,
    this.createdAt,
  });

  final String toStatus;
  final String? fromStatus;
  final String? reason;
  final String? createdAt;

  factory DefectHistoryEntry.fromJson(Map<String, dynamic> j) =>
      DefectHistoryEntry(
        toStatus: j['to_status'] as String,
        fromStatus: j['from_status'] as String?,
        reason: j['reason'] as String?,
        createdAt: j['created_at'] as String?,
      );
}

class Photo {
  Photo({required this.id, this.caption, this.downloadUrl, this.defectId});

  final String id;
  final String? caption;
  final String? downloadUrl;
  final String? defectId;

  factory Photo.fromJson(Map<String, dynamic> j) => Photo(
        id: j['id'] as String,
        caption: j['caption'] as String?,
        downloadUrl: j['download_url'] as String?,
        defectId: j['defect_id'] as String?,
      );
}

class SiteVisit {
  SiteVisit({
    required this.id,
    required this.scheduledDate,
    required this.status,
    this.scheduledTime,
  });

  final String id;
  final String scheduledDate;
  final String status;
  final String? scheduledTime;

  factory SiteVisit.fromJson(Map<String, dynamic> j) => SiteVisit(
        id: j['id'] as String,
        scheduledDate: j['scheduled_date'] as String,
        status: j['status'] as String,
        scheduledTime: j['scheduled_time'] as String?,
      );
}

class MaterialProduct {
  MaterialProduct({
    required this.id,
    required this.category,
    required this.name,
    this.productCode,
    this.colour,
    this.colourHex,
    this.finish,
    this.sourceUrl,
  });

  final String id;
  final String category;
  final String name;
  final String? productCode;
  final String? colour;
  final String? colourHex;
  final String? finish;
  final String? sourceUrl;

  factory MaterialProduct.fromJson(Map<String, dynamic> j) => MaterialProduct(
        id: j['id'] as String,
        category: j['category'] as String,
        name: j['name'] as String,
        productCode: j['product_code'] as String?,
        colour: j['colour'] as String?,
        colourHex: j['colour_hex'] as String?,
        finish: j['finish'] as String?,
        sourceUrl: j['source_url'] as String?,
      );
}

class MaterialSelection {
  MaterialSelection({
    required this.id,
    required this.category,
    required this.status,
    this.area,
    this.modelSurface,
    this.colour,
    this.colourHex,
    this.note,
  });

  final String id;
  final String category;
  final String status;
  final String? area;
  final String? modelSurface;
  final String? colour;
  final String? colourHex;
  final String? note;

  factory MaterialSelection.fromJson(Map<String, dynamic> j) =>
      MaterialSelection(
        id: j['id'] as String,
        category: j['category'] as String,
        status: j['status'] as String,
        area: j['area'] as String?,
        modelSurface: j['model_surface'] as String?,
        colour: j['colour'] as String?,
        colourHex: j['colour_hex'] as String?,
        note: j['note'] as String?,
      );
}
