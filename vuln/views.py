from flask import redirect, render_template, request, url_for


from protector import protect
from vuln import vuln_blueprint as vuln


@vuln.route('/echo/')
@protect
def echo():
    if 'name' not in request.args:
        return redirect(url_for('vuln.echo', name='stranger'))

    return render_template(
        'vuln/echo.html',
        name=request.args['name']
    )


@vuln.route('/search/')
@protect
def search():
    search_topic = request.args.get('search', '')
    return render_template(
        'vuln/attribute.html',
        search=search_topic
    )


@vuln.route('/ctf-stat/')
@protect
def ctf_stat():
    if 'nick' not in request.args:
        return redirect(url_for('vuln.ctf_stat', nick='vovapi'))
    return render_template(
        'vuln/ctf-stat.html',
        nick=request.args['nick']
    )
