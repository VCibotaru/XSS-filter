from flask import Blueprint


vuln_blueprint = Blueprint(
    'vuln', __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/static/vuln'
)

import vuln.views
