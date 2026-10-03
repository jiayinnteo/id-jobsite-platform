/// The four roles the platform serves.
enum UserRole {
  id,
  client,
  contractor,
  worker;

  String get label {
    switch (this) {
      case UserRole.id:
        return 'Interior Designer';
      case UserRole.client:
        return 'Client';
      case UserRole.contractor:
        return 'Contractor';
      case UserRole.worker:
        return 'Worker';
    }
  }
}
