/// The roles the platform serves.
enum UserRole {
  idBoss,
  id,
  client,
  contractor,
  worker;

  String get label {
    switch (this) {
      case UserRole.idBoss:
        return 'ID Company Boss';
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
