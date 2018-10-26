class SearchGuardException(Exception):
    pass


class CreateUserException(SearchGuardException):
    pass


class DeleteUserException(SearchGuardException):
    pass


class CreateRoleException(SearchGuardException):
    pass


class DeleteRoleException(SearchGuardException):
    pass


class ViewRoleException(SearchGuardException):
    pass


class ViewUserException(SearchGuardException):
    pass


class ModifyRoleException(SearchGuardException):
    pass


class ListUsersException(SearchGuardException):
    pass


class CheckUserExistsException(SearchGuardException):
    pass


class CheckRoleExistsException(SearchGuardException):
    pass
