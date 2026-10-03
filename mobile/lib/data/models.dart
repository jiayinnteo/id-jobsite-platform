/// Lightweight data models mirroring the backend schemas.

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
  });

  final String id;
  final String jobId;
  final String title;
  final String status;
  final String? description;
  final String? location;

  factory Defect.fromJson(Map<String, dynamic> j) => Defect(
        id: j['id'] as String,
        jobId: j['job_id'] as String,
        title: j['title'] as String,
        status: j['status'] as String,
        description: j['description'] as String?,
        location: j['location'] as String?,
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
