
def get_selected_items(request):
    selected_items = request.POST.getlist('selected_items')

    return selected_items
