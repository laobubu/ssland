

def ssland_processor(request):
    import config
    
    context = {'site_name': config.SITE_NAME}

    return context
