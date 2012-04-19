

def user_info(request):
    """
    get the Khan user from the KNet user object
    bring back the Khan information
    """
    khan_user_info = get_data_for_khan_api_call(request, '/api/v1/user')
    return {'khan_user_info': khan_user_info }