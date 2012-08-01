#if not 'siteLanguage' in request.cookies:
#    T.force('pt-br')

if 'siteLanguage' in request.cookies and not (request.cookies['siteLanguage'] is None):
    T.force(request.cookies['siteLanguage'].value)
